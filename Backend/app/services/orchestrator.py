"""
Orchestrator service: coordinates AI analysis and incident creation/enrichment.
"""
from typing import Dict

from .ai_service import analyze_clip

def enrich_incident_with_clip(incident_id: int, clip_path: str) -> Dict:
    """
    Run AI pipeline on clip and return enrichment data.
    """
    analysis = analyze_clip(clip_path)
    # enrich persistence could be added here
    return {
        "incident_id": incident_id,
        "analysis": analysis
    }