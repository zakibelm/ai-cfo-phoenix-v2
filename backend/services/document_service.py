"""
Document Persistence Service
Manages document storage in PostgreSQL with full CRUD operations
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.document import Document, QueryHistory, ProcessingJob
from core.database import get_db

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document persistence and retrieval"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(
        self,
        filename: str,
        file_size: int,
        file_type: str,
        content_preview: str,
        content_hash: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Document:
        """Create a new document record"""
        
        doc_id = str(uuid.uuid4())
        
        document = Document(
            id=doc_id,
            filename=filename,
            original_filename=filename,
            file_size=file_size,
            file_type=file_type,
            content_preview=content_preview[:500],
            full_content_hash=content_hash,
            metadata=metadata or {},
            user_id=user_id,
            tenant_id=tenant_id,
            status="pending"
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Created document {doc_id}: {filename}")
        return document
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(
            and_(
                Document.id == document_id,
                Document.is_deleted == False
            )
        ).first()
    
    def list_documents(
        self,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """List documents with filters"""
        
        query = self.db.query(Document).filter(Document.is_deleted == False)
        
        if user_id:
            query = query.filter(Document.user_id == user_id)
        
        if tenant_id:
            query = query.filter(Document.tenant_id == tenant_id)
        
        if status:
            query = query.filter(Document.status == status)
        
        if file_type:
            query = query.filter(Document.file_type == file_type)
        
        return query.order_by(Document.created_at.desc()).limit(limit).offset(offset).all()
    
    def update_document_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """Update document processing status"""
        
        document = self.get_document(document_id)
        if not document:
            return None
        
        document.status = status
        document.updated_at = datetime.utcnow()
        
        if status == "processing":
            document.processing_started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            document.processing_completed_at = datetime.utcnow()
        
        if error_message:
            document.processing_error = error_message
        
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Updated document {document_id} status to {status}")
        return document
    
    def update_document_rag_info(
        self,
        document_id: str,
        qdrant_collection: str,
        qdrant_namespace: str,
        chunks_count: int,
        vectors_count: int
    ) -> Optional[Document]:
        """Update document RAG processing information"""
        
        document = self.get_document(document_id)
        if not document:
            return None
        
        document.qdrant_collection = qdrant_collection
        document.qdrant_namespace = qdrant_namespace
        document.chunks_count = chunks_count
        document.vectors_count = vectors_count
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Updated RAG info for document {document_id}: {chunks_count} chunks, {vectors_count} vectors")
        return document
    
    def assign_agents(
        self,
        document_id: str,
        agent_ids: List[str]
    ) -> Optional[Document]:
        """Assign agents to document"""
        
        document = self.get_document(document_id)
        if not document:
            return None
        
        document.assigned_agents = agent_ids
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Assigned {len(agent_ids)} agents to document {document_id}")
        return document
    
    def delete_document(self, document_id: str, soft: bool = True) -> bool:
        """Delete document (soft or hard)"""
        
        document = self.get_document(document_id)
        if not document:
            return False
        
        if soft:
            document.is_deleted = True
            document.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Soft deleted document {document_id}")
        else:
            self.db.delete(document)
            self.db.commit()
            logger.info(f"Hard deleted document {document_id}")
        
        return True
    
    def search_documents(
        self,
        search_text: str,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Document]:
        """Search documents by text and metadata"""
        
        query = self.db.query(Document).filter(Document.is_deleted == False)
        
        # Text search in filename and content preview
        if search_text:
            search_pattern = f"%{search_text}%"
            query = query.filter(
                or_(
                    Document.filename.ilike(search_pattern),
                    Document.content_preview.ilike(search_pattern)
                )
            )
        
        # Metadata filters (simplified - for production use JSONB queries)
        if metadata_filters:
            for key, value in metadata_filters.items():
                # This is a simplified version
                # In production, use PostgreSQL JSONB operators
                pass
        
        return query.order_by(Document.created_at.desc()).limit(limit).all()
    
    def get_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get document statistics"""
        
        query = self.db.query(Document).filter(Document.is_deleted == False)
        
        if user_id:
            query = query.filter(Document.user_id == user_id)
        
        total = query.count()
        pending = query.filter(Document.status == "pending").count()
        processing = query.filter(Document.status == "processing").count()
        completed = query.filter(Document.status == "completed").count()
        failed = query.filter(Document.status == "failed").count()
        
        return {
            "total_documents": total,
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0
        }


class QueryHistoryService:
    """Service for query history tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_query(
        self,
        query_text: str,
        agent_name: str,
        model_used: str,
        response_text: str,
        response_tokens: int,
        response_time_ms: float,
        sources_count: int = 0,
        sources_documents: Optional[List[str]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> QueryHistory:
        """Log a query for analytics"""
        
        query_id = str(uuid.uuid4())
        
        query_record = QueryHistory(
            id=query_id,
            query_text=query_text,
            agent_name=agent_name,
            model_used=model_used,
            response_text=response_text[:1000],  # Truncate
            response_tokens=response_tokens,
            response_time_ms=response_time_ms,
            sources_count=sources_count,
            sources_documents=sources_documents or [],
            success=success,
            error_message=error_message,
            user_id=user_id
        )
        
        self.db.add(query_record)
        self.db.commit()
        
        logger.info(f"Logged query {query_id} for agent {agent_name}")
        return query_record
    
    def get_recent_queries(self, limit: int = 50, user_id: Optional[str] = None) -> List[QueryHistory]:
        """Get recent queries"""
        
        query = self.db.query(QueryHistory)
        
        if user_id:
            query = query.filter(QueryHistory.user_id == user_id)
        
        return query.order_by(QueryHistory.created_at.desc()).limit(limit).all()
    
    def get_agent_statistics(self, agent_name: str) -> Dict[str, Any]:
        """Get statistics for a specific agent"""
        
        queries = self.db.query(QueryHistory).filter(
            QueryHistory.agent_name == agent_name
        ).all()
        
        if not queries:
            return {"total_queries": 0}
        
        total = len(queries)
        successful = sum(1 for q in queries if q.success)
        avg_response_time = sum(q.response_time_ms for q in queries if q.response_time_ms) / total
        total_tokens = sum(q.response_tokens for q in queries if q.response_tokens)
        
        return {
            "total_queries": total,
            "successful_queries": successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "avg_response_time_ms": avg_response_time,
            "total_tokens_used": total_tokens
        }


# Helper functions for dependency injection
def get_document_service(db: Session = None) -> DocumentService:
    """Get document service instance"""
    if db is None:
        db = next(get_db())
    return DocumentService(db)


def get_query_history_service(db: Session = None) -> QueryHistoryService:
    """Get query history service instance"""
    if db is None:
        db = next(get_db())
    return QueryHistoryService(db)

