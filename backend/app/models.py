from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    FACTORY_OWNER = "factory_owner"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AlertSeverity(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SignalType(enum.Enum):
    ANOMALY = "anomaly"
    THRESHOLD_BREACH = "threshold_breach"
    PREDICTIVE = "predictive"
    MAINTENANCE = "maintenance"
    EFFICIENCY = "efficiency"


class SignalStatus(enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    factory = relationship("Factory", back_populates="users")


class Factory(Base):
    __tablename__ = "factories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    industry = Column(String(100))  # steel, foundry, chemicals, etc.
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    users = relationship("User", back_populates="factory")
    devices = relationship("Device", back_populates="factory")
    alerts = relationship("Alert", back_populates="factory")
    reports = relationship("Report", back_populates="factory")
    signals = relationship("Signal", back_populates="factory")


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, index=True, nullable=False)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(100))  # ESP32, etc.
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    machine_name = Column(String(255))  # Which machine this is installed on
    location = Column(String(255))  # Location within factory
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime(timezone=True))
    firmware_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    factory = relationship("Factory", back_populates="devices")
    sensor_readings = relationship("SensorReading", back_populates="device")
    alerts = relationship("Alert", back_populates="device")
    signals = relationship("Signal", back_populates="device")


class SensorReading(Base):
    """
    Time series sensor data from ESP32 devices.
    In production, consider using TimescaleDB hypertables for better time series performance.
    """
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Sensor values
    temperature = Column(Float)  # Celsius
    gas_index = Column(Float)  # Air quality/gas sensor reading
    vibration_x = Column(Float)  # Vibration on X axis
    vibration_y = Column(Float)  # Vibration on Y axis
    vibration_z = Column(Float)  # Vibration on Z axis
    
    # Optional additional metrics
    humidity = Column(Float)
    pressure = Column(Float)
    power_consumption = Column(Float)  # kWh
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    device = relationship("Device", back_populates="sensor_readings")


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    
    alert_type = Column(String(100))  # temperature_high, vibration_anomaly, device_offline, etc.
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.INFO)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Metrics at time of alert
    metric_value = Column(Float)
    threshold_value = Column(Float)
    
    triggered_at = Column(DateTime(timezone=True), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    device = relationship("Device", back_populates="alerts")
    factory = relationship("Factory", back_populates="alerts")


class Signal(Base):
    """
    Generated signals from sensor data analysis.
    These are insights/anomalies detected from the data using the Gemini API or rule-based logic.
    """
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False, index=True)
    
    signal_type = Column(SQLEnum(SignalType), default=SignalType.ANOMALY)
    status = Column(SQLEnum(SignalStatus), default=SignalStatus.NEW)
    
    # Signal details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.INFO)
    
    # Analysis data
    input_data = Column(JSON)  # Sensor data that triggered the signal
    analysis_result = Column(JSON)  # AI analysis result
    recommendation = Column(Text)  # Recommended action
    
    # Confidence score (0-100)
    confidence_score = Column(Float)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    device = relationship("Device", back_populates="signals")
    factory = relationship("Factory", back_populates="signals")


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    
    report_type = Column(String(100))  # weekly, monthly, compliance
    report_period_start = Column(DateTime(timezone=True), nullable=False)
    report_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Report content (JSON-serializable data)
    summary = Column(Text)  # JSON string with summary metrics
    
    # File path if PDF/Excel generated
    file_path = Column(String(500))
    
    generated_by = Column(Integer, ForeignKey("users.id"))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    factory = relationship("Factory", back_populates="reports")
