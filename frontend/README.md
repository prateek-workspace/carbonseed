# Carbonseed Frontend

Next.js frontend for Carbonseed industrial IoT platform.

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Set up Environment

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Pages

### Public Homepage (/)
- Explains what Carbonseed does
- Lists problems MSMEs face
- Shows how the system works
- Highlights key benefits
- Industries served
- Compliance readiness

### Login Page (/login)
- Email + password authentication
- No self-signup (access provided after pilot)
- Demo credentials shown for testing

### Dashboard (/dashboard)
- Overview cards (temperature, gas index, vibration, uptime)
- Time-series charts
- Active alerts panel
- Device status monitoring
- Compliance reports download

## Design Principles

**Industrial & Serious**
- Minimal, restrained design
- High information density
- Neutral color palette (charcoal, slate, deep blue)
- No greenwashing visuals
- Professional typography

**Palantir-like aesthetic**
- Clean data visualization
- Clear hierarchy
- Focus on functionality over decoration

## API Integration

Frontend connects to FastAPI backend at `http://localhost:8000`

Key endpoints used:
- `POST /auth/login` - Authentication
- `GET /auth/me` - User info
- `GET /data/latest` - Latest sensor data
- `GET /data/timeseries` - Time series data for charts
- `GET /alerts` - Active alerts
- `GET /devices` - Device list
- `GET /reports/*` - Report generation

## Building for Production

```bash
npm run build
npm start
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts (lightweight)
- **Icons**: Lucide React

## Color Palette

```
Charcoal: #2d3035 - #f6f6f7
Slate: #0f172a - #f8fafc
Deep Blue: #1e3a8a - #eff6ff
```

## Authentication Flow

1. User enters credentials on login page
2. Frontend POSTs to `/auth/login`
3. Backend returns JWT token
4. Token stored in localStorage
5. Token sent in Authorization header for protected routes
6. If token invalid, redirect to login

## Future Enhancements

- Real-time updates via WebSockets
- Advanced filtering and date range selection
- Mobile responsive optimization
- PDF report generation
- Alert acknowledgment from UI
- Device configuration interface
- Multi-language support (Hindi, etc.)
