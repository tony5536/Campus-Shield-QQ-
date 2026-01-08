"""
Document indexing for RAG system.
Handles document loading, chunking, and embedding.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from .vector_store import get_vector_store, VectorStore
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class DocumentIndexer:
    """Indexes documents for RAG retrieval."""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or get_vector_store()
        self.chunk_size = 500
        self.chunk_overlap = 50
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Start new chunk with overlap
                overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _generate_id(self, text: str, metadata: Dict[str, Any]) -> str:
        """Generate unique ID for document."""
        content = f"{text}{str(metadata)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def index_text(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk: bool = True
    ) -> List[str]:
        """Index a text document."""
        if chunk:
            chunks = self._chunk_text(text)
        else:
            chunks = [text]
        
        ids = []
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            chunk_id = self._generate_id(chunk_text, chunk_metadata)
            ids.append(chunk_id)
        
        self.vector_store.add_documents(
            texts=chunks,
            metadatas=[{
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            } for i in range(len(chunks))],
            ids=ids
        )
        
        logger.info(f"Indexed document with {len(chunks)} chunks")
        return ids
    
    def index_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Index a file (PDF, TXT, DOCX, etc.)."""
        file_path = Path(file_path)
        metadata = metadata or {}
        metadata.update({
            "source": str(file_path),
            "file_type": file_path.suffix,
            "file_name": file_path.name
        })
        
        # Read file based on type
        if file_path.suffix == ".txt":
            text = file_path.read_text(encoding="utf-8")
        elif file_path.suffix == ".pdf":
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = "\n".join([page.extract_text() for page in reader.pages])
            except ImportError:
                raise ImportError("PyPDF2 required for PDF processing")
        elif file_path.suffix in [".docx", ".doc"]:
            try:
                from docx import Document
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                raise ImportError("python-docx required for DOCX processing")
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        return self.index_text(text, metadata)
    
    def index_incident(self, incident_data: Dict[str, Any]) -> str:
        """Index an incident for RAG retrieval."""
        text = f"""
        Incident Type: {incident_data.get('incident_type', 'Unknown')}
        Severity: {incident_data.get('severity', 'Unknown')}
        Location: {incident_data.get('location', 'Unknown')}
        Description: {incident_data.get('description', 'No description')}
        Timestamp: {incident_data.get('timestamp', 'Unknown')}
        """
        
        metadata = {
            "type": "incident",
            "incident_id": incident_data.get("id"),
            "incident_type": incident_data.get("incident_type"),
            "severity": incident_data.get("severity"),
            "location": incident_data.get("location"),
            "timestamp": str(incident_data.get("timestamp", ""))
        }
        
        ids = self.index_text(text, metadata, chunk=False)
        return ids[0] if ids else None

