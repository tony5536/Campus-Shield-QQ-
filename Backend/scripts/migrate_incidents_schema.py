#!/usr/bin/env python
"""
Migration script to update incidents table schema.

Adds new columns: incident_id, zone, assigned_team
Updates status column to use enum.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import engine, SessionLocal
from app.db.base import Base
from sqlalchemy import text

def migrate_schema():
    """Migrate incidents table to new schema."""
    db = SessionLocal()
    
    try:
        print("Migrating incidents table schema...")
        
        # Check if incident_id column exists
        result = db.execute(text("PRAGMA table_info(incidents)"))
        columns = [row[1] for row in result]
        
        # Add new columns if they don't exist
        if 'incident_id' not in columns:
            print("  Adding incident_id column...")
            db.execute(text("ALTER TABLE incidents ADD COLUMN incident_id INTEGER"))
            db.commit()
        
        if 'location' not in columns:
            print("  Adding location column...")
            db.execute(text("ALTER TABLE incidents ADD COLUMN location VARCHAR(256)"))
            db.commit()
        
        if 'zone' not in columns:
            print("  Adding zone column...")
            db.execute(text("ALTER TABLE incidents ADD COLUMN zone VARCHAR(256)"))
            db.commit()
        
        if 'assigned_team' not in columns:
            print("  Adding assigned_team column...")
            db.execute(text("ALTER TABLE incidents ADD COLUMN assigned_team VARCHAR(128)"))
            db.commit()
        
        if 'source' not in columns:
            print("  Adding source column...")
            db.execute(text("ALTER TABLE incidents ADD COLUMN source VARCHAR(128)"))
            db.commit()
        
        # Note: SQLite doesn't support changing column types or adding enums directly
        # The status column will remain as VARCHAR, but we'll use the enum in Python code
        print("  ✅ Schema migration complete!")
        
        # Verify
        result = db.execute(text("PRAGMA table_info(incidents)"))
        columns = [row[1] for row in result]
        print(f"  Current columns: {', '.join(columns)}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_schema()
    print("\n✅ Migration completed successfully!")

