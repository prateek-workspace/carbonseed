from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from datetime import datetime, timedelta
from app import models, schemas, auth
from app.database import get_db
import json

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/weekly", response_model=schemas.Report)
async def get_weekly_report(
    factory_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Generate weekly operational report.
    Includes summary of operations, alerts, and key metrics.
    """
    # Determine factory
    if current_user.role != models.UserRole.ADMIN:
        factory_id = current_user.factory_id
    
    if not factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Factory ID required"
        )
    
    # Calculate date range (last 7 days)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    
    # Check if report already exists
    existing_report = db.query(models.Report).filter(
        models.Report.factory_id == factory_id,
        models.Report.report_type == "weekly",
        models.Report.report_period_start >= start_time - timedelta(days=1)
    ).first()
    
    if existing_report:
        return existing_report
    
    # Generate report data
    device_ids = [d.id for d in db.query(models.Device).filter(
        models.Device.factory_id == factory_id
    ).all()]
    
    if not device_ids:
        summary = json.dumps({
            "error": "No devices found for this factory"
        })
    else:
        # Aggregate metrics
        metrics = db.query(
            func.avg(models.SensorReading.temperature).label('avg_temp'),
            func.max(models.SensorReading.temperature).label('max_temp'),
            func.min(models.SensorReading.temperature).label('min_temp'),
            func.avg(models.SensorReading.gas_index).label('avg_gas'),
            func.sum(models.SensorReading.power_consumption).label('total_power'),
            func.count(models.SensorReading.id).label('data_points')
        ).filter(
            models.SensorReading.device_id.in_(device_ids),
            models.SensorReading.timestamp >= start_time,
            models.SensorReading.timestamp <= end_time
        ).first()
        
        # Count alerts
        alert_counts = db.query(
            models.Alert.severity,
            func.count(models.Alert.id).label('count')
        ).filter(
            models.Alert.factory_id == factory_id,
            models.Alert.triggered_at >= start_time,
            models.Alert.triggered_at <= end_time
        ).group_by(models.Alert.severity).all()
        
        alerts_by_severity = {str(sev): count for sev, count in alert_counts}
        
        summary = json.dumps({
            "period": "weekly",
            "start_date": start_time.isoformat(),
            "end_date": end_time.isoformat(),
            "metrics": {
                "avg_temperature": metrics.avg_temp,
                "max_temperature": metrics.max_temp,
                "min_temperature": metrics.min_temp,
                "avg_gas_index": metrics.avg_gas,
                "total_energy_consumption_kwh": metrics.total_power,
                "data_points_collected": metrics.data_points
            },
            "alerts": alerts_by_severity,
            "device_count": len(device_ids)
        })
    
    # Create report record
    report = models.Report(
        factory_id=factory_id,
        report_type="weekly",
        report_period_start=start_time,
        report_period_end=end_time,
        summary=summary,
        generated_by=current_user.id
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.get("/monthly", response_model=schemas.Report)
async def get_monthly_report(
    factory_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Generate monthly operational report.
    """
    # Determine factory
    if current_user.role != models.UserRole.ADMIN:
        factory_id = current_user.factory_id
    
    if not factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Factory ID required"
        )
    
    # Calculate date range (last 30 days)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)
    
    # Check if report already exists
    existing_report = db.query(models.Report).filter(
        models.Report.factory_id == factory_id,
        models.Report.report_type == "monthly",
        models.Report.report_period_start >= start_time - timedelta(days=5)
    ).first()
    
    if existing_report:
        return existing_report
    
    # Generate report (similar logic to weekly)
    device_ids = [d.id for d in db.query(models.Device).filter(
        models.Device.factory_id == factory_id
    ).all()]
    
    if not device_ids:
        summary = json.dumps({
            "error": "No devices found for this factory"
        })
    else:
        metrics = db.query(
            func.avg(models.SensorReading.temperature).label('avg_temp'),
            func.max(models.SensorReading.temperature).label('max_temp'),
            func.min(models.SensorReading.temperature).label('min_temp'),
            func.avg(models.SensorReading.gas_index).label('avg_gas'),
            func.sum(models.SensorReading.power_consumption).label('total_power'),
            func.count(models.SensorReading.id).label('data_points')
        ).filter(
            models.SensorReading.device_id.in_(device_ids),
            models.SensorReading.timestamp >= start_time,
            models.SensorReading.timestamp <= end_time
        ).first()
        
        alert_counts = db.query(
            models.Alert.severity,
            func.count(models.Alert.id).label('count')
        ).filter(
            models.Alert.factory_id == factory_id,
            models.Alert.triggered_at >= start_time,
            models.Alert.triggered_at <= end_time
        ).group_by(models.Alert.severity).all()
        
        alerts_by_severity = {str(sev): count for sev, count in alert_counts}
        
        summary = json.dumps({
            "period": "monthly",
            "start_date": start_time.isoformat(),
            "end_date": end_time.isoformat(),
            "metrics": {
                "avg_temperature": metrics.avg_temp,
                "max_temperature": metrics.max_temp,
                "min_temperature": metrics.min_temp,
                "avg_gas_index": metrics.avg_gas,
                "total_energy_consumption_kwh": metrics.total_power,
                "data_points_collected": metrics.data_points
            },
            "alerts": alerts_by_severity,
            "device_count": len(device_ids)
        })
    
    report = models.Report(
        factory_id=factory_id,
        report_type="monthly",
        report_period_start=start_time,
        report_period_end=end_time,
        summary=summary,
        generated_by=current_user.id
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.get("/compliance", response_model=schemas.Report)
async def get_compliance_report(
    factory_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Generate compliance-ready report.
    Formatted for SPCB, PAT, CBAM requirements.
    
    This report includes:
    - Emissions data (gas index as proxy)
    - Energy consumption
    - Operational uptime
    - Anomaly logs
    """
    # Determine factory
    if current_user.role != models.UserRole.ADMIN:
        factory_id = current_user.factory_id
    
    if not factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Factory ID required"
        )
    
    # Get factory details
    factory = db.query(models.Factory).filter(models.Factory.id == factory_id).first()
    
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factory not found"
        )
    
    # Last 30 days for compliance
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)
    
    device_ids = [d.id for d in db.query(models.Device).filter(
        models.Device.factory_id == factory_id
    ).all()]
    
    if not device_ids:
        summary = json.dumps({
            "error": "No devices found for this factory"
        })
    else:
        # Compliance metrics
        metrics = db.query(
            func.avg(models.SensorReading.gas_index).label('avg_emissions'),
            func.max(models.SensorReading.gas_index).label('max_emissions'),
            func.sum(models.SensorReading.power_consumption).label('total_energy'),
            func.count(models.SensorReading.id).label('data_points')
        ).filter(
            models.SensorReading.device_id.in_(device_ids),
            models.SensorReading.timestamp >= start_time,
            models.SensorReading.timestamp <= end_time
        ).first()
        
        # Calculate operational hours
        hours_in_period = (end_time - start_time).total_seconds() / 3600
        
        summary = json.dumps({
            "report_type": "compliance",
            "compliance_standards": ["SPCB", "PAT", "CBAM"],
            "factory": {
                "name": factory.name,
                "location": factory.location,
                "industry": factory.industry
            },
            "reporting_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours_in_period
            },
            "emissions": {
                "avg_gas_index": metrics.avg_emissions,
                "max_gas_index": metrics.max_emissions,
                "unit": "gas_index",
                "note": "Gas index is a proxy for air quality and emissions"
            },
            "energy": {
                "total_consumption_kwh": metrics.total_energy,
                "avg_consumption_per_hour": metrics.total_energy / hours_in_period if metrics.total_energy else 0
            },
            "monitoring": {
                "data_points_collected": metrics.data_points,
                "device_count": len(device_ids),
                "coverage": "Continuous monitoring via IoT sensors"
            }
        })
    
    report = models.Report(
        factory_id=factory_id,
        report_type="compliance",
        report_period_start=start_time,
        report_period_end=end_time,
        summary=summary,
        generated_by=current_user.id
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report
