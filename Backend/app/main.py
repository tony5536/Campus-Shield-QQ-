"""
FastAPI application entrypoint with comprehensive startup checks.

Features:
- Strict configuration validation
- Startup health checks
- Graceful service degradation
- Detailed logging of all services
- CORS, WebSocket, LLM integration
"""

import logging
import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config.settings import settings
from .core.logging import setup_logger, log_startup_info
from .services.notification_service import NotificationManager
from .services.langchain_service import get_langchain_service

# Runtime labels and feature flags
env_label = settings.environment
is_production = settings.is_production

# Initialize LangChain service early so we can report status
langchain_service = get_langchain_service()
llm_available = bool(langchain_service.is_available and settings.enable_llm)

# ------------------------------------------------------------------
# Initialize Logging FIRST
# ------------------------------------------------------------------

logger = setup_logger(
    name="campusshield.main",
    level=settings.log_level,
    log_file=settings.log_file or "logs/campusshield.log"
)

# ------------------------------------------------------------------
# Validate Settings
# ------------------------------------------------------------------

startup_checks = settings.validate_startup()

logger.info("=" * 80)
logger.info("CAMPUSSHIELD AI - BACKEND STARTUP")
logger.info("=" * 80)
logger.info(f"Environment: {settings.environment}")
logger.info(f"Version: {settings.version}")
logger.info(f"Debug: {settings.debug}")
logger.info(f"LLM Enabled: {settings.enable_llm}")
logger.info(f"RAG Enabled: {settings.enable_rag}")
logger.info(f"WebSocket Enabled: {settings.enable_websocket}")

for check, passed in startup_checks.items():
    status = "[OK]" if passed else "[FAIL]"
    logger.info(f"{status} {check}")

logger.info("=" * 80)

# ------------------------------------------------------------------
# FastAPI App Initialization
# ------------------------------------------------------------------

app = FastAPI(
    title="CampusShield AI - Backend",
    description="AI-Powered Campus Security Intelligence Platform",
    version=settings.version,
    debug=settings.debug,
    # Swagger only in development
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
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

# Legacy routes (backward compatibility)
try:
    from .api.routes import auth, cameras, incidents, alerts, ai, llm
except Exception:
    auth = cameras = incidents = alerts = ai = llm = None

for module, prefix, tag in [
    (auth, "/api/auth", "auth"),
    (cameras, "/api/cameras", "cameras"),
    (incidents, "/api/incidents", "incidents"),
    (alerts, "/api/alerts", "alerts"),
    (ai, "/api/ai", "ai"),
]:
    if module is not None and hasattr(module, "router"):
        try:
            app.include_router(module.router, prefix=prefix, tags=[tag])
        except Exception as e:
            logger.warning(f"Failed to include router {module}: {e}")

# New v1 API routes (clean architecture)
try:
    from .api.v1 import incidents as v1_incidents, alerts as v1_alerts, ai as v1_ai, intelligence, forecasting, documents, dashboard
except Exception:
    v1_incidents = v1_alerts = v1_ai = intelligence = forecasting = documents = dashboard = None

for module, prefix, tag in [
    (v1_incidents, "/api/v1/incidents", "v1-incidents"),
    (v1_alerts, "/api/v1/alerts", "v1-alerts"),
    (v1_ai, "/api/v1/ai", "v1-ai"),
    (intelligence, "/api/v1/intelligence", "intelligence"),
    (forecasting, "/api/v1/forecast", "forecasting"),
    (documents, "/api/v1/documents", "documents"),
    (dashboard, "/api/v1/dashboard", "dashboard"),
]:
    if module is not None and hasattr(module, "router"):
        try:
            app.include_router(module.router, prefix=prefix, tags=[tag])
        except Exception as e:
            logger.warning(f"Failed to include router {module}: {e}")

# Include advanced LLM routes (always available, returns 503 if LLM unavailable)
if llm is not None and hasattr(llm, "router"):
    try:
        app.include_router(llm.router, tags=["llm"])
    except Exception as e:
        logger.warning(f"Failed to include llm router: {e}")


# ------------------------------------------------------------------
# Health & Status Endpoints
# ------------------------------------------------------------------

@app.get("/", tags=["health"])
async def root():
    """Root endpoint with basic info."""
    return {
        "status": "ok",
        "service": "CampusShield AI Backend",
        "environment": env_label,
        "version": settings.version,
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "CampusShield AI Backend",
        "version": settings.version,
    }


@app.get("/status", tags=["health"])
async def status():
    """
    Detailed status endpoint showing system capabilities.
    """
    langchain_status = langchain_service.status if langchain_service else {}
    
    # Check RAG availability
    rag_available = False
    try:
        from .ai.rag.vector_store import get_vector_store
        get_vector_store()
        rag_available = True
    except Exception:
        rag_available = False
    
    return {
        "status": "ok",
        "service": "CampusShield AI Backend",
        "version": settings.version,
        "environment": env_label,
        "features": {
            "llm": {
                "available": llm_available,
                "langchain_installed": langchain_status.get("langchain_installed", False) if isinstance(langchain_status, dict) else False,
                "model": langchain_status.get("model") if isinstance(langchain_status, dict) else None,
                "error": langchain_status.get("error") if isinstance(langchain_status, dict) else None,
            },
            "rag": {
                "available": rag_available,
            },
            "ml": {
                "available": getattr(settings, "risk_prediction_enabled", False),
            },
        },
        "llm_routes_enabled": True,
    }


# ------------------------------------------------------------------
# Lifecycle Events
# ------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("=" * 60)
    logger.info("Starting CampusShield AI Backend")
    logger.info(f"Environment: {env_label}")
    logger.info(f"Docs enabled: {not is_production}")
    logger.info("-" * 60)
    
    # Log LLM status
    if llm_available:
        logger.info(f"[OK] LLM Service: ENABLED (Model: {settings.openai_model})")
    else:
        logger.warning("[WARN] LLM Service: DISABLED")
        if langchain_service and not langchain_service.status.get("langchain_installed"):
            logger.warning("   Reason: LangChain packages not installed")
        elif not settings.openai_api_key:
            logger.warning("   Reason: OPENAI_API_KEY not configured")
        elif langchain_service:
            logger.warning(f"   Reason: {langchain_service.status.get('error', 'Unknown error')}")
    
    # Log RAG status
    try:
        from .ai.rag.vector_store import get_vector_store
        get_vector_store()
        logger.info("[OK] RAG System: AVAILABLE")
    except Exception as e:
        logger.warning(f"[WARN] RAG System: UNAVAILABLE ({str(e)[:50]})")
    
    # Log ML status
    if getattr(settings, "risk_prediction_enabled", False):
        logger.info("[OK] ML Risk Prediction: ENABLED")
    else:
        logger.info("[INFO] ML Risk Prediction: DISABLED")
    
    logger.info("=" * 60)
    await asyncio.sleep(0)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down CampusShield AI backend...")
    await notifier.shutdown()


# ------------------------------------------------------------------
# WebSocket Endpoint
# ------------------------------------------------------------------

@app.websocket("/ws/alerts")
async def websocket_alerts(ws: WebSocket):
    """WebSocket endpoint for real-time alerts."""
    await notifier.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await notifier.disconnect(ws)
