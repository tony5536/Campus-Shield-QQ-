"""
One-off helper to create an initial admin user in the DB.
Run: .venv\Scripts\Activate.ps1 ; python backend\app\scripts\create_admin.py
"""
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust sys.path to allow direct script run
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..")))

from ..utils.security import get_password_hash
from ..models.user import User
from ..config.settings import settings as cfg

engine = create_engine(cfg.database_url, connect_args={"check_same_thread": False} if "sqlite" in cfg.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from ..models.base import Base
Base.metadata.create_all(bind=engine)

def create_user(username: str, password: str, role: str = "admin"):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            print(f"User '{username}' already exists.")
            return
        user = User(username=username, password_hash=get_password_hash(password), role=role)
        db.add(user)
        db.commit()
        print(f"Created user: {username} (role={role})")
    finally:
        db.close()

if __name__ == "__main__":
    create_user("admin", "adminpass123", role="admin")