"""
Incident model stores detected events and metadata.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.types import TypeDecorator
from sqlalchemy.sql import func
import enum
from .base import Base
import logging


class IncidentStatus(str, enum.Enum):
    """Incident status enumeration."""
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"


class IncidentStatusType(TypeDecorator):
    """Custom SQLAlchemy type that safely maps DB strings to `IncidentStatus`.

    This normalizes legacy/invalid values (for example, 'open') to a correct
    `IncidentStatus` member instead of raising LookupError during result
    processing. It stores values as plain strings in the DB.
    """

    impl = String(50)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, IncidentStatus):
            return value.value
        if isinstance(value, str):
            # Accept enum names or values, case-insensitive; normalize known synonyms
            try:
                # Accept direct enum value
                IncidentStatus(value)
                return value
            except ValueError:
                # Accept name (e.g., 'ACTIVE')
                try:
                    return IncidentStatus[value].value
                except KeyError:
                    # Known legacy mapping
                    if value.lower() == "open":
                        logging.getLogger(__name__).warning(
                            "Normalizing legacy incident status 'open' -> 'ACTIVE' when writing to DB"
                        )
                        return IncidentStatus.ACTIVE.value
                    # Try case-insensitive match against values
                    for member in IncidentStatus:
                        if member.value.lower() == value.lower():
                            return member.value
                    # Unknown value: default to ACTIVE but log it
                    logging.getLogger(__name__).warning(
                        "Unknown incident status '%s' when writing to DB; defaulting to ACTIVE",
                        value,
                    )
                    return IncidentStatus.ACTIVE.value
        raise ValueError(f"Unsupported type for IncidentStatus: {type(value)}")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, IncidentStatus):
            return value
        if isinstance(value, str):
            # Try to construct enum from value (value-based)
            try:
                return IncidentStatus(value)
            except ValueError:
                # Try by name
                try:
                    return IncidentStatus[value]
                except KeyError:
                    # Legacy mapping: 'open' -> ACTIVE
                    if value.lower() == "open":
                        logging.getLogger(__name__).warning(
                            "Normalizing legacy incident status 'open' -> 'ACTIVE' from DB"
                        )
                        return IncidentStatus.ACTIVE
                    for member in IncidentStatus:
                        if member.value.lower() == value.lower():
                            return member
                    logging.getLogger(__name__).warning(
                        "Unknown incident status '%s' in DB; defaulting to ACTIVE",
                        value,
                    )
                    return IncidentStatus.ACTIVE
        return value


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, unique=True, nullable=True, index=True)  # External ID from CSV
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    incident_type = Column(String(128), nullable=False, index=True)
    severity = Column(Float, default=0.0, index=True)
    status = Column(IncidentStatusType(), default=IncidentStatus.ACTIVE, nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(String(256), nullable=True, index=True)
    zone = Column(String(256), nullable=True, index=True)
    source = Column(String(128), nullable=True)
    assigned_team = Column(String(128), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)