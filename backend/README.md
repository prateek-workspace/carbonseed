# Carbonseed Backend

Industrial IoT SaaS backend built with FastAPI and PostgreSQL.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL

Install PostgreSQL and create a database:

```bash
createdb carbonseed
createuser carbonseed --password
# Enter password: password
```

Or using Docker:

```bash
docker run --name carbonseed-db \
  -e POSTGRES_DB=carbonseed \
  -e POSTGRES_USER=carbonseed \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update if needed:

```bash
cp .env.example .env
```

### 4. Seed Database

```bash
python seed.py
```

This creates:
- Sample factories
- Test users
- Devices
- 24 hours of sensor data
- Sample alerts

### 5. Run Server

```bash
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

API docs at: http://localhost:8000/docs

## Test Credentials

- **Admin**: admin@carbonseed.io / admin123
- **Factory Owner**: owner@steelforge.in / password123
- **Operator**: operator@steelforge.in / password123

## API Endpoints

### Authentication
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

### Devices
- `POST /devices/register` - Register new device
- `GET /devices` - List devices
- `GET /devices/{id}/status` - Device status with uptime

### Data Ingestion
- `POST /ingest` - Ingest sensor data from ESP32
- `GET /data/latest` - Latest readings summary
- `GET /data/timeseries` - Time series data for charts

### Insights & Analytics
- `GET /insights` - Analytics insights (24h, 7d, 30d)
- `GET /alerts` - List alerts
- `POST /alerts/{id}/acknowledge` - Acknowledge alert

### Reports
- `GET /reports/weekly` - Weekly report
- `GET /reports/monthly` - Monthly report
- `GET /reports/compliance` - Compliance report (SPCB, PAT, CBAM)

## Database Schema

### Core Models

**User** - Factory users with role-based access
**Factory** - Industrial facilities
**Device** - ESP32 edge devices
**SensorReading** - Time series sensor data
**Alert** - Anomaly alerts
**Report** - Generated reports

## ESP32 Integration

Devices should POST to `/ingest` with:

```json
{
  "device_id": "ESP32-SF-001",
  "timestamp": "2025-01-16T10:30:00Z",
  "temperature": 850.5,
  "gas_index": 320.0,
  "vibration_x": 2.1,
  "vibration_y": 1.8,
  "vibration_z": 2.3,
  "humidity": 45.0,
  "pressure": 1013.2,
  "power_consumption": 32.5
}
```

## Analytics Logic

The system implements simple, explainable analytics:

1. **Rolling Averages** - Track trends over time
2. **Baseline Comparison** - Compare current vs historical
3. **Threshold Detection** - Alert when limits exceeded
4. **Health Scores** - Simple scoring algorithms

### Future ML Integration

Comments in code indicate where ML models would plug in:
- Anomaly detection via Gemini API
- Predictive maintenance
- Energy optimization recommendations

Ready for integration with hosted ML services.

## Production Considerations

- Add API key authentication for devices
- Implement rate limiting
- Add message queue (RabbitMQ/Kafka) for high-throughput
- Use TimescaleDB hypertables for better time series performance
- Add Redis for caching
- Implement proper logging and monitoring
- Add database migrations with Alembic
- Set up proper backup strategy
- Add SSL/TLS termination
- Implement retry logic for ML API calls
