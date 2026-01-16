from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/register", response_model=schemas.Device)
async def register_device(
    device: schemas.DeviceRegister,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Register a new ESP32 device.
    Only admin or factory_owner can register devices.
    """
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.FACTORY_OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to register devices"
        )
    
    # Check if device already exists
    existing_device = db.query(models.Device).filter(
        models.Device.device_id == device.device_id
    ).first()
    
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    
    # Create new device
    db_device = models.Device(
        device_id=device.device_id,
        device_name=device.device_name,
        device_type=device.device_type,
        factory_id=device.factory_id,
        machine_name=device.machine_name,
        location=device.location,
        is_active=True
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return db_device


@router.get("", response_model=List[schemas.Device])
async def get_devices(
    factory_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all devices, optionally filtered by factory.
    Users can only see devices from their own factory unless they're admin.
    """
    query = db.query(models.Device)
    
    # Filter by factory based on user role
    if current_user.role != models.UserRole.ADMIN:
        if current_user.factory_id:
            query = query.filter(models.Device.factory_id == current_user.factory_id)
    elif factory_id:
        query = query.filter(models.Device.factory_id == factory_id)
    
    devices = query.all()
    return devices


@router.get("/{device_id}/status", response_model=schemas.DeviceStatus)
async def get_device_status(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get detailed status of a specific device including uptime percentage.
    """
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check access permissions
    if current_user.role != models.UserRole.ADMIN:
        if device.factory_id != current_user.factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this device"
            )
    
    # Calculate uptime percentage (last 24 hours)
    # A device is "up" if it sent data in the last 5 minutes
    uptime_percentage = None
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    
    # Count 5-minute intervals with data in last 24h
    intervals_with_data = db.query(
        func.count(func.distinct(func.date_trunc('minute', models.SensorReading.timestamp) / 5))
    ).filter(
        models.SensorReading.device_id == device_id,
        models.SensorReading.timestamp >= last_24h
    ).scalar()
    
    total_intervals = 24 * 12  # 288 five-minute intervals in 24 hours
    if intervals_with_data:
        uptime_percentage = (intervals_with_data / total_intervals) * 100
    
    return schemas.DeviceStatus(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        is_active=device.is_active,
        last_seen=device.last_seen,
        uptime_percentage=uptime_percentage
    )
