from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from datetime import datetime, timedelta
from app import models, schemas, auth
from app.database import get_db
import json

router = APIRouter(tags=["Insights & Analytics"])


@router.get("/insights", response_model=schemas.Insight)
async def get_insights(
    factory_id: int = None,
    period: str = "24h",  # 24h, 7d, 30d
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get analytics insights for a factory.
    
    This endpoint performs simple physics-informed analytics:
    - Rolling averages
    - Baseline vs current comparison
    - Threshold-based anomaly detection
    - Health scores
    
    Future: This is where ML models would be integrated via API calls
    """
    # Determine time range
    now = datetime.utcnow()
    if period == "24h":
        start_time = now - timedelta(hours=24)
    elif period == "7d":
        start_time = now - timedelta(days=7)
    elif period == "30d":
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(hours=24)
    
    # Determine factory based on user role
    if current_user.role != models.UserRole.ADMIN:
        factory_id = current_user.factory_id
    
    if not factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Factory ID required"
        )
    
    # Get all devices for this factory
    devices = db.query(models.Device).filter(
        models.Device.factory_id == factory_id
    ).all()
    
    device_ids = [d.id for d in devices]
    
    if not device_ids:
        return schemas.Insight(
            period=period,
            factory_id=factory_id,
            metrics=schemas.InsightMetrics(
                avg_temperature=None,
                max_temperature=None,
                avg_gas_index=None,
                vibration_health_score=None,
                device_uptime_percentage=None,
                anomalies_detected=0,
                energy_consumption=None
            ),
            generated_at=now
        )
    
    # Query sensor readings for this period
    readings = db.query(
        func.avg(models.SensorReading.temperature).label('avg_temp'),
        func.max(models.SensorReading.temperature).label('max_temp'),
        func.avg(models.SensorReading.gas_index).label('avg_gas'),
        func.avg(models.SensorReading.vibration_x).label('avg_vib_x'),
        func.avg(models.SensorReading.vibration_y).label('avg_vib_y'),
        func.avg(models.SensorReading.vibration_z).label('avg_vib_z'),
        func.sum(models.SensorReading.power_consumption).label('total_power')
    ).filter(
        models.SensorReading.device_id.in_(device_ids),
        models.SensorReading.timestamp >= start_time
    ).first()
    
    # Calculate vibration health score (0-100)
    vibration_health_score = 100.0
    if readings.avg_vib_x or readings.avg_vib_y or readings.avg_vib_z:
        avg_vibration = (
            (readings.avg_vib_x or 0) +
            (readings.avg_vib_y or 0) +
            (readings.avg_vib_z or 0)
        ) / 3
        
        # Simple scoring: > 10 is critical (score 0-30), 5-10 is moderate (30-70), <5 is good (70-100)
        if avg_vibration > 10:
            vibration_health_score = max(0, 30 - (avg_vibration - 10) * 3)
        elif avg_vibration > 5:
            vibration_health_score = 70 - (avg_vibration - 5) * 8
        else:
            vibration_health_score = 100 - avg_vibration * 6
    
    # Calculate device uptime
    active_devices = db.query(func.count(func.distinct(models.Device.id))).filter(
        models.Device.factory_id == factory_id,
        models.Device.last_seen >= now - timedelta(minutes=5)
    ).scalar()
    
    total_devices = len(device_ids)
    device_uptime_percentage = (active_devices / total_devices * 100) if total_devices > 0 else 0
    
    # Count anomalies (active alerts in this period)
    anomalies_detected = db.query(func.count(models.Alert.id)).filter(
        models.Alert.factory_id == factory_id,
        models.Alert.triggered_at >= start_time,
        models.Alert.severity.in_([models.AlertSeverity.WARNING, models.AlertSeverity.CRITICAL])
    ).scalar()
    
    return schemas.Insight(
        period=period,
        factory_id=factory_id,
        metrics=schemas.InsightMetrics(
            avg_temperature=readings.avg_temp,
            max_temperature=readings.max_temp,
            avg_gas_index=readings.avg_gas,
            vibration_health_score=vibration_health_score,
            device_uptime_percentage=device_uptime_percentage,
            anomalies_detected=anomalies_detected or 0,
            energy_consumption=readings.total_power
        ),
        generated_at=now
    )


@router.get("/alerts", response_model=List[schemas.Alert])
async def get_alerts(
    factory_id: int = None,
    status: str = None,  # active, acknowledged, resolved
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get alerts for a factory.
    Alerts are generated by the analytics engine when anomalies are detected.
    """
    query = db.query(models.Alert)
    
    # Filter by factory based on user role
    if current_user.role != models.UserRole.ADMIN:
        query = query.filter(models.Alert.factory_id == current_user.factory_id)
    elif factory_id:
        query = query.filter(models.Alert.factory_id == factory_id)
    
    # Filter by status
    if status:
        if status == "active":
            query = query.filter(models.Alert.status == models.AlertStatus.ACTIVE)
        elif status == "acknowledged":
            query = query.filter(models.Alert.status == models.AlertStatus.ACKNOWLEDGED)
        elif status == "resolved":
            query = query.filter(models.Alert.status == models.AlertStatus.RESOLVED)
    
    alerts = query.order_by(models.Alert.triggered_at.desc()).limit(100).all()
    return alerts


@router.post("/alerts/{alert_id}/acknowledge", response_model=schemas.Alert)
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Acknowledge an alert.
    """
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Check permissions
    if current_user.role != models.UserRole.ADMIN:
        if alert.factory_id != current_user.factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to acknowledge this alert"
            )
    
    alert.status = models.AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = current_user.id
    
    db.commit()
    db.refresh(alert)
    
    return alert
