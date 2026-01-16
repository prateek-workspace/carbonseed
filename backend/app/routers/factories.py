from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/factories", tags=["Factories"])


@router.post("", response_model=schemas.Factory)
async def create_factory(
    factory: schemas.FactoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new factory (Admin only).
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create factories"
        )
    
    db_factory = models.Factory(
        name=factory.name,
        location=factory.location,
        industry=factory.industry,
        contact_email=factory.contact_email,
        contact_phone=factory.contact_phone
    )
    
    db.add(db_factory)
    db.commit()
    db.refresh(db_factory)
    
    return db_factory


@router.get("", response_model=List[schemas.FactoryWithStats])
async def list_factories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    List all factories with stats.
    - Admins see all factories
    - Factory owners/operators see only their factory
    """
    query = db.query(models.Factory)
    
    if current_user.role != models.UserRole.ADMIN:
        if current_user.factory_id:
            query = query.filter(models.Factory.id == current_user.factory_id)
        else:
            return []
    
    factories = query.all()
    
    # Add stats to each factory
    result = []
    for factory in factories:
        device_count = db.query(func.count(models.Device.id)).filter(
            models.Device.factory_id == factory.id
        ).scalar()
        
        user_count = db.query(func.count(models.User.id)).filter(
            models.User.factory_id == factory.id
        ).scalar()
        
        active_alerts = db.query(func.count(models.Alert.id)).filter(
            models.Alert.factory_id == factory.id,
            models.Alert.status == models.AlertStatus.ACTIVE
        ).scalar()
        
        result.append(schemas.FactoryWithStats(
            id=factory.id,
            name=factory.name,
            location=factory.location,
            industry=factory.industry,
            contact_email=factory.contact_email,
            contact_phone=factory.contact_phone,
            created_at=factory.created_at,
            device_count=device_count or 0,
            user_count=user_count or 0,
            active_alerts=active_alerts or 0
        ))
    
    return result


@router.get("/{factory_id}", response_model=schemas.FactoryWithStats)
async def get_factory(
    factory_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific factory by ID.
    """
    # Check access
    if current_user.role != models.UserRole.ADMIN:
        if current_user.factory_id != factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this factory"
            )
    
    factory = db.query(models.Factory).filter(models.Factory.id == factory_id).first()
    
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factory not found"
        )
    
    # Get stats
    device_count = db.query(func.count(models.Device.id)).filter(
        models.Device.factory_id == factory.id
    ).scalar()
    
    user_count = db.query(func.count(models.User.id)).filter(
        models.User.factory_id == factory.id
    ).scalar()
    
    active_alerts = db.query(func.count(models.Alert.id)).filter(
        models.Alert.factory_id == factory.id,
        models.Alert.status == models.AlertStatus.ACTIVE
    ).scalar()
    
    return schemas.FactoryWithStats(
        id=factory.id,
        name=factory.name,
        location=factory.location,
        industry=factory.industry,
        contact_email=factory.contact_email,
        contact_phone=factory.contact_phone,
        created_at=factory.created_at,
        device_count=device_count or 0,
        user_count=user_count or 0,
        active_alerts=active_alerts or 0
    )


@router.put("/{factory_id}", response_model=schemas.Factory)
async def update_factory(
    factory_id: int,
    factory_update: schemas.FactoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update a factory (Admin or Factory Owner only).
    """
    # Check access
    if current_user.role == models.UserRole.ADMIN:
        pass  # Admin can update any factory
    elif current_user.role == models.UserRole.FACTORY_OWNER:
        if current_user.factory_id != factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this factory"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and factory owners can update factories"
        )
    
    factory = db.query(models.Factory).filter(models.Factory.id == factory_id).first()
    
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factory not found"
        )
    
    # Update fields
    update_data = factory_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(factory, field, value)
    
    db.commit()
    db.refresh(factory)
    
    return factory


@router.delete("/{factory_id}")
async def delete_factory(
    factory_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Delete a factory (Admin only).
    Warning: This will also delete all associated devices, users, and data.
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete factories"
        )
    
    factory = db.query(models.Factory).filter(models.Factory.id == factory_id).first()
    
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factory not found"
        )
    
    # Delete in order due to foreign key constraints
    # 1. Delete sensor readings for all devices
    device_ids = [d.id for d in factory.devices]
    if device_ids:
        db.query(models.SensorReading).filter(
            models.SensorReading.device_id.in_(device_ids)
        ).delete(synchronize_session=False)
        
        # Delete signals
        db.query(models.Signal).filter(
            models.Signal.factory_id == factory_id
        ).delete(synchronize_session=False)
        
        # Delete alerts
        db.query(models.Alert).filter(
            models.Alert.factory_id == factory_id
        ).delete(synchronize_session=False)
    
    # 2. Delete devices
    db.query(models.Device).filter(
        models.Device.factory_id == factory_id
    ).delete(synchronize_session=False)
    
    # 3. Delete reports
    db.query(models.Report).filter(
        models.Report.factory_id == factory_id
    ).delete(synchronize_session=False)
    
    # 4. Update users (remove factory association)
    db.query(models.User).filter(
        models.User.factory_id == factory_id
    ).update({"factory_id": None}, synchronize_session=False)
    
    # 5. Delete factory
    db.delete(factory)
    db.commit()
    
    return {"status": "deleted", "factory_id": factory_id}


@router.get("/{factory_id}/dashboard", response_model=schemas.DashboardStats)
async def get_factory_dashboard(
    factory_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get dashboard statistics for a factory.
    """
    # Check access
    if current_user.role != models.UserRole.ADMIN:
        if current_user.factory_id != factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this factory"
            )
    
    factory = db.query(models.Factory).filter(models.Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factory not found"
        )
    
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    
    # Device stats
    total_devices = db.query(func.count(models.Device.id)).filter(
        models.Device.factory_id == factory_id
    ).scalar() or 0
    
    active_devices = db.query(func.count(models.Device.id)).filter(
        models.Device.factory_id == factory_id,
        models.Device.is_active == True,
        models.Device.last_seen >= now - timedelta(minutes=5)
    ).scalar() or 0
    
    # Alert stats
    total_alerts = db.query(func.count(models.Alert.id)).filter(
        models.Alert.factory_id == factory_id
    ).scalar() or 0
    
    active_alerts = db.query(func.count(models.Alert.id)).filter(
        models.Alert.factory_id == factory_id,
        models.Alert.status == models.AlertStatus.ACTIVE
    ).scalar() or 0
    
    # Signal stats
    total_signals = db.query(func.count(models.Signal.id)).filter(
        models.Signal.factory_id == factory_id
    ).scalar() or 0
    
    new_signals = db.query(func.count(models.Signal.id)).filter(
        models.Signal.factory_id == factory_id,
        models.Signal.status == models.SignalStatus.NEW
    ).scalar() or 0
    
    # Get device IDs for this factory
    device_ids = [d.id for d in db.query(models.Device).filter(
        models.Device.factory_id == factory_id
    ).all()]
    
    # Sensor metrics (last 24h)
    avg_temp = None
    avg_gas = None
    vibration_score = None
    energy_24h = None
    
    if device_ids:
        metrics = db.query(
            func.avg(models.SensorReading.temperature).label('avg_temp'),
            func.avg(models.SensorReading.gas_index).label('avg_gas'),
            func.avg(models.SensorReading.vibration_x).label('avg_vib_x'),
            func.avg(models.SensorReading.vibration_y).label('avg_vib_y'),
            func.avg(models.SensorReading.vibration_z).label('avg_vib_z'),
            func.sum(models.SensorReading.power_consumption).label('total_power')
        ).filter(
            models.SensorReading.device_id.in_(device_ids),
            models.SensorReading.timestamp >= last_24h
        ).first()
        
        if metrics:
            avg_temp = round(metrics.avg_temp, 1) if metrics.avg_temp else None
            avg_gas = round(metrics.avg_gas, 1) if metrics.avg_gas else None
            energy_24h = round(metrics.total_power, 2) if metrics.total_power else None
            
            # Calculate vibration health score
            if metrics.avg_vib_x or metrics.avg_vib_y or metrics.avg_vib_z:
                avg_vibration = (
                    (metrics.avg_vib_x or 0) +
                    (metrics.avg_vib_y or 0) +
                    (metrics.avg_vib_z or 0)
                ) / 3
                
                if avg_vibration > 10:
                    vibration_score = max(0, 30 - (avg_vibration - 10) * 3)
                elif avg_vibration > 5:
                    vibration_score = 70 - (avg_vibration - 5) * 8
                else:
                    vibration_score = 100 - avg_vibration * 6
                vibration_score = round(vibration_score, 1)
    
    return schemas.DashboardStats(
        total_devices=total_devices,
        active_devices=active_devices,
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        total_signals=total_signals,
        new_signals=new_signals,
        avg_temperature=avg_temp,
        avg_gas_index=avg_gas,
        vibration_health_score=vibration_score,
        energy_consumption_24h=energy_24h
    )
