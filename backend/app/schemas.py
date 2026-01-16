from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    FACTORY_OWNER = "factory_owner"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SignalType(str, Enum):
    ANOMALY = "anomaly"
    THRESHOLD_BREACH = "threshold_breach"
    PREDICTIVE = "predictive"
    MAINTENANCE = "maintenance"
    EFFICIENCY = "efficiency"


class SignalStatus(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.VIEWER
    factory_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithFactory(User):
    """User with factory details for login response"""
    factory: Optional["Factory"] = None
    
    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginResponse(BaseModel):
    """Enhanced login response with user details and redirect info"""
    access_token: str
    token_type: str
    user: User
    redirect_url: str  # Where to redirect based on role
    
    class Config:
        from_attributes = True


# Factory Schemas
class FactoryBase(BaseModel):
    name: str
    location: Optional[str] = None
    industry: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class FactoryCreate(FactoryBase):
    pass


class FactoryUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class Factory(FactoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FactoryWithStats(Factory):
    """Factory with aggregated statistics"""
    device_count: int = 0
    user_count: int = 0
    active_alerts: int = 0
    
    class Config:
        from_attributes = True


# Device Schemas
class DeviceBase(BaseModel):
    device_id: str
    device_name: str
    device_type: Optional[str] = "ESP32"
    factory_id: int
    machine_name: Optional[str] = None
    location: Optional[str] = None


class DeviceRegister(DeviceBase):
    pass


class DeviceStatus(BaseModel):
    id: int
    device_id: str
    device_name: str
    is_active: bool
    last_seen: Optional[datetime]
    uptime_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True


class Device(DeviceBase):
    id: int
    is_active: bool
    last_seen: Optional[datetime]
    firmware_version: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sensor Reading Schemas
class SensorReadingCreate(BaseModel):
    device_id: str  # External device_id from ESP32
    timestamp: Optional[datetime] = None
    temperature: Optional[float] = None
    gas_index: Optional[float] = None
    vibration_x: Optional[float] = None
    vibration_y: Optional[float] = None
    vibration_z: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    power_consumption: Optional[float] = None


class SensorReading(BaseModel):
    id: int
    device_id: int
    timestamp: datetime
    temperature: Optional[float]
    gas_index: Optional[float]
    vibration_x: Optional[float]
    vibration_y: Optional[float]
    vibration_z: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]
    power_consumption: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LatestData(BaseModel):
    temperature: Optional[float]
    gas_index: Optional[float]
    vibration_health: Optional[str]  # "good", "moderate", "critical"
    device_uptime: Optional[float]  # percentage
    last_update: Optional[datetime]


# Alert Schemas
class AlertBase(BaseModel):
    alert_type: str
    severity: AlertSeverity
    title: str
    message: str
    metric_value: Optional[float]
    threshold_value: Optional[float]


class AlertCreate(AlertBase):
    device_id: int
    factory_id: int
    triggered_at: datetime


class Alert(AlertBase):
    id: int
    device_id: int
    factory_id: int
    status: AlertStatus
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Signal Schemas
class SignalBase(BaseModel):
    signal_type: SignalType
    title: str
    description: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.INFO
    recommendation: Optional[str] = None


class SignalCreate(SignalBase):
    device_id: int
    factory_id: int
    input_data: Optional[Dict[str, Any]] = None
    detected_at: datetime


class Signal(SignalBase):
    id: int
    device_id: int
    factory_id: int
    status: SignalStatus
    input_data: Optional[Dict[str, Any]]
    analysis_result: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    detected_at: datetime
    processed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SignalWithDevice(Signal):
    """Signal with device info for listing"""
    device: Optional[Device] = None
    
    class Config:
        from_attributes = True


# Insights Schema
class InsightMetrics(BaseModel):
    avg_temperature: Optional[float]
    max_temperature: Optional[float]
    avg_gas_index: Optional[float]
    vibration_health_score: Optional[float]
    device_uptime_percentage: Optional[float]
    anomalies_detected: int
    energy_consumption: Optional[float]


class Insight(BaseModel):
    period: str  # "24h", "7d", "30d"
    factory_id: int
    metrics: InsightMetrics
    generated_at: datetime


# Report Schemas
class ReportBase(BaseModel):
    report_type: str  # weekly, monthly, compliance
    report_period_start: datetime
    report_period_end: datetime


class ReportCreate(ReportBase):
    factory_id: int
    summary: Optional[str]


class Report(ReportBase):
    id: int
    factory_id: int
    summary: Optional[str]
    file_path: Optional[str]
    generated_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_devices: int
    active_devices: int
    total_alerts: int
    active_alerts: int
    total_signals: int
    new_signals: int
    avg_temperature: Optional[float]
    avg_gas_index: Optional[float]
    vibration_health_score: Optional[float]
    energy_consumption_24h: Optional[float]


# Update forward references
UserWithFactory.model_rebuild()
