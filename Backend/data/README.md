# CampusShield AI - Incident Dataset

## Overview

This dataset contains synthetic campus safety incidents designed for testing, demonstration, and academic evaluation of the CampusShield AI system. All data is **completely synthetic** and does not contain any real surveillance or personal information.

## Dataset Purpose

- **Testing**: Validate AI analysis and severity classification
- **Demo**: Provide realistic scenarios for hackathon presentations
- **Evaluation**: Support final year project assessment
- **Development**: Test system behavior with varied incident types

## File Structure

**Location**: `Backend/data/incidents.csv`

**Format**: CSV (Comma-separated values)

**Encoding**: UTF-8

## Column Descriptions

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `incident_id` | Integer | Unique identifier for each incident | 1, 2, 3... |
| `incident_type` | String | Category of incident | Fight, Fire, Intrusion, Medical Emergency, Theft, Suspicious Activity, Crowd Gathering |
| `location` | String | Specific building or area | Hostel, Library, Laboratory, Playground, Parking Area, Main Gate, Academic Block |
| `zone` | String | Detailed location within the area | Block A - Ground Floor, Reading Hall - 2nd Floor, Parking Lot B |
| `timestamp` | ISO 8601 | When the incident occurred | 2025-01-27T14:30:00 |
| `source` | String | How the incident was detected | CCTV, Sensor, Manual |
| `severity_expected` | String | Expected severity classification | Low, Medium, High |
| `description` | String | Natural language description of the incident | Detailed human-readable description |

## Incident Types

1. **Fight**: Physical altercations between individuals
2. **Fire**: Fire alarms, smoke detection, fire-related emergencies
3. **Intrusion**: Unauthorized access attempts or security breaches
4. **Medical Emergency**: Health-related incidents requiring medical attention
5. **Theft**: Property theft or break-ins
6. **Suspicious Activity**: Unusual behavior requiring investigation
7. **Crowd Gathering**: Large gatherings that may require monitoring

## Severity Classification

- **High**: Immediate threat to safety, requires urgent response
  - Examples: Fights, Fires, Intrusions, Critical Medical Emergencies
  
- **Medium**: Potential risk, needs monitoring and response
  - Examples: Theft, Suspicious Activity, Non-critical Medical Emergencies
  
- **Low**: Minor concern, routine monitoring
  - Examples: Crowd Gatherings, Minor Suspicious Activity, Low-priority Theft

## Data Sources

- **CCTV**: Camera-based detection (visual monitoring)
- **Sensor**: Automated sensor detection (motion, smoke, access control)
- **Manual**: Human-reported incidents (staff, students, security personnel)

## How This Dataset Feeds into AI Assistant

1. **Incident Detection**: When an incident is detected (via CCTV, Sensor, or Manual report), the system creates an incident record.

2. **AI Analysis**: The incident description is sent to the AI assistant (`/api/ai/assist`) which:
   - Analyzes the natural language description
   - Determines severity (High/Medium/Low)
   - Generates a summary
   - Provides recommended actions

3. **Visual Display**: The AI's severity assessment is displayed with color-coded badges:
   - 🔴 Red: High severity
   - 🟠 Orange: Medium severity
   - 🟢 Green: Low severity

4. **Response Coordination**: Security teams use the AI analysis to prioritize and respond to incidents.

## Usage in Project

### Loading Data into Database

```python
import csv
from datetime import datetime
from Backend.app.models.incident import Incident
from Backend.app.config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load CSV and create incident records
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

with open('Backend/data/incidents.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        incident = Incident(
            incident_type=row['incident_type'],
            location=row['location'],
            description=row['description'],
            severity=row['severity_expected'],
            status='open',
            timestamp=datetime.fromisoformat(row['timestamp'])
        )
        db.add(incident)
    
db.commit()
db.close()
```

### Testing AI Analysis

```python
# Test AI analysis with dataset descriptions
import requests

with open('Backend/data/incidents.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        response = requests.post('http://localhost:8000/api/ai/assist', json={
            'query': row['description']
        })
        analysis = response.json()
        print(f"Expected: {row['severity_expected']}, AI: {analysis['analysis']['severity']}")
```

## Dataset Statistics

- **Total Incidents**: 25
- **Incident Types**: 7 unique types
- **Locations**: 7 main locations
- **Time Range**: Day and night incidents (08:00 - 23:45)
- **Severity Distribution**: 
  - High: ~40%
  - Medium: ~40%
  - Low: ~20%

## Data Quality

✅ **No Duplicates**: Each incident has a unique ID  
✅ **Logical Severity**: Severity matches incident type logically  
✅ **Realistic Descriptions**: Human-readable, contextually appropriate  
✅ **Valid Timestamps**: ISO 8601 format, realistic time distribution  
✅ **Source Variety**: Mix of CCTV, Sensor, and Manual reports  

## Academic Use

This dataset is designed for:
- **Final Year Projects**: Demonstrates realistic data handling
- **Hackathon Demos**: Shows AI capabilities with varied scenarios
- **System Testing**: Validates end-to-end incident processing
- **AI Evaluation**: Tests severity classification accuracy

## Privacy & Ethics

- ✅ **Synthetic Data Only**: No real surveillance footage or personal information
- ✅ **Academic Purpose**: Designed for educational and demonstration use
- ✅ **No Real Identities**: All descriptions are fictional
- ✅ **Ethical Use**: Suitable for public demonstration and evaluation

## Future Enhancements

Potential additions to the dataset:
- More incident types (Vandalism, Equipment Failure, etc.)
- Seasonal variations (exam periods, events)
- Time-based patterns (rush hours, quiet periods)
- Multi-camera incidents
- Resolution status and response times

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Ready for Demo & Testing

