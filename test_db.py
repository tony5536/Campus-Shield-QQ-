from Backend.app.core.security import get_db
from Backend.app.models.camera import Camera
from sqlalchemy.orm import Session

# Manually create session
db_gen = get_db()
db = next(db_gen)

try:
    print("Querying cameras...")
    cameras = db.query(Camera).all()
    print(f"Found {len(cameras)} cameras from DB")
except Exception as e:
    print(f"DB Error: {e}")
finally:
    db.close()
