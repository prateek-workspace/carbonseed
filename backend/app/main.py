from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, devices, data, insights, reports, simulator, signals, factories
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Carbonseed API",
    description="IoT SaaS platform for Indian industrial MSMEs",
    version="1.0.0"
)

# CORS middleware for Cloudflare Pages and local development
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    settings.FRONTEND_URL,
]

# Add wildcard for Cloudflare Pages preview deployments
if "pages.dev" in settings.FRONTEND_URL:
    allowed_origins.append("https://*.pages.dev")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.pages\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(factories.router)
app.include_router(devices.router)
app.include_router(data.router)
app.include_router(insights.router)
app.include_router(signals.router)
app.include_router(reports.router)
app.include_router(simulator.router)


@app.get("/")
async def root():
    return {
        "message": "Carbonseed API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
