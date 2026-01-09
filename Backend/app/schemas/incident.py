"""
CANONICAL DATA CONTRACT FOR INCIDENTS
=====================================
This schema is NON-NEGOTIABLE and IMMUTABLE.
All backend responses and frontend code MUST follow this structure exactly.
No renaming, no field reordering, no silent defaults.

Any deviation MUST go through explicit versioning.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SEVERITY LEVELS - STRICT ENUM
# ============================================================================
SEVERITY_ENUM = Literal["LOW", "MEDIUM", "HIGH"]

def normalize_severity(value: Optional[str]) -> SEVERITY_ENUM:
    """
    Normalize any severity representation to canonical form.
    Returns: "low", "medium", "high"
    Logs warnings for invalid inputs.
    """
    if value is None:
        return "low"
    
    normalized = str(value).strip().upper()
    
    # Map common aliases
    if normalized in ("CRITICAL", "URGENT", "EMERGENCY"):
        return "HIGH"
    if normalized in ("MED", "MODERATE", "WARNING"):
        return "MEDIUM"
    if normalized in ("LOW", "MINOR", "INFO"):
        return "LOW"
    
    # Try numeric interpretation (0-1 scale)
    try:
        num = float(normalized)
        if num >= 0.66:
            return "HIGH"
        if num >= 0.33:
            return "MEDIUM"
        return "LOW"
    except (ValueError, TypeError):
        # Already normalized uppercase check
        if normalized in ("LOW", "MEDIUM", "HIGH"):
            return normalized
            
        logger.warning(
            f"Invalid severity value '{value}' (type={type(value).__name__}). "
            f"Expected one of: LOW, MEDIUM, HIGH. Defaulting to 'LOW'."
        )
        return "LOW"


# ============================================================================
# CANONICAL INCIDENT SCHEMA
# ============================================================================

class IncidentBase(BaseModel):
    """Base incident schema - shared between request/response"""
    incident_type: str = Field(
        ..., 
        min_length=1,
        max_length=255,
        description="Type of incident (e.g., unauthorized_entry, crowd_gathering, fire_alarm)"
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Physical location where incident occurred"
    )
    zone: Optional[str] = Field(
        None,
        max_length=255,
        description="Campus zone/sector (e.g., Building A, North Section)"
    )
    source: Optional[str] = Field(
        None,
        max_length=255,
        description="Detection source (camera_id, sensor_id, user_report, etc)"
    )
    severity: SEVERITY_ENUM = Field(
        default="LOW",
        description="Severity level: LOW | MEDIUM | HIGH"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Detailed incident description"
    )

    @field_validator("severity", mode="before")
    @classmethod
    def validate_severity(cls, v):
        """Normalize severity to canonical form"""
        return normalize_severity(v)

    @field_validator("incident_type", "location")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip leading/trailing whitespace"""
        return v.strip() if v else v


class IncidentCreate(IncidentBase):
    """Request schema for creating incident"""
    pass


class IncidentUpdate(BaseModel):
    """Request schema for updating incident (all fields optional)"""
    incident_type: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    zone: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=255)
    severity: Optional[SEVERITY_ENUM] = None
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[Literal["ACTIVE", "RESOLVED"]] = None

    @field_validator("severity", mode="before")
    @classmethod
    def validate_severity(cls, v):
        if v is None:
            return None
        return normalize_severity(v)

    @field_validator("incident_type", "location")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip leading/trailing whitespace"""
        return v.strip() if v else v


class IncidentResponse(IncidentBase):
    """
    CANONICAL RESPONSE SCHEMA
    Returned by all backend endpoints without exception.
    Frontend MUST expect exactly this structure.
    """
    incident_id: int = Field(..., description="Unique incident ID")
    timestamp: str = Field(
        ...,
        description="ISO 8601 UTC timestamp (e.g., 2025-01-08T14:30:00Z)"
    )
    status: Literal["ACTIVE", "RESOLVED"] = Field(
        default="ACTIVE",
        description="Current incident status"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "incident_id": 42,
                "incident_type": "unauthorized_entry",
                "timestamp": "2025-01-08T14:30:00Z",
                "location": "Building A, 2nd Floor",
                "zone": "North Section",
                "source": "CAM-001",
                "severity": "high",
                "description": "Motion detected at rear entrance after hours",
                "status": "ACTIVE"
            }
        }


class IncidentListResponse(BaseModel):
    """Response for incident list endpoint"""
    total: int = Field(..., ge=0, description="Total incidents matching filter")
    incidents: list[IncidentResponse] = Field(
        default_factory=list,
        description="List of incidents matching query"
    )


class AssistantResponse(BaseModel):
    """
    CANONICAL AI ASSISTANT RESPONSE FORMAT
    Guaranteed structure for all LLM outputs.
    """
    reply: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="AI-generated response (never empty)"
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence score 0-1 (0=uncertain, 1=certain)"
    )
    sources: Optional[list[str]] = Field(
        None,
        description="Optional source references from RAG or knowledge base"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reply": "This incident appears to be an unauthorized entry with high risk to safety...",
                "confidence": 0.92,
                "sources": ["incident_1", "incident_2", "protocol_breach_guide"]
            }
        }


class ErrorResponse(BaseModel):
    """
    CANONICAL ERROR RESPONSE
    All API errors MUST return this format.
    """
    error: str = Field(
        ...,
        description="Error code/type (e.g., INCIDENT_NOT_FOUND, INVALID_REQUEST)"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    status_code: int = Field(
        ...,
        ge=400,
        le=599,
        description="HTTP status code"
    )
    details: Optional[dict] = Field(
        None,
        description="Additional error context (debug info, field errors, etc)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "INCIDENT_NOT_FOUND",
                "message": "Incident with ID 999 not found",
                "status_code": 404,
                "details": None
            }
        }


class HealthResponse(BaseModel):
    """Response for /health endpoint"""
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        description="Overall system health"
    )
    timestamp: str = Field(description="ISO 8601 UTC timestamp")
    services: dict = Field(
        default_factory=dict,
        description="Individual service health status"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-01-08T14:30:00Z",
                "services": {
                    "database": True,
                    "llm": True,
                    "rag": True
                }
            }
        }
