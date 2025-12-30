"""
AI service placeholder: runs simple heuristics or calls external models.
This module returns enrichment data for incidents (mocked).
"""
from typing import Dict

def analyze_clip(clip_path: str) -> Dict:
    """
    Analyze a saved clip and return metadata (mocked).
    Replace with real model inference (YOLO/violence detector).
    """
    # Mocked response example
    return {
        "clip_path": clip_path,
        "detected_objects": ["person", "backpack"],
        "violence_score": 0.12,
        "summary": "Person running, low violence score"
    }