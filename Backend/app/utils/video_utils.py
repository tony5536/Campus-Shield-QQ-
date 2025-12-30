"""
Utilities for video handling: clip creation, storage path helpers.
These are placeholders; replace with real ffmpeg logic on the edge service.
"""
import os

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage", "clips"))

def ensure_storage():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    return STORAGE_DIR

def build_clip_path(camera_id: int, timestamp: str) -> str:
    ensure_storage()
    filename = f"camera_{camera_id}_{timestamp}.mp4"
    return os.path.join(STORAGE_DIR, filename)