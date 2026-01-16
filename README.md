# Carbonseed

**Industrial IoT SaaS for Indian MSMEs**

Carbonseed provides real-time operational intelligence and compliance reporting for Indian industrial facilities through low-cost ESP32-based edge devices.

## Project Structure

```
carbonseed/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── models.py  # Database models
│   │   ├── schemas.py # Pydantic schemas
│   │   ├── auth.py    # Authentication
│   │   └── main.py    # FastAPI app
│   ├── seed.py        # Database seeding
│   └── requirements.txt
│
└── frontend/          # Next.js frontend
    ├── src/
    │   └── app/
    │       ├── page.tsx           # Homepage
    │       ├── login/page.tsx     # Login
    │       └── dashboard/page.tsx # Dashboard
    └── package.json
```

## Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Seed database
python seed.py

# Run server
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at: http://localhost:3000

## Test Credentials

- **Admin**: admin@carbonseed.io / admin123
- **Factory Owner**: owner@steelforge.in / password123
- **Operator**: operator@steelforge.in / password123

## System Architecture

```
ESP32 Sensors → HTTP/MQTT → FastAPI Backend → PostgreSQL
                                    ↓
                              Analytics Engine
                                    ↓
                            Next.js Dashboard
```

## Key Features

### For Factory Operators
- Real-time monitoring of temperature, vibration, emissions
- Instant alerts for anomalies
- Device health and uptime tracking

### For Compliance Officers
- Automated SPCB/PAT/CBAM reports
- Historical data with audit trails
- Energy consumption tracking

### For Management
- Cost savings insights
- Downtime analysis
- Performance benchmarking

## Tech Stack

**Backend**
- Python FastAPI
- PostgreSQL (TimescaleDB-ready)
- JWT authentication
- RESTful API

**Frontend**
- Next.js 14 with TypeScript
- Tailwind CSS
- Recharts for visualization
- Serious, industrial design

**Edge Devices**
- ESP32 microcontrollers
- Multi-sensor support (temperature, gas, vibration)
- Low power consumption
- WiFi connectivity

## API Endpoints

### Authentication
- `POST /auth/login`
- `GET /auth/me`

### Devices
- `POST /devices/register`
- `GET /devices`
- `GET /devices/{id}/status`

### Data
- `POST /ingest`
- `GET /data/latest`
- `GET /data/timeseries`

### Analytics
- `GET /insights`
- `GET /alerts`

### Reports
- `GET /reports/weekly`
- `GET /reports/monthly`
- `GET /reports/compliance`

## ESP32 Integration

Send sensor data to `/ingest`:

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

## Analytics Approach

The system uses **simple, explainable analytics**:

1. **Rolling Averages** - Smooth trends over time windows
2. **Baseline Comparison** - Compare current vs historical patterns
3. **Threshold Detection** - Alert when metrics exceed limits
4. **Health Scoring** - Calculate simple health scores

**Future ML Integration**: Code has placeholders for integrating hosted ML APIs for advanced anomaly detection and predictive maintenance.

## Database Schema

- **User** - Factory personnel with role-based access
- **Factory** - Industrial facilities
- **Device** - ESP32 edge devices
- **SensorReading** - Time series sensor data
- **Alert** - System-generated alerts
- **Report** - Compliance reports

## License

Proprietary - Carbonseed 2026
