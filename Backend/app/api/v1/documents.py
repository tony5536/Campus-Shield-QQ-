"""
Document Upload & Indexing API - Phase 3
Handles document uploads and RAG indexing.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import aiofiles

from ...core.security import get_db
from ...ai.rag.indexer import DocumentIndexer
from ...core.config import settings
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize indexer
indexer = DocumentIndexer()

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class IndexStatusResponse(BaseModel):
    """Response model for indexing status."""
    document_id: str
    status: str
    chunks_indexed: int
    message: str


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and index a document (PDF, TXT, DOCX).
    
    The document will be:
    - Stored securely
    - Chunked intelligently
    - Embedded and indexed for RAG retrieval
    """
    try:
        # Validate file type
        allowed_extensions = {".pdf", ".txt", ".docx", ".doc"}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Index document
        metadata = {
            "uploaded_at": datetime.utcnow().isoformat(),
            "original_filename": file.filename,
            "file_size": len(content)
        }
        
        doc_ids = indexer.index_file(file_path, metadata)
        
        return {
            "status": "success",
            "document_id": doc_ids[0] if doc_ids else None,
            "chunks_indexed": len(doc_ids),
            "filename": file.filename,
            "message": f"Document indexed successfully with {len(doc_ids)} chunks"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.post("/index-incident")
async def index_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """Index an existing incident for RAG retrieval."""
    from ...models.incident import Incident
    
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident_data = {
        "id": incident.id,
        "incident_type": incident.incident_type,
        "severity": incident.severity,
        "location": incident.location,
        "description": incident.description,
        "timestamp": incident.timestamp.isoformat() if incident.timestamp else None,
    }
    
    doc_id = indexer.index_incident(incident_data)
    
    return {
        "status": "success",
        "incident_id": incident.id,
        "document_id": doc_id,
        "message": "Incident indexed successfully"
    }

