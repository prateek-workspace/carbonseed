from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app import models, schemas, auth
from app.database import get_db
from app.services.gemini import gemini_service
import json

router = APIRouter(prefix="/signals", tags=["Signals & Analytics"])


# Thresholds for anomaly detection
THRESHOLDS = {
    "temperature_high": 900,  # Celsius for furnaces
    "temperature_low": 20,
    "gas_index_high": 400,
    "vibration_critical": 8.0,
    "vibration_warning": 5.0,
    "humidity_high": 80,
    "humidity_low": 20,
    "power_consumption_high": 50,
}


async def analyze_reading_with_ai(reading: models.SensorReading, device: models.Device) -> Optional[dict]:
    """Use Gemini API to analyze sensor reading for anomalies"""
    sensor_data = {
        "temperature": reading.temperature,
        "gas_index": reading.gas_index,
        "vibration_x": reading.vibration_x,
        "vibration_y": reading.vibration_y,
        "vibration_z": reading.vibration_z,
        "humidity": reading.humidity,
        "pressure": reading.pressure,
        "power_consumption": reading.power_consumption,
        "device_name": device.device_name,
        "machine_name": device.machine_name,
    }
    
    return await gemini_service.analyze_anomaly(sensor_data)


def check_thresholds(reading: models.SensorReading, device: models.Device) -> List[dict]:
    """Rule-based threshold checking for anomalies"""
    anomalies = []
    
    # Temperature check
    if reading.temperature:
        if reading.temperature > THRESHOLDS["temperature_high"]:
            anomalies.append({
                "type": models.SignalType.THRESHOLD_BREACH,
                "title": "High Temperature Alert",
                "description": f"Temperature {reading.temperature}°C exceeds threshold of {THRESHOLDS['temperature_high']}°C",
                "severity": models.AlertSeverity.CRITICAL if reading.temperature > THRESHOLDS["temperature_high"] * 1.1 else models.AlertSeverity.WARNING,
                "recommendation": "Check cooling systems and reduce furnace load if safe to do so.",
            })
    
    # Gas index check
    if reading.gas_index:
        if reading.gas_index > THRESHOLDS["gas_index_high"]:
            anomalies.append({
                "type": models.SignalType.ANOMALY,
                "title": "Elevated Gas Index",
                "description": f"Gas index {reading.gas_index} exceeds threshold of {THRESHOLDS['gas_index_high']}",
                "severity": models.AlertSeverity.WARNING,
                "recommendation": "Check ventilation systems and air quality. May indicate process issues.",
            })
    
    # Vibration check
    max_vibration = max(
        reading.vibration_x or 0,
        reading.vibration_y or 0,
        reading.vibration_z or 0
    )
    if max_vibration > THRESHOLDS["vibration_critical"]:
        anomalies.append({
            "type": models.SignalType.MAINTENANCE,
            "title": "Critical Vibration Detected",
            "description": f"Vibration level {max_vibration} exceeds critical threshold of {THRESHOLDS['vibration_critical']}",
            "severity": models.AlertSeverity.CRITICAL,
            "recommendation": "Immediate maintenance required. Check for bearing wear, misalignment, or loose components.",
        })
    elif max_vibration > THRESHOLDS["vibration_warning"]:
        anomalies.append({
            "type": models.SignalType.PREDICTIVE,
            "title": "Elevated Vibration Warning",
            "description": f"Vibration level {max_vibration} exceeds warning threshold of {THRESHOLDS['vibration_warning']}",
            "severity": models.AlertSeverity.WARNING,
            "recommendation": "Schedule preventive maintenance within 48 hours.",
        })
    
    # Power consumption check
    if reading.power_consumption:
        if reading.power_consumption > THRESHOLDS["power_consumption_high"]:
            anomalies.append({
                "type": models.SignalType.EFFICIENCY,
                "title": "High Power Consumption",
                "description": f"Power consumption {reading.power_consumption} kWh exceeds threshold of {THRESHOLDS['power_consumption_high']} kWh",
                "severity": models.AlertSeverity.INFO,
                "recommendation": "Review process efficiency. Consider load balancing or equipment optimization.",
            })
    
    return anomalies


async def process_signals_for_reading(
    db: Session,
    reading: models.SensorReading,
    device: models.Device,
    use_ai: bool = True
) -> List[models.Signal]:
    """Process a sensor reading and generate signals"""
    signals_created = []
    
    # 1. Rule-based threshold checking
    threshold_anomalies = check_thresholds(reading, device)
    
    for anomaly in threshold_anomalies:
        signal = models.Signal(
            device_id=device.id,
            factory_id=device.factory_id,
            signal_type=anomaly["type"],
            status=models.SignalStatus.COMPLETED,
            title=anomaly["title"],
            description=anomaly["description"],
            severity=anomaly["severity"],
            recommendation=anomaly["recommendation"],
            input_data={
                "temperature": reading.temperature,
                "gas_index": reading.gas_index,
                "vibration_x": reading.vibration_x,
                "vibration_y": reading.vibration_y,
                "vibration_z": reading.vibration_z,
                "humidity": reading.humidity,
                "power_consumption": reading.power_consumption,
            },
            confidence_score=95.0,  # High confidence for rule-based
            detected_at=reading.timestamp,
            processed_at=datetime.utcnow(),
        )
        db.add(signal)
        signals_created.append(signal)
    
    # 2. AI-based analysis (if enabled and no critical issues found)
    if use_ai and len(threshold_anomalies) == 0:
        try:
            ai_result = await analyze_reading_with_ai(reading, device)
            if ai_result and ai_result.get("anomaly_detected"):
                signal = models.Signal(
                    device_id=device.id,
                    factory_id=device.factory_id,
                    signal_type=models.SignalType.ANOMALY,
                    status=models.SignalStatus.COMPLETED,
                    title=f"AI Detected: {ai_result.get('issue', 'Anomaly')}",
                    description=ai_result.get("issue", "Anomaly detected by AI analysis"),
                    severity=models.AlertSeverity(ai_result.get("severity", "info")),
                    recommendation=ai_result.get("recommendation", "Review sensor data"),
                    input_data={
                        "temperature": reading.temperature,
                        "gas_index": reading.gas_index,
                        "vibration_x": reading.vibration_x,
                        "vibration_y": reading.vibration_y,
                        "vibration_z": reading.vibration_z,
                    },
                    analysis_result=ai_result,
                    confidence_score=75.0,  # Lower confidence for AI
                    detected_at=reading.timestamp,
                    processed_at=datetime.utcnow(),
                )
                db.add(signal)
                signals_created.append(signal)
        except Exception as e:
            print(f"AI analysis failed: {e}")
    
    if signals_created:
        db.commit()
    
    return signals_created


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_recent_data(
    factory_id: Optional[int] = None,
    hours: int = 1,
    use_ai: bool = True,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Analyze recent sensor data and generate signals.
    This scans the last N hours of data for all devices and creates signals.
    
    - **factory_id**: Optional factory filter (admin only, others use their factory)
    - **hours**: How many hours of data to analyze (default: 1)
    - **use_ai**: Whether to use Gemini AI for analysis (default: True)
    """
    # Determine factory
    if current_user.role != models.UserRole.ADMIN:
        factory_id = current_user.factory_id
    
    if not factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Factory ID required"
        )
    
    # Get devices for factory
    devices = db.query(models.Device).filter(
        models.Device.factory_id == factory_id,
        models.Device.is_active == True
    ).all()
    
    if not devices:
        return {"status": "no_devices", "message": "No active devices found", "signals_created": 0}
    
    # Get recent readings
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    total_signals = 0
    device_results = []
    
    for device in devices:
        # Get readings not yet analyzed (simplified: just get recent readings)
        readings = db.query(models.SensorReading).filter(
            models.SensorReading.device_id == device.id,
            models.SensorReading.timestamp >= cutoff_time
        ).order_by(desc(models.SensorReading.timestamp)).limit(10).all()
        
        device_signals = 0
        for reading in readings:
            signals = await process_signals_for_reading(db, reading, device, use_ai)
            device_signals += len(signals)
        
        total_signals += device_signals
        device_results.append({
            "device_id": device.device_id,
            "device_name": device.device_name,
            "readings_analyzed": len(readings),
            "signals_created": device_signals
        })
    
    return {
        "status": "success",
        "factory_id": factory_id,
        "hours_analyzed": hours,
        "total_signals_created": total_signals,
        "devices": device_results
    }


@router.get("", response_model=List[schemas.Signal])
async def get_signals(
    factory_id: Optional[int] = None,
    device_id: Optional[int] = None,
    signal_type: Optional[schemas.SignalType] = None,
    severity: Optional[schemas.AlertSeverity] = None,
    status: Optional[schemas.SignalStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get signals/anomalies with optional filters.
    """
    query = db.query(models.Signal)
    
    # Filter by factory based on user role
    if current_user.role != models.UserRole.ADMIN:
        query = query.filter(models.Signal.factory_id == current_user.factory_id)
    elif factory_id:
        query = query.filter(models.Signal.factory_id == factory_id)
    
    # Apply optional filters
    if device_id:
        query = query.filter(models.Signal.device_id == device_id)
    if signal_type:
        query = query.filter(models.Signal.signal_type == models.SignalType(signal_type.value))
    if severity:
        query = query.filter(models.Signal.severity == models.AlertSeverity(severity.value))
    if status:
        query = query.filter(models.Signal.status == models.SignalStatus(status.value))
    
    signals = query.order_by(desc(models.Signal.detected_at)).limit(limit).all()
    return signals


@router.get("/summary")
async def get_signals_summary(
    factory_id: Optional[int] = None,
    period: str = "24h",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get summary of signals for a factory.
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
    
    # Determine factory
    if current_user.role != models.UserRole.ADMIN:
        factory_id = current_user.factory_id
    
    if not factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Factory ID required"
        )
    
    # Count by severity
    severity_counts = db.query(
        models.Signal.severity,
        func.count(models.Signal.id).label('count')
    ).filter(
        models.Signal.factory_id == factory_id,
        models.Signal.detected_at >= start_time
    ).group_by(models.Signal.severity).all()
    
    # Count by type
    type_counts = db.query(
        models.Signal.signal_type,
        func.count(models.Signal.id).label('count')
    ).filter(
        models.Signal.factory_id == factory_id,
        models.Signal.detected_at >= start_time
    ).group_by(models.Signal.signal_type).all()
    
    # Count by status
    status_counts = db.query(
        models.Signal.status,
        func.count(models.Signal.id).label('count')
    ).filter(
        models.Signal.factory_id == factory_id,
        models.Signal.detected_at >= start_time
    ).group_by(models.Signal.status).all()
    
    return {
        "factory_id": factory_id,
        "period": period,
        "total_signals": sum(c[1] for c in severity_counts),
        "by_severity": {str(s.value): c for s, c in severity_counts},
        "by_type": {str(t.value): c for t, c in type_counts},
        "by_status": {str(st.value): c for st, c in status_counts},
        "generated_at": now.isoformat()
    }


@router.get("/{signal_id}", response_model=schemas.Signal)
async def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific signal by ID.
    """
    signal = db.query(models.Signal).filter(models.Signal.id == signal_id).first()
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    # Check access
    if current_user.role != models.UserRole.ADMIN:
        if signal.factory_id != current_user.factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this signal"
            )
    
    return signal


@router.post("/{signal_id}/acknowledge")
async def acknowledge_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Acknowledge a signal.
    """
    signal = db.query(models.Signal).filter(models.Signal.id == signal_id).first()
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    # Check access
    if current_user.role != models.UserRole.ADMIN:
        if signal.factory_id != current_user.factory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to acknowledge this signal"
            )
    
    signal.status = models.SignalStatus.COMPLETED
    signal.processed_at = datetime.utcnow()
    db.commit()
    
    return {"status": "acknowledged", "signal_id": signal_id}


@router.post("/generate-from-mock")
async def generate_signals_from_mock_data(
    factory_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Generate signals from existing mock/seeded data.
    This analyzes all recent sensor readings and creates appropriate signals.
    Useful after running the seed script.
    """
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.FACTORY_OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Determine factory
    if current_user.role != models.UserRole.ADMIN:
        factory_id = current_user.factory_id
    
    if not factory_id:
        # Get all factories if admin
        factories = db.query(models.Factory).all()
        factory_ids = [f.id for f in factories]
    else:
        factory_ids = [factory_id]
    
    total_signals = 0
    results = []
    
    for fid in factory_ids:
        devices = db.query(models.Device).filter(
            models.Device.factory_id == fid,
            models.Device.is_active == True
        ).all()
        
        factory_signals = 0
        
        for device in devices:
            # Get latest readings (limit to 50 per device)
            readings = db.query(models.SensorReading).filter(
                models.SensorReading.device_id == device.id
            ).order_by(desc(models.SensorReading.timestamp)).limit(50).all()
            
            for reading in readings:
                # Check thresholds and create signals
                anomalies = check_thresholds(reading, device)
                
                for anomaly in anomalies:
                    # Check if similar signal already exists
                    existing = db.query(models.Signal).filter(
                        models.Signal.device_id == device.id,
                        models.Signal.title == anomaly["title"],
                        models.Signal.detected_at == reading.timestamp
                    ).first()
                    
                    if not existing:
                        signal = models.Signal(
                            device_id=device.id,
                            factory_id=device.factory_id,
                            signal_type=anomaly["type"],
                            status=models.SignalStatus.NEW,
                            title=anomaly["title"],
                            description=anomaly["description"],
                            severity=anomaly["severity"],
                            recommendation=anomaly["recommendation"],
                            input_data={
                                "temperature": reading.temperature,
                                "gas_index": reading.gas_index,
                                "vibration_x": reading.vibration_x,
                                "vibration_y": reading.vibration_y,
                                "vibration_z": reading.vibration_z,
                            },
                            confidence_score=95.0,
                            detected_at=reading.timestamp,
                        )
                        db.add(signal)
                        factory_signals += 1
        
        total_signals += factory_signals
        results.append({"factory_id": fid, "signals_created": factory_signals})
        db.commit()
    
    return {
        "status": "success",
        "total_signals_created": total_signals,
        "results": results
    }
