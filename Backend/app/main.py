"""
FastAPI application entrypoint with comprehensive startup checks.

Features:
- Strict configuration validation
- Startup health checks
- Graceful service degradation
- Detailed logging of all services
- CORS, WebSocket, LLM integration
- RAG (Retrieval-Augmented Generation) support
"""

import logging
import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from .core.config import settings
from .core.logging import setup_logger, log_startup_info
from .services.notification_service import NotificationManager
from .services.langchain_service import get_langchain_service
from .services.rag_service import get_rag_service

# Runtime labels and feature flags
env_label = settings.environment
is_production = settings.is_production

# Initialize services (they handle their own graceful degradation)
langchain_service = get_langchain_service()
rag_service = get_rag_service()
llm_available = bool(langchain_service.is_available and settings.enable_llm)
rag_available = rag_service.is_available and settings.enable_rag

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

# CRITICAL: Validate LLM if enabled
if settings.enable_llm:
    if not settings.openai_api_key:
        logger.critical("CRITICAL ERROR: ENABLE_LLM=true but OPENAI_API_KEY is not set!")
        logger.critical("Set OPENAI_API_KEY in .env file and restart.")
        raise RuntimeError(
            "OPENAI_API_KEY is required when ENABLE_LLM=true. "
            "Set it in your .env file at project root and restart the server."
        )
    logger.info(f"[OK] OPENAI_API_KEY configured, LLM will be enabled with model: {settings.openai_model}")
else:
    logger.info("[INFO] LLM disabled (ENABLE_LLM=false)")

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

# CORS configuration with explicit origin list
cors_origins = settings.cors_origins or [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
logger.info(f"CORS Origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-Total-Count"],
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
    from .api.routes import auth, cameras, incidents, alerts, ai, llm, video, dashboard
except Exception:
    auth = cameras = incidents = alerts = ai = llm = video = dashboard = None

for module, prefix, tag in [
    (auth, "/api/auth", "auth"),
    (cameras, "/api/cameras", "cameras"),
    (incidents, "/api/incidents", "incidents"),
    (alerts, "/api/alerts", "alerts"),
    (ai, "/api/ai", "ai"),
    (video, "/api/video", "video"),
    (dashboard, "/api/dashboard", "dashboard"),
]:
    if module is not None and hasattr(module, "router"):
        try:
            app.include_router(module.router, prefix=prefix, tags=[tag])
        except Exception as e:
            logger.warning(f"Failed to include router {module}: {e}")

# New v1 API routes (clean architecture)
try:
    from .api.v1 import incidents as v1_incidents, alerts as v1_alerts, ai as v1_ai, intelligence, forecasting, documents, dashboard, cameras as v1_cameras
except Exception:
    v1_incidents = v1_alerts = v1_ai = intelligence = forecasting = documents = dashboard = v1_cameras = None

for module, prefix, tag in [
    (v1_incidents, "/api/v1/incidents", "v1-incidents"),
    (v1_alerts, "/api/v1/alerts", "v1-alerts"),
    (v1_ai, "/api/v1/ai", "v1-ai"),
    (intelligence, "/api/v1/intelligence", "intelligence"),
    (forecasting, "/api/v1/forecast", "forecasting"),
    (documents, "/api/v1/documents", "documents"),
    (dashboard, "/api/v1/dashboard", "v1-dashboard"),
    (v1_cameras, "/api/v1/cameras", "v1-cameras"),

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
# Static Files & SPA Support
# ------------------------------------------------------------------

# Mount static files if directory exists (Docker production)
static_dir = "/workspace/static_build"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=f"{static_dir}/static"), name="static")


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
    rag_status = rag_service.status if rag_service else {}
    
    return {
        "status": "ok",
        "service": "CampusShield AI Backend",
        "version": settings.version,
        "environment": env_label,
        "features": {
            "llm": {
                "available": llm_available,
                "enabled": settings.enable_llm,
                "langchain_installed": langchain_status.get("langchain_installed", False) if isinstance(langchain_status, dict) else False,
                "model": langchain_status.get("model") if isinstance(langchain_status, dict) else None,
                "error": langchain_status.get("error") if isinstance(langchain_status, dict) else None,
            },
            "rag": {
                "available": rag_available,
                "enabled": settings.enable_rag,
                "vector_store_type": rag_status.get("vector_store_type") if isinstance(rag_status, dict) else None,
                "error": rag_status.get("error") if isinstance(rag_status, dict) else None,
            },
            "ml": {
                "available": getattr(settings, "risk_prediction_enabled", False),
            },
        },
        "llm_routes_enabled": True,
    }


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    """
    Catch-all route for SPA support.
    Returns index.html for any known path that isn't an API route.
    """
    # Skip API routes (let them 404 naturally if not found)
    if full_path.startswith("api") or full_path.startswith("ws"):
        return JSONResponse({"error": "Not Found"}, status_code=404)
        
    # Serve index.html from static build directory
    if os.path.exists(f"{static_dir}/index.html"):
        return FileResponse(f"{static_dir}/index.html")
    
    # Fallback for local development or missing build
    return JSONResponse(
        {
            "message": "Frontend not ready (index.html not found)",
            "details": f"Checked in {static_dir}"
        }, 
        status_code=404
    )


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
    
    # Log API routes
    logger.info("[OK] Dashboard API: /api/v1/dashboard/metrics (canonical endpoint)")
    logger.info("[OK] Video Streaming: /api/video/stream")
    logger.info("[OK] WebSocket Alerts: /ws/alerts")
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
    if rag_available:
        rag_status = rag_service.status
        logger.info(f"[OK] RAG System: ENABLED (Vector Store: {rag_status.get('vector_store_type', 'unknown')})")
    else:
        if settings.enable_rag:
            logger.warning("[WARN] RAG System: DISABLED")
            if rag_service:
                logger.warning(f"   Reason: {rag_service.status.get('error', 'Unknown error')}")
        else:
            logger.info("[INFO] RAG System: DISABLED (via ENABLE_RAG=False)")
    
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
# WebSocket Endpoints
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


@app.websocket("/ws/video")
async def websocket_video(ws: WebSocket):
    """
    WebSocket endpoint for real-time video streaming.
    Streams frames as base64-encoded JPEG or raw binary.
    
    Client should:
    1. Connect to ws://localhost:8000/ws/video
    2. Receive frames as JSON: {"type": "frame", "data": "base64_data", "timestamp": "..."}
    3. Decode and display frames in real-time
    """
    await ws.accept()
    
    try:
        # Import video simulator
        from .api.routes.video import VideoStreamSimulator
        
        simulator = VideoStreamSimulator()
        
        # Check if enabled
        if not settings.enable_video_stream:
            await ws.send_json({
                "type": "error",
                "message": "Video streaming is disabled"
            })
            await ws.close(code=1000)
            return
        
        # Stream frames continuously
        frame_count = 0
        async for frame_bytes in simulator.stream_frames():
            try:
                # Encode as base64 JSON message
                import base64
                frame_b64 = base64.b64encode(frame_bytes).decode('utf-8')
                
                await ws.send_json({
                    "type": "frame",
                    "data": frame_b64,
                    "timestamp": datetime.utcnow().isoformat(),
                    "frame_number": frame_count
                })
                
                frame_count += 1
                
            except Exception as e:
                logger.error(f"Error sending frame: {e}")
                await ws.send_json({
                    "type": "error",
                    "message": f"Error streaming: {str(e)}"
                })
                break
    
    except Exception as e:
        logger.error(f"WebSocket video error: {e}")
        try:
            await ws.send_json({
                "type": "error",
                "message": f"Video stream error: {str(e)}"
            })
        except:
            pass
    
    finally:
        try:
            await ws.close(code=1000)
        except:
            pass
        logger.info("WebSocket video connection closed")

