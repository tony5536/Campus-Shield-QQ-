#!/usr/bin/env python
"""
CSV Incident Data Ingestion Script

Loads incidents from CSV file into the database.
Normalizes severity_expected to severity (High=0.9, Medium=0.6, Low=0.3)
Marks High severity incidents as ACTIVE by default.
"""
import sys
import os
import csv
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import init_db
from app.core.security import SessionLocal
from app.models.incident import Incident, IncidentStatus

# Severity mapping
SEVERITY_MAP = {
    "High": 0.9,
    "Medium": 0.6,
    "Low": 0.3,
}


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO format timestamp string."""
    try:
        # Handle ISO format: 2025-01-27T14:30:00
        return datetime.fromisoformat(timestamp_str.replace("T", " "))
    except ValueError:
        # Try alternative formats
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")


def normalize_severity(severity_str: str) -> float:
    """Convert severity string to numeric value."""
    severity_str = severity_str.strip().capitalize()
    return SEVERITY_MAP.get(severity_str, 0.5)  # Default to medium if unknown


def load_incidents_from_csv(csv_path: str, dry_run: bool = False) -> int:
    """
    Load incidents from CSV file into database.
    
    Args:
        csv_path: Path to CSV file
        dry_run: If True, don't commit to database (default: False)
    
    Returns:
        Number of incidents loaded
    """
    db = SessionLocal()
    loaded_count = 0
    skipped_count = 0
    
    try:
        # Initialize database
        init_db()
        
        csv_path = Path(csv_path)
        if not csv_path.exists():
            print(f"Error: CSV file not found: {csv_path}")
            return 0
        
        print(f"Loading incidents from: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Check if incident already exists by incident_id
                    incident_id = int(row.get('incident_id', '').strip()) if row.get('incident_id') else None
                    
                    if incident_id:
                        existing = db.query(Incident).filter(
                            Incident.incident_id == incident_id
                        ).first()
                        if existing:
                            print(f"  Row {row_num}: Skipping duplicate incident_id={incident_id}")
                            skipped_count += 1
                            continue
                    
                    # Parse and normalize data
                    severity_str = row.get('severity_expected', row.get('severity', 'Medium')).strip()
                    severity = normalize_severity(severity_str)
                    
                    # Determine status: High severity = ACTIVE by default
                    status = IncidentStatus.ACTIVE if severity >= 0.7 else IncidentStatus.RESOLVED
                    
                    # Parse timestamp
                    timestamp_str = row.get('timestamp', '').strip()
                    if not timestamp_str:
                        timestamp = datetime.utcnow()
                    else:
                        timestamp = parse_timestamp(timestamp_str)
                    
                    # Create incident
                    incident = Incident(
                        incident_id=incident_id,
                        incident_type=row.get('incident_type', '').strip(),
                        location=row.get('location', '').strip() or None,
                        zone=row.get('zone', '').strip() or None,
                        timestamp=timestamp,
                        source=row.get('source', '').strip() or None,
                        severity=severity,
                        description=row.get('description', '').strip() or None,
                        status=status,
                        assigned_team=None  # Can be assigned later
                    )
                    
                    db.add(incident)
                    loaded_count += 1
                    
                    if loaded_count % 10 == 0:
                        print(f"  Processed {loaded_count} incidents...")
                
                except Exception as e:
                    print(f"  Row {row_num}: Error processing row - {e}")
                    print(f"    Row data: {row}")
                    skipped_count += 1
                    continue
        
        if not dry_run:
            db.commit()
            print(f"\n✅ Successfully loaded {loaded_count} incidents into database")
        else:
            print(f"\n🔍 Dry run: Would load {loaded_count} incidents (not committed)")
            db.rollback()
        
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} incidents (duplicates or errors)")
        
        return loaded_count
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading incidents: {e}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load incidents from CSV into database")
    parser.add_argument(
        "csv_file",
        nargs="?",
        default="Backend/data/incidents.csv",
        help="Path to CSV file (default: Backend/data/incidents.csv)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without committing to database"
    )
    
    args = parser.parse_args()
    
    count = load_incidents_from_csv(args.csv_file, dry_run=args.dry_run)
    print(f"\nTotal incidents processed: {count}")
    sys.exit(0 if count > 0 else 1)

