"""
Centralized error handling for CampusShield.

Guarantees:
- All errors are caught and logged
- All responses follow ErrorResponse schema
- No silent failures
- All errors are observable
"""

import logging
import traceback
from typing import Optional, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime

from ..schemas.incident import ErrorResponse

logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class CampusShieldError(Exception):
    """Base exception for all CampusShield errors."""
    
    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class IncidentNotFoundError(CampusShieldError):
    """Incident with given ID not found."""
    
    def __init__(self, incident_id: int):
        super().__init__(
            error="INCIDENT_NOT_FOUND",
            message=f"Incident with ID {incident_id} not found",
            status_code=404,
            details={"incident_id": incident_id}
        )


class ValidationFailedError(CampusShieldError):
    """Request validation failed."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            error="VALIDATION_FAILED",
            message=message,
            status_code=422,
            details=details or {}
        )


class LLMError(CampusShieldError):
    """LLM service error (timeout, API key, etc)."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            error="LLM_ERROR",
            message=message,
            status_code=503,
            details=details or {}
        )


class RAGError(CampusShieldError):
    """RAG pipeline error (vector store, retrieval, etc)."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            error="RAG_ERROR",
            message=message,
            status_code=503,
            details=details or {}
        )


class DatabaseError(CampusShieldError):
    """Database operation error."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            error="DATABASE_ERROR",
            message=message,
            status_code=500,
            details=details or {}
        )


class UnauthorizedError(CampusShieldError):
    """User not authorized."""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            error="UNAUTHORIZED",
            message=message,
            status_code=401
        )


# ============================================================================
# ERROR RESPONSE BUILDERS
# ============================================================================

def error_response(error: CampusShieldError) -> dict:
    """Build error response dict from CampusShieldError."""
    return {
        "error": error.error,
        "message": error.message,
        "status_code": error.status_code,
        "details": error.details if error.details else None
    }


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

async def campusshield_exception_handler(
    request: Request,
    exc: CampusShieldError
) -> JSONResponse:
    """Handle CampusShieldError exceptions."""
    logger.warning(
        f"CampusShield error: {exc.error} - {exc.message}",
        extra={"status_code": exc.status_code, "details": exc.details}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc)
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors from request body."""
    logger.warning(
        f"Request validation error: {len(exc.errors())} error(s)",
        extra={"errors": exc.errors()}
    )
    
    # Extract field errors
    field_errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])  # Skip "body"
        field_errors[field] = error["msg"]
    
    error_obj = ValidationFailedError(
        message="Request validation failed",
        details={"field_errors": field_errors}
    )
    
    return JSONResponse(
        status_code=error_obj.status_code,
        content=error_response(error_obj)
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions (should rarely happen in prod)."""
    logger.error(
        f"Unexpected exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True
    )
    
    # In production, don't expose internal details
    is_production = hasattr(request.app, "state") and getattr(request.app.state, "is_production", False)
    
    if is_production:
        message = "Internal server error"
        details = None
    else:
        message = str(exc)
        details = {"traceback": traceback.format_exc()}
    
    error_obj = CampusShieldError(
        error="INTERNAL_ERROR",
        message=message,
        status_code=500,
        details=details
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response(error_obj)
    )


# ============================================================================
# SETUP ERROR HANDLERS
# ============================================================================

def setup_error_handlers(app: FastAPI) -> None:
    """Register all exception handlers with FastAPI app."""
    app.add_exception_handler(CampusShieldError, campusshield_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers registered successfully")
