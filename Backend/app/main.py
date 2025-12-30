"""
FastAPI application entrypoint for CampusShield AI backend.

Features:
- API routers registration
- Environment-based Swagger control
- CORS for frontend (Vercel)
- Health checks for Render
- WebSocket support for live alerts
"""

import asyncio
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import Settings
from .utils.logger import setup_logger
from .services.notification_service import NotificationManager
from .api.routes import auth, cameras, incidents, alerts, ai


# ------------------------------------------------------------------
# Settings & Logger
# ------------------------------------------------------------------

settings = Settings()
logger = setup_logger()

# Use the canonical setting from Settings so behavior is consistent across the app
# `Settings` already parses common env vars (CS_DEBUG, ENV, PYTHON_ENV, etc.)
is_production = settings.is_production
env_label = "production" if is_production else "development"


# ------------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------------

app = FastAPI(
    title="CampusShield AI - Backend",
    description="Smart Campus Safety & Emergency Response System",
    version="0.1.0",

    # Swagger ONLY in development
    docs_url="/docs" if not is_production else None,
    redoc_url="/redoc" if not is_production else None,
    openapi_url="/openapi.json" if not is_production else None,
)


# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Services
# ------------------------------------------------------------------

notifier = NotificationManager()


# ------------------------------------------------------------------
# API Routers
# ------------------------------------------------------------------

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])


# ------------------------------------------------------------------
# Health Endpoints (IMPORTANT for Render)
# ------------------------------------------------------------------

@app.get("/", tags=["health"])
async def root():
    return {
        "status": "ok",
        "service": "CampusShield AI Backend",
        "environment": env_label,
        "version": app.version,
    }


@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "ok",
        "service": "CampusShield AI Backend",
        "version": app.version,
    }


# ------------------------------------------------------------------
# Lifecycle Events
# ------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    # Log raw env vars used for environment detection to aid local debugging
    logger.info(
        f"Starting CampusShield AI backend (env={env_label}) - docs enabled={not is_production}; "
        f"CS_DEBUG={os.environ.get('CS_DEBUG')}, ENV={os.environ.get('ENV')}, PYTHON_ENV={os.environ.get('PYTHON_ENV')}"
    )
    await asyncio.sleep(0)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down CampusShield AI backend...")
    await notifier.shutdown()


# ------------------------------------------------------------------
# WebSocket Endpoint
# ------------------------------------------------------------------

@app.websocket("/ws/alerts")
async def websocket_alerts(ws: WebSocket):
    await notifier.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await notifier.disconnect(ws)
