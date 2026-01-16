# Carbonseed System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FACTORY FLOOR                           │
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│  │ Machine │    │ Machine │    │ Machine │    │ Machine │       │
│  │    1    │    │    2    │    │    3    │    │    4    │       │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘       │
│       │              │              │              │            │
│  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐       │
│  │ ESP32-1 │    │ ESP32-2 │    │ ESP32-3 │    │ ESP32-4 │       │
│  │ Sensors │    │ Sensors │    │ Sensors │    │ Sensors │       │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘       │
│       │              │              │              │            │
│       └──────────────┴──────────────┴──────────────┘            │
│                           │                                     │
│                      WiFi Network                               │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            │ HTTPS/JSON
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLOUD BACKEND (FastAPI)                    │
│                                                                 │
│  ┌──────────────┐                                               │
│  │ /ingest      │◄─── Data from ESP32 devices                   │
│  │ endpoint     │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────┐           │
│  │          PostgreSQL Database                     │           │
│  │                                                  │           │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────┐   │           │
│  │  │   Users    │  │   Factories  │  │ Devices │   │           │
│  │  └────────────┘  └──────────────┘  └─────────┘   │           │
│  │                                                  │           │
│  │  ┌────────────────────────────────────────────┐  │           │
│  │  │      Sensor Readings (Time Series)         │  │           │
│  │  │  - Millions of data points                 │  │           │
│  │  │  - Indexed by device_id + timestamp        │  │           │
│  │  └────────────────────────────────────────────┘  │           │
│  │                                                  │           │
│  │  ┌────────────┐  ┌──────────────┐                │           │
│  │  │   Alerts   │  │   Reports    │                │           │
│  │  └────────────┘  └──────────────┘                │           │
│  └──────────────────────────────────────────────────┘           │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────┐           │
│  │         Analytics Engine                         │           │
│  │                                                  │           │
│  │  • Rolling averages                              │           │
│  │  • Baseline comparison                           │           │
│  │  • Threshold detection                           │           │
│  │  • Health scoring                                │           │
│  │  • Alert generation                              │           │
│  │                                                  │           │
│  │  [Future: ML API Integration]                    │           │
│  └──────────────────────────────────────────────────┘           │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────┐           │
│  │            REST API Endpoints                    │           │
│  │                                                  │           │
│  │  /auth/*     - Authentication                    │           │
│  │  /devices/*  - Device management                 │           │
│  │  /data/*     - Data queries                      │           │
│  │  /insights   - Analytics                         │           │
│  │  /alerts     - Alert management                  │           │
│  │  /reports/*  - Report generation                 │           │
│  └──────────────────────────────────────────────────┘           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTPS/JSON + JWT
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WEB DASHBOARD (Next.js)                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Public Homepage (/)                        │    │
│  │                                                         │    │
│  │  • Value proposition                                    │    │
│  │  • How it works                                         │    │
│  │  • Industries served                                    │    │
│  │  • Compliance ready                                     │    │
│  │  • Request pilot CTA                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Login Page (/login)                        │    │
│  │                                                         │    │
│  │  • Email + password                                     │    │
│  │  • No self-signup                                       │    │
│  │  • Enterprise access only                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         Authenticated Dashboard (/dashboard)            │    │
│  │                                                         │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │    │
│  │  │  Temp    │ │   Gas    │ │ Vibration│ │  Uptime  │    │    │
│  │  │  850°C   │ │   320    │ │   Good   │ │   95%    │    │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │    │
│  │                                                         │    │
│  │  ┌────────────────────────────┐  ┌──────────────────┐   │    │
│  │  │   Time Series Charts       │  │  Active Alerts   │   │    │
│  │  │   (Temperature, Gas, etc.) │  │  • High temp     │   │    │
│  │  │                            │  │  • Vibration     │   │    │
│  │  │   [chart visualization]    │  │  • Gas spike     │   │    │
│  │  └────────────────────────────┘  └──────────────────┘   │    │
│  │                                                         │    │
│  │  ┌────────────────────────────┐  ┌──────────────────┐   │    │
│  │  │   Device Status            │  │  Reports         │   │    │
│  │  │   • ESP32-1 ●  Online      │  │  • Weekly        │   │    │
│  │  │   • ESP32-2 ●  Online      │  │  • Monthly       │   │    │
│  │  │   • ESP32-3 ○  Offline     │  │  • Compliance    │   │    │
│  │  └────────────────────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         END USERS                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Factory   │  │ Compliance  │  │  Management │              │
│  │  Operators  │  │  Officers   │  │    Team     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Ingestion Flow
```
ESP32 → WiFi → /ingest API → Validation → PostgreSQL
                                    ↓
                            Analytics Engine
                                    ↓
                              Alert Check
                                    ↓
                        Generate Alerts (if needed)
```

### 2. Dashboard Query Flow
```
User → Dashboard → API Request + JWT → Backend Auth → Database Query
                                                              ↓
                                                    Process & Aggregate
                                                              ↓
                                        JSON Response ← Return Data
```

### 3. Report Generation Flow
```
User Request → /reports/* → Fetch Historical Data → Aggregate Metrics
                                                            ↓
                                                  Generate JSON Report
                                                            ↓
                                                    Return to User
                                                            ↓
                                                    Download as File
```

## Technology Stack Layers

```
┌──────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  Next.js 14 | TypeScript | Tailwind CSS | Recharts       │
└──────────────────────────────────────────────────────────┘
                            │
                            │ REST API + JWT
                            ▼
┌──────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                      │
│  FastAPI | Pydantic | JWT Auth | CORS                    │
└──────────────────────────────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
                            ▼
┌──────────────────────────────────────────────────────────┐
│                     DATA LAYER                           │
│  PostgreSQL | Time Series Optimized Schema               │
└──────────────────────────────────────────────────────────┘
                            │
                            │ TCP/IP
                            ▼
┌──────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE                         │
│  Docker | Docker Compose | Linux                         │
└──────────────────────────────────────────────────────────┘
```

## Database Schema Relationships

```
┌─────────────┐
│   Factory   │
└──────┬──────┘
       │ 1:N
       ├──────────┬──────────┐
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌────────┐
│   Users  │ │Devices │ │ Alerts │
└──────────┘ └───┬────┘ └────────┘
                 │ 1:N
                 ▼
         ┌───────────────┐
         │SensorReadings │
         │(Time Series)  │
         └───────────────┘
```

## Security Model

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                      │
├─────────────────────────────────────────────────────────┤
│ 1. Network Level                                        │
│    • HTTPS/TLS encryption                               │
│    • VPN for factory networks (production)              │
│    • Firewall rules                                     │
├─────────────────────────────────────────────────────────┤
│ 2. Application Level                                    │
│    • JWT authentication                                 │
│    • Password hashing (bcrypt)                          │
│    • CORS policy                                        │
├─────────────────────────────────────────────────────────┤
│ 3. Data Level                                           │
│    • Role-based access control                          │
│    • Factory-scoped queries                             │
│    • SQL injection prevention (ORM)                     │
├─────────────────────────────────────────────────────────┤
│ 4. Device Level (Future)                                │
│    • Device API keys                                    │
│    • Certificate-based auth                             │
│    • Rate limiting                                      │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architecture (Production)

```
                        ┌───────────────┐
                        │  Load Balancer│
                        │   (Nginx)     │
                        └───────┬───────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
        ┌───────────────┐             ┌───────────────┐
        │   Frontend    │             │   Frontend    │
        │   (Next.js)   │             │   (Next.js)   │
        │   Instance 1  │             │   Instance 2  │
        └───────┬───────┘             └───────┬───────┘
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │  API Gateway    │
                    │   (FastAPI)     │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐   ┌───────────┐
    │  Backend  │    │  Backend  │   │  Backend  │
    │Instance 1 │    │Instance 2 │   │Instance 3 │
    └─────┬─────┘    └─────┬─────┘   └─────┬─────┘
          │                │               │
          └────────────────┼───────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │   PostgreSQL      │
                 │   (Primary)       │
                 └─────────┬─────────┘
                           │
                           │ Replication
                           ▼
                 ┌───────────────────┐
                 │   PostgreSQL      │
                 │   (Replica)       │
                 └───────────────────┘
```
