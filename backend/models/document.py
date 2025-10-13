"""
Document Persistence Models
Store document metadata and processing status in PostgreSQL
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class Document(Base):
    """Document metadata and processing status"""
    
    __tablename__ = "documents"
    
    # Primary key
    id = Column(String(36), primary_key=True)  # UUID
    
    # File information
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, csv
    mime_type = Column(String(100))
    
    # Storage information
    storage_path = Column(String(500))  # MinIO path
    storage_bucket = Column(String(100))
    
    # Content
    content_preview = Column(Text)  # First 500 chars
    full_content_hash = Column(String(64))  # SHA256
    
    # Processing status
    status = Column(String(20), default="pending", index=True)
    # pending, processing, completed, failed
    
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)
    
    # RAG information
    qdrant_collection = Column(String(100))
    qdrant_namespace = Column(String(100), index=True)
    chunks_count = Column(Integer, default=0)
    vectors_count = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSON)  # Flexible metadata storage
    # {
    #   "country": "CA",
    #   "province": "QC",
    #   "year": 2024,
    #   "document_type": "tax_return",
    #   "language": "fr",
    #   "tags": ["fiscal", "t1"],
    #   "custom_fields": {...}
    # }
    
    # Agent assignments
    assigned_agents = Column(JSON)  # List of agent IDs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User/tenant (for multi-tenancy)
    user_id = Column(String(36), index=True)
    tenant_id = Column(String(36), index=True)
    
    # Flags
    is_deleted = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "status": self.status,
            "chunks_count": self.chunks_count,
            "vectors_count": self.vectors_count,
            "metadata": self.metadata or {},
            "assigned_agents": self.assigned_agents or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            "is_deleted": self.is_deleted,
            "is_archived": self.is_archived
        }


class QueryHistory(Base):
    """Query history for analytics and audit"""
    
    __tablename__ = "query_history"
    
    id = Column(String(36), primary_key=True)
    
    # Query information
    query_text = Column(Text, nullable=False)
    query_language = Column(String(10))  # fr, en
    query_jurisdiction = Column(String(20))  # CA, CA-QC, FR, US
    
    # Agent information
    agent_name = Column(String(100), index=True)
    agent_type = Column(String(50))  # static, dynamic, custom
    
    # Response information
    response_text = Column(Text)
    response_tokens = Column(Integer)
    response_time_ms = Column(Float)  # milliseconds
    
    # Model information
    model_used = Column(String(100))
    model_provider = Column(String(50))  # openrouter, local
    
    # RAG information
    sources_count = Column(Integer, default=0)
    sources_documents = Column(JSON)  # List of document IDs
    
    # User/tenant
    user_id = Column(String(36), index=True)
    tenant_id = Column(String(36), index=True)
    
    # Success/failure
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "query_text": self.query_text,
            "agent_name": self.agent_name,
            "model_used": self.model_used,
            "response_tokens": self.response_tokens,
            "response_time_ms": self.response_time_ms,
            "sources_count": self.sources_count,
            "success": self.success,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProcessingJob(Base):
    """Background processing jobs tracking"""
    
    __tablename__ = "processing_jobs"
    
    id = Column(String(36), primary_key=True)
    
    # Job information
    job_type = Column(String(50), nullable=False, index=True)
    # document_ingestion, batch_processing, reindexing
    
    document_id = Column(String(36), index=True)
    
    # Status
    status = Column(String(20), default="pending", index=True)
    # pending, running, completed, failed, cancelled
    
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Results
    result_data = Column(JSON)
    error_message = Column(Text)
    
    # Worker information
    worker_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "document_id": self.document_id,
            "status": self.status,
            "progress": self.progress,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

