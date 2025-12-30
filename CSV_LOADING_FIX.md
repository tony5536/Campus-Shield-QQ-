# 🐛 Issues Found & Solutions

## Problem: Dashboard Shows "Failed to load dashboard data. Using demo data."

### Root Cause
Your `incidents.csv` file exists at `Backend/data/incidents.csv` with 25 rows of incident data, but **it was never being loaded into the database**. The system uses SQLAlchemy with a database backend (PostgreSQL/SQLite), and the CSV data needs to be explicitly imported.

### Files Changed
1. **`Backend/app/models/incident.py`** - Added missing fields:
   - `location: String(256)` - Where the incident occurred
   - `source: String(128)` - Source of detection (CCTV, Sensor, Manual)

2. **`load_incidents_from_csv.py`** (NEW) - CSV loader script that:
   - Reads incidents.csv
   - Parses timestamps and severity levels
   - Inserts data into the database
   - Provides error reporting

### How to Fix It

#### Step 1: Reinitialize the Database
```bash
python init_db.py
```
This creates fresh tables with the new fields.

#### Step 2: Load CSV Data into Database
```bash
python load_incidents_from_csv.py
```
Expected output:
```
📂 Loading incidents from: Backend/data/incidents.csv
✅ Successfully loaded 25 incidents into the database!
```

#### Step 3: Restart Your Backend
```bash
# If using Flask/FastAPI directly
python -m Backend.app.main

# Or with uvicorn
uvicorn Backend.app.main:app --reload
```

#### Step 4: Refresh Dashboard
Clear browser cache and refresh `http://localhost:3000` (or your dashboard URL)

---

## What the CSV Loader Does

✅ **Parses CSV columns:**
- `incident_id` → Auto-generated
- `incident_type` → Incident type (Fight, Fire, Intrusion, etc.)
- `location` → Location string
- `zone` → Included in description
- `timestamp` → ISO format datetime
- `source` → Detection source (CCTV/Sensor/Manual)
- `severity_expected` → Converted to numeric (1.0-4.0)
- `description` → Full description

✅ **Smart Status Assignment:**
- High/Critical severity → "active" status
- Low/Medium → "resolved" status

✅ **Error Handling:**
- Reports rows with parsing errors
- Continues loading remaining rows
- Shows summary at end

---

## Verification

After loading, verify data is in the database:

```bash
# For SQLite
sqlite3 your_database.db "SELECT COUNT(*) FROM incidents;"

# For PostgreSQL
psql -d your_db -c "SELECT COUNT(*) FROM incidents;"
```

Should show: `25` incidents loaded.

---

## Automate This in the Future

To automatically load CSV data on startup, add this to `init_db.py`:

```python
# At the end of init_db.py, add:
from load_incidents_from_csv import load_incidents_from_csv
load_incidents_from_csv('Backend/data/incidents.csv')
```

This way, whenever you reinitialize the database, it automatically populates with incident data.
