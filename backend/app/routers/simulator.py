from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app import models, schemas, auth
from app.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/simulator", tags=["Data Simulator"])


class SimulatorReading(BaseModel):
    """Single sensor reading for simulation"""
    device_id: str
    timestamp: Optional[datetime] = None
    temperature: Optional[float] = None
    gas_index: Optional[float] = None
    vibration_x: Optional[float] = None
    vibration_y: Optional[float] = None
    vibration_z: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    power_consumption: Optional[float] = None


class SimulatorBatch(BaseModel):
    """Batch of readings for multiple devices"""
    readings: List[SimulatorReading]


@router.post("/ingest-batch", status_code=status.HTTP_201_CREATED)
async def simulate_batch_data(
    batch: SimulatorBatch,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Simulate batch sensor data ingestion.
    
    This endpoint allows manual data entry for testing when ESP32 devices 
    are not yet deployed. Accepts JSON with multiple device readings.
    
    Only accessible to authenticated users with admin or factory_owner roles.
    """
    # Check permissions
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.FACTORY_OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to simulate data"
        )
    
    ingested_count = 0
    errors = []
    
    for reading in batch.readings:
        try:
            # Find device
            device = db.query(models.Device).filter(
                models.Device.device_id == reading.device_id
            ).first()
            
            if not device:
                errors.append({
                    "device_id": reading.device_id,
                    "error": "Device not found"
                })
                continue
            
            # Check if user has access to this device's factory
            if current_user.role != models.UserRole.ADMIN:
                if device.factory_id != current_user.factory_id:
                    errors.append({
                        "device_id": reading.device_id,
                        "error": "Not authorized for this device"
                    })
                    continue
            
            # Use provided timestamp or current time
            timestamp = reading.timestamp if reading.timestamp else datetime.utcnow()
            
            # Create sensor reading
            db_reading = models.SensorReading(
                device_id=device.id,
                timestamp=timestamp,
                temperature=reading.temperature,
                gas_index=reading.gas_index,
                vibration_x=reading.vibration_x,
                vibration_y=reading.vibration_y,
                vibration_z=reading.vibration_z,
                humidity=reading.humidity,
                pressure=reading.pressure,
                power_consumption=reading.power_consumption
            )
            
            db.add(db_reading)
            
            # Update device last_seen
            device.last_seen = timestamp
            
            ingested_count += 1
            
        except Exception as e:
            errors.append({
                "device_id": reading.device_id,
                "error": str(e)
            })
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "status": "success",
        "ingested_count": ingested_count,
        "total_readings": len(batch.readings),
        "errors": errors if errors else None
    }


@router.post("/generate-sample", status_code=status.HTTP_201_CREATED)
async def generate_sample_data(
    device_id: str,
    count: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Generate sample sensor data for testing.
    Creates realistic-looking data points for a specific device.
    """
    import random
    from datetime import timedelta
    
    # Check permissions
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.FACTORY_OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to generate data"
        )
    
    # Find device
    device = db.query(models.Device).filter(
        models.Device.device_id == device_id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check access
    if current_user.role != models.UserRole.ADMIN:
        if device.factory_id != current_user.factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this device"
            )
    
    # Generate sample data
    now = datetime.utcnow()
    base_temp = 850 if "furnace" in device.device_name.lower() else 45
    
    for i in range(count):
        timestamp = now - timedelta(minutes=i * 5)
        
        reading = models.SensorReading(
            device_id=device.id,
            timestamp=timestamp,
            temperature=base_temp + random.uniform(-20, 20),
            gas_index=random.uniform(100, 500),
            vibration_x=random.uniform(0.5, 3.5),
            vibration_y=random.uniform(0.5, 3.5),
            vibration_z=random.uniform(0.5, 3.5),
            humidity=random.uniform(30, 70),
            pressure=random.uniform(990, 1020),
            power_consumption=random.uniform(15, 45)
        )
        db.add(reading)
    
    device.last_seen = now
    db.commit()
    
    return {
        "status": "success",
        "device_id": device_id,
        "generated_count": count,
        "message": f"Generated {count} sample readings"
    }
