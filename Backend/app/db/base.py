"""Database base and initialization."""
from sqlalchemy.ext.declarative import declarative_base
from ..core.config import settings
from ..core.security import engine

Base = declarative_base()


def init_db():
    """Initialize database tables."""
    # Import all models to register them with Base
    from ..models import incident, alert, camera, user  # noqa: F401
    Base.metadata.create_all(bind=engine)

