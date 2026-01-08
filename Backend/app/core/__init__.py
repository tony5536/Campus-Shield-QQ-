"""Core modules for CampusShield AI."""
from .config import settings
from .security import (
    get_db,
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    authenticate_user,
)

__all__ = [
    "settings",
    "get_db",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "authenticate_user",
]

