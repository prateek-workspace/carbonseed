"""
Seed data script for Carbonseed backend.
Creates initial users, factories, devices, sample sensor data, and generates signals.
"""
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash


def generate_signals_for_reading(db: Session, reading: models.SensorReading, device: models.Device):
    """Generate signals based on threshold checks for a reading"""
    THRESHOLDS = {
        "temperature_high": 900,
        "gas_index_high": 400,
        "vibration_critical": 8.0,
        "vibration_warning": 5.0,
        "power_consumption_high": 50,
    }
    
    signals_created = []
    
    # Temperature check
    if reading.temperature and reading.temperature > THRESHOLDS["temperature_high"]:
        signal = models.Signal(
            device_id=device.id,
            factory_id=device.factory_id,
            signal_type=models.SignalType.THRESHOLD_BREACH,
            status=models.SignalStatus.NEW,
            title="High Temperature Alert",
            description=f"Temperature {reading.temperature:.1f}°C exceeds threshold of {THRESHOLDS['temperature_high']}°C",
            severity=models.AlertSeverity.CRITICAL if reading.temperature > THRESHOLDS["temperature_high"] * 1.1 else models.AlertSeverity.WARNING,
            recommendation="Check cooling systems and reduce furnace load if safe to do so.",
            input_data={
                "temperature": reading.temperature,
                "gas_index": reading.gas_index,
                "vibration_x": reading.vibration_x,
            },
            confidence_score=95.0,
            detected_at=reading.timestamp,
        )
        db.add(signal)
        signals_created.append(signal)
    
    # Gas index check
    if reading.gas_index and reading.gas_index > THRESHOLDS["gas_index_high"]:
        signal = models.Signal(
            device_id=device.id,
            factory_id=device.factory_id,
            signal_type=models.SignalType.ANOMALY,
            status=models.SignalStatus.NEW,
            title="Elevated Gas Index",
            description=f"Gas index {reading.gas_index:.1f} exceeds threshold of {THRESHOLDS['gas_index_high']}",
            severity=models.AlertSeverity.WARNING,
            recommendation="Check ventilation systems and air quality.",
            input_data={
                "gas_index": reading.gas_index,
            },
            confidence_score=90.0,
            detected_at=reading.timestamp,
        )
        db.add(signal)
        signals_created.append(signal)
    
    # Vibration check
    max_vibration = max(
        reading.vibration_x or 0,
        reading.vibration_y or 0,
        reading.vibration_z or 0
    )
    if max_vibration > THRESHOLDS["vibration_critical"]:
        signal = models.Signal(
            device_id=device.id,
            factory_id=device.factory_id,
            signal_type=models.SignalType.MAINTENANCE,
            status=models.SignalStatus.NEW,
            title="Critical Vibration Detected",
            description=f"Vibration level {max_vibration:.2f} exceeds critical threshold",
            severity=models.AlertSeverity.CRITICAL,
            recommendation="Immediate maintenance required. Check for bearing wear.",
            input_data={
                "vibration_x": reading.vibration_x,
                "vibration_y": reading.vibration_y,
                "vibration_z": reading.vibration_z,
            },
            confidence_score=95.0,
            detected_at=reading.timestamp,
        )
        db.add(signal)
        signals_created.append(signal)
    elif max_vibration > THRESHOLDS["vibration_warning"]:
        signal = models.Signal(
            device_id=device.id,
            factory_id=device.factory_id,
            signal_type=models.SignalType.PREDICTIVE,
            status=models.SignalStatus.NEW,
            title="Elevated Vibration Warning",
            description=f"Vibration level {max_vibration:.2f} exceeds warning threshold",
            severity=models.AlertSeverity.WARNING,
            recommendation="Schedule preventive maintenance within 48 hours.",
            input_data={
                "vibration_x": reading.vibration_x,
                "vibration_y": reading.vibration_y,
                "vibration_z": reading.vibration_z,
            },
            confidence_score=85.0,
            detected_at=reading.timestamp,
        )
        db.add(signal)
        signals_created.append(signal)
    
    return signals_created


def seed_database():
    """Populate database with sample data for MVP testing"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_factory = db.query(models.Factory).first()
        if existing_factory:
            print("Database already has data. Skipping seed.")
            return
        
        # Create factories
        factory1 = models.Factory(
            name="Steel Forge Industries",
            location="Pune, Maharashtra",
            industry="steel",
            contact_email="contact@steelforge.in",
            contact_phone="+91-9876543210"
        )
        
        factory2 = models.Factory(
            name="Chemical Processing Ltd",
            location="Vadodara, Gujarat",
            industry="chemicals",
            contact_email="info@chemprocessing.in",
            contact_phone="+91-9876543211"
        )
        
        db.add_all([factory1, factory2])
        db.commit()
        
        # Create users
        admin_user = models.User(
            email="admin@carbonseed.io",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=models.UserRole.ADMIN,
            is_active=True
        )
        
        factory1_owner = models.User(
            email="owner@steelforge.in",
            hashed_password=get_password_hash("password123"),
            full_name="Rajesh Kumar",
            role=models.UserRole.FACTORY_OWNER,
            factory_id=factory1.id,
            is_active=True
        )
        
        factory1_operator = models.User(
            email="operator@steelforge.in",
            hashed_password=get_password_hash("password123"),
            full_name="Suresh Sharma",
            role=models.UserRole.OPERATOR,
            factory_id=factory1.id,
            is_active=True
        )
        
        factory2_owner = models.User(
            email="owner@chemprocessing.in",
            hashed_password=get_password_hash("password123"),
            full_name="Amit Patel",
            role=models.UserRole.FACTORY_OWNER,
            factory_id=factory2.id,
            is_active=True
        )
        
        db.add_all([admin_user, factory1_owner, factory1_operator, factory2_owner])
        db.commit()
        
        # Create devices
        device1 = models.Device(
            device_id="ESP32-SF-001",
            device_name="Furnace Monitor 1",
            device_type="ESP32",
            factory_id=factory1.id,
            machine_name="Main Blast Furnace",
            location="Floor 1, Bay A",
            is_active=True,
            firmware_version="v1.2.0",
            last_seen=datetime.utcnow()
        )
        
        device2 = models.Device(
            device_id="ESP32-SF-002",
            device_name="Cooling Tower Monitor",
            device_type="ESP32",
            factory_id=factory1.id,
            machine_name="Cooling Tower Unit 3",
            location="Floor 2, Bay B",
            is_active=True,
            firmware_version="v1.2.0",
            last_seen=datetime.utcnow()
        )
        
        device3 = models.Device(
            device_id="ESP32-CP-001",
            device_name="Reactor Monitor",
            device_type="ESP32",
            factory_id=factory2.id,
            machine_name="Chemical Reactor A",
            location="Building 3, Floor 1",
            is_active=True,
            firmware_version="v1.2.0",
            last_seen=datetime.utcnow()
        )
        
        db.add_all([device1, device2, device3])
        db.commit()
        
        # Create sample sensor readings (last 24 hours) with some anomalies
        now = datetime.utcnow()
        devices = [device1, device2, device3]
        all_readings = []
        total_signals = 0
        
        print("Generating sensor readings and signals...")
        for device in devices:
            device_signals = 0
            # Generate readings every 5 minutes for last 24 hours
            for i in range(288):  # 24 hours * 12 readings per hour
                timestamp = now - timedelta(minutes=i * 5)
                
                # Simulate realistic sensor data with some anomalies
                base_temp = 850 if device.machine_name.startswith("Main") else 45
                
                # Inject some anomalies randomly
                is_anomaly = random.random() < 0.05  # 5% chance of anomaly
                
                if is_anomaly:
                    temp_variation = random.uniform(50, 100)  # Higher variation for anomaly
                    vibration_multiplier = random.uniform(2, 4)
                    gas_multiplier = random.uniform(1.2, 1.5)
                else:
                    temp_variation = random.uniform(-20, 20)
                    vibration_multiplier = 1
                    gas_multiplier = 1
                
                reading = models.SensorReading(
                    device_id=device.id,
                    timestamp=timestamp,
                    temperature=base_temp + temp_variation,
                    gas_index=random.uniform(100, 350) * gas_multiplier,
                    vibration_x=random.uniform(0.5, 3.5) * vibration_multiplier,
                    vibration_y=random.uniform(0.5, 3.5) * vibration_multiplier,
                    vibration_z=random.uniform(0.5, 3.5) * vibration_multiplier,
                    humidity=random.uniform(30, 70),
                    pressure=random.uniform(990, 1020),
                    power_consumption=random.uniform(15, 45)
                )
                db.add(reading)
                all_readings.append((reading, device))
                
                # Generate signals for anomalous readings
                if is_anomaly and i < 50:  # Only generate signals for recent anomalies
                    signals = generate_signals_for_reading(db, reading, device)
                    device_signals += len(signals)
            
            total_signals += device_signals
            print(f"  {device.device_name}: {device_signals} signals generated")
            
            # Commit in batches
            db.commit()
        
        print(f"Total signals generated: {total_signals}")
        
        # Create sample alerts
        alert1 = models.Alert(
            device_id=device1.id,
            factory_id=factory1.id,
            alert_type="temperature_high",
            severity=models.AlertSeverity.WARNING,
            status=models.AlertStatus.ACTIVE,
            title="High Temperature Detected",
            message="Furnace temperature exceeded threshold of 900°C",
            metric_value=925.5,
            threshold_value=900.0,
            triggered_at=now - timedelta(hours=2)
        )
        
        alert2 = models.Alert(
            device_id=device2.id,
            factory_id=factory1.id,
            alert_type="vibration_anomaly",
            severity=models.AlertSeverity.CRITICAL,
            status=models.AlertStatus.ACKNOWLEDGED,
            title="Abnormal Vibration Pattern",
            message="Cooling tower showing unusual vibration levels",
            metric_value=8.5,
            threshold_value=5.0,
            triggered_at=now - timedelta(hours=6),
            acknowledged_at=now - timedelta(hours=5),
            acknowledged_by=factory1_operator.id
        )
        
        alert3 = models.Alert(
            device_id=device3.id,
            factory_id=factory2.id,
            alert_type="gas_index_high",
            severity=models.AlertSeverity.INFO,
            status=models.AlertStatus.RESOLVED,
            title="Elevated Gas Levels",
            message="Gas index temporarily elevated during process cycle",
            metric_value=450.0,
            threshold_value=400.0,
            triggered_at=now - timedelta(days=1),
            resolved_at=now - timedelta(hours=22)
        )
        
        db.add_all([alert1, alert2, alert3])
        db.commit()
        
        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print("\nTest Credentials:")
        print("-"*50)
        print("Admin:          admin@carbonseed.io / admin123")
        print("Factory Owner:  owner@steelforge.in / password123")
        print("Operator:       operator@steelforge.in / password123")
        print("Factory 2:      owner@chemprocessing.in / password123")
        print("-"*50)
        print(f"\nData Summary:")
        print(f"  Factories: 2")
        print(f"  Users: 4")
        print(f"  Devices: 3")
        print(f"  Sensor Readings: {288 * 3}")
        print(f"  Signals: {total_signals}")
        print(f"  Alerts: 3")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Seeding database...")
    seed_database()
