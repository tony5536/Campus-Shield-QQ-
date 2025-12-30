#!/usr/bin/env python
"""
Load incidents from CSV file into the database.
Run this after initializing the database with: python init_db.py
"""
import csv
import os
from datetime import datetime
from Backend.app.models.base import Base
from Backend.app.models.incident import Incident
from Backend.app.config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def load_incidents_from_csv(csv_path: str):
    """Load incidents from CSV file into the database."""
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at: {csv_path}")
        return
    
    print(f"📂 Loading incidents from: {csv_path}")
    
    incidents_added = 0
    errors = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Parse the timestamp
                    timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                    
                    # Map severity to numeric value (you can adjust this)
                    severity_map = {
                        'Low': 1.0,
                        'Medium': 2.0,
                        'High': 3.0,
                        'Critical': 4.0
                    }
                    severity = severity_map.get(row['severity_expected'], 2.0)
                    
                    # Determine status based on incident type and severity
                    if row['severity_expected'] == 'High' or row['severity_expected'] == 'Critical':
                        status = 'active'
                    else:
                        status = 'resolved'
                    
                    # Create incident object
                    incident = Incident(
                        incident_type=row['incident_type'],
                        severity=severity,
                        description=row['description'],
                        timestamp=timestamp,
                        status=status,
                        location=row.get('location', ''),
                        source=row.get('source', 'Unknown'),
                    )
                    
                    session.add(incident)
                    incidents_added += 1
                    
                except Exception as e:
                    print(f"⚠️  Error processing row {row_num}: {str(e)}")
                    errors += 1
                    continue
        
        # Commit all changes
        session.commit()
        print(f"\n✅ Successfully loaded {incidents_added} incidents into the database!")
        if errors > 0:
            print(f"⚠️  {errors} rows had errors and were skipped.")
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), 'Backend', 'data', 'incidents.csv')
    load_incidents_from_csv(csv_path)
