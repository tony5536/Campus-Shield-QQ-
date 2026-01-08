"""Normalize legacy/invalid incident status values in the DB.

Run this script once during deployment or manually to update bad rows:

    python Backend/scripts/normalize_incident_status.py

It looks up the application's SQLAlchemy `engine` and runs safe UPDATEs to
replace legacy values like 'open' with 'ACTIVE', and normalizes any other
unknown non-null status values to 'ACTIVE'. It logs changes.
"""
import logging
from sqlalchemy import text

from app.core.security import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED = ("ACTIVE", "RESOLVED")

def run():
    with engine.begin() as conn:
        # Normalize exact legacy string 'open' (case-insensitive)
        result = conn.execute(
            text("UPDATE incidents SET status = 'ACTIVE' WHERE lower(status) = 'open'")
        )
        logger.info("Normalized 'open' -> 'ACTIVE', rows affected: %s", result.rowcount)

        # Normalize any non-null, non-allowed statuses to ACTIVE
        result2 = conn.execute(
            text("UPDATE incidents SET status = 'ACTIVE' WHERE status IS NOT NULL AND status NOT IN (:a, :b)"),
            {"a": ALLOWED[0], "b": ALLOWED[1]},
        )
        logger.info("Normalized unknown statuses -> 'ACTIVE', rows affected: %s", result2.rowcount)

if __name__ == '__main__':
    run()
