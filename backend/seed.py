"""
Seed data script for Carbonseed backend.
Creates initial users, factories, devices, and sample sensor data.
"""
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

def seed_database():
    """Populate database with sample data for MVP testing"""
    db = SessionLocal()
    
    try:
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
        
        # Create sample sensor readings (last 24 hours)
        now = datetime.utcnow()
        devices = [device1, device2, device3]
        
        print("Generating sensor readings...")
        for device in devices:
            # Generate readings every 5 minutes for last 24 hours
            for i in range(288):  # 24 hours * 12 readings per hour
                timestamp = now - timedelta(minutes=i * 5)
                
                # Simulate realistic sensor data with some variation
                base_temp = 850 if device.machine_name.startswith("Main") else 45
                temp_variation = random.uniform(-20, 20)
                
                reading = models.SensorReading(
                    device_id=device.id,
                    timestamp=timestamp,
                    temperature=base_temp + temp_variation,
                    gas_index=random.uniform(100, 500),
                    vibration_x=random.uniform(0.5, 3.5),
                    vibration_y=random.uniform(0.5, 3.5),
                    vibration_z=random.uniform(0.5, 3.5),
                    humidity=random.uniform(30, 70),
                    pressure=random.uniform(990, 1020),
                    power_consumption=random.uniform(15, 45)
                )
                db.add(reading)
            
            # Commit in batches
            if devices.index(device) % 1 == 0:
                db.commit()
        
        db.commit()
        
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
        
        print("Database seeded successfully!")
        print("\nTest Credentials:")
        print("Admin: admin@carbonseed.io / admin123")
        print("Factory Owner: owner@steelforge.in / password123")
        print("Operator: operator@steelforge.in / password123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Seeding database...")
    seed_database()
