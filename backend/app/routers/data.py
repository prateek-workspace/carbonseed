from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(tags=["Data Ingestion"])


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_sensor_data(
    data: schemas.SensorReadingCreate,
    db: Session = Depends(get_db)
):
    """
    Ingest sensor data from ESP32 devices.
    This endpoint should be called by edge devices with sensor readings.
    
    In production, consider:
    - API key authentication for devices
    - Batch ingestion support
    - Message queue (e.g., RabbitMQ) for high-throughput scenarios
    """
    # Find device by external device_id
    device = db.query(models.Device).filter(
        models.Device.device_id == data.device_id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {data.device_id} not registered"
        )
    
    # Use provided timestamp or current time
    timestamp = data.timestamp if data.timestamp else datetime.utcnow()
    
    # Create sensor reading
    db_reading = models.SensorReading(
        device_id=device.id,
        timestamp=timestamp,
        temperature=data.temperature,
        gas_index=data.gas_index,
        vibration_x=data.vibration_x,
        vibration_y=data.vibration_y,
        vibration_z=data.vibration_z,
        humidity=data.humidity,
        pressure=data.pressure,
        power_consumption=data.power_consumption
    )
    
    db.add(db_reading)
    
    # Update device last_seen
    device.last_seen = timestamp
    
    db.commit()
    
    # TODO: Trigger anomaly detection analysis
    # This is where we would call the analytics service or queue a job
    # to check if this reading triggers any alerts
    # Example: await check_anomalies(db_reading, device)
    
    return {"status": "success", "message": "Data ingested successfully"}


@router.get("/data/latest", response_model=schemas.LatestData)
async def get_latest_data(
    factory_id: Optional[int] = None,
    device_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get latest sensor readings aggregated across devices.
    Used for dashboard overview.
    """
    # Build query based on permissions
    query = db.query(models.SensorReading).join(models.Device)
    
    if current_user.role != models.UserRole.ADMIN:
        query = query.filter(models.Device.factory_id == current_user.factory_id)
    elif factory_id:
        query = query.filter(models.Device.factory_id == factory_id)
    
    if device_id:
        query = query.filter(models.Device.id == device_id)
    
    # Get most recent reading
    latest_reading = query.order_by(desc(models.SensorReading.timestamp)).first()
    
    if not latest_reading:
        return schemas.LatestData(
            temperature=None,
            gas_index=None,
            vibration_health="unknown",
            device_uptime=None,
            last_update=None
        )
    
    # Calculate vibration health
    vibration_health = "good"
    if latest_reading.vibration_x or latest_reading.vibration_y or latest_reading.vibration_z:
        # Simple threshold-based health check
        max_vibration = max(
            latest_reading.vibration_x or 0,
            latest_reading.vibration_y or 0,
            latest_reading.vibration_z or 0
        )
        if max_vibration > 10:
            vibration_health = "critical"
        elif max_vibration > 5:
            vibration_health = "moderate"
    
    # Calculate uptime
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    
    # Count devices that have sent data in last 5 minutes
    active_devices = db.query(func.count(func.distinct(models.Device.id))).filter(
        models.Device.last_seen >= now - timedelta(minutes=5)
    )
    
    if current_user.role != models.UserRole.ADMIN:
        active_devices = active_devices.filter(models.Device.factory_id == current_user.factory_id)
    elif factory_id:
        active_devices = active_devices.filter(models.Device.factory_id == factory_id)
    
    active_count = active_devices.scalar()
    
    # Total devices
    total_devices = db.query(func.count(models.Device.id))
    if current_user.role != models.UserRole.ADMIN:
        total_devices = total_devices.filter(models.Device.factory_id == current_user.factory_id)
    elif factory_id:
        total_devices = total_devices.filter(models.Device.factory_id == factory_id)
    
    total_count = total_devices.scalar()
    
    device_uptime = (active_count / total_count * 100) if total_count > 0 else 0
    
    return schemas.LatestData(
        temperature=latest_reading.temperature,
        gas_index=latest_reading.gas_index,
        vibration_health=vibration_health,
        device_uptime=device_uptime,
        last_update=latest_reading.timestamp
    )


@router.get("/data/timeseries", response_model=List[schemas.SensorReading])
async def get_timeseries_data(
    device_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(default=1000, le=10000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get time series sensor data for charting.
    Returns data points for a specific device within a time range.
    """
    # Verify device access
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if current_user.role != models.UserRole.ADMIN:
        if device.factory_id != current_user.factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this device's data"
            )
    
    # Default to last 24 hours if no time range specified
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(hours=24)
    
    # Query sensor readings
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.device_id == device_id,
        models.SensorReading.timestamp >= start_time,
        models.SensorReading.timestamp <= end_time
    ).order_by(models.SensorReading.timestamp).limit(limit).all()
    
    return readings
