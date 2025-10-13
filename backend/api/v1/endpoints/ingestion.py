import logging
import time
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from models.api_models import UploadResponse, DocumentStatus, AgentType, Document, DocumentListResponse
from services.ingestion_service import IngestionService
from services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
ingestion_service = IngestionService()
rag_service = RAGService()

# In-memory document store (in production, use PostgreSQL)
documents_db: dict = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    files: List[UploadFile] = File(...),
    assigned_agents: str = Form(""),
    doctype: str = Form("Financial Document"),
    country: str = Form("CA"),
    province: str = Form(None),
    year: int = Form(None)
):
    """Upload and process documents"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Process first file (multi-file support can be added)
        file = files[0]
        start_time = time.time()
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Parse assigned agents
        agent_list = []
        if assigned_agents:
            agent_names = [a.strip() for a in assigned_agents.split(",")]
            agent_list = [AgentType(name) for name in agent_names if name]
        
        # Extract text from document
        file_content = await file.read()
        await file.seek(0)
        
        processed = ingestion_service.process_document(file.file, file.filename)
        
        # Prepare metadata
        metadata = {
            "document_id": doc_id,
            "filename": file.filename,
            "doctype": doctype,
            "country": country,
            "province": province,
            "year": year,
            "assigned_agents": [a.value for a in agent_list],
            "uploaded_at": datetime.now().isoformat()
        }
        
        # Ingest into vector database
        # Determine namespace based on agents
        namespace = "default"
        if agent_list:
            # Use first agent's namespace
            agent_namespaces = {
                AgentType.ACCOUNTANT: "finance_accounting",
                AgentType.TAX: "finance_tax",
                AgentType.FORECAST: "finance_forecast",
                AgentType.COMPLIANCE: "finance_compliance",
                AgentType.AUDIT: "finance_audit"
            }
            namespace = agent_namespaces.get(agent_list[0], "default")
        
        rag_result = rag_service.ingest_document(
            document_id=doc_id,
            filename=file.filename,
            content=processed["text"],
            metadata=metadata,
            namespace=namespace
        )
        
        # Store document metadata
        doc = Document(
            id=doc_id,
            name=file.filename,
            status=DocumentStatus.PROCESSED,
            uploaded=datetime.now(),
            assigned_agents=agent_list,
            tags=[doctype, country],
            doctype=doctype,
            country=country,
            province=province,
            year=year,
            size_bytes=processed["size_bytes"],
            chunk_count=rag_result["chunk_count"],
            sha256=processed["sha256"]
        )
        
        documents_db[doc_id] = doc
        
        processing_time = time.time() - start_time
        
        return UploadResponse(
            message="Document processed successfully",
            document_id=doc_id,
            filename=file.filename,
            status=DocumentStatus.PROCESSED,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(page: int = 1, page_size: int = 50):
    """List all documents"""
    try:
        docs = list(documents_db.values())
        total = len(docs)
        
        # Simple pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_docs = docs[start:end]
        
        return DocumentListResponse(
            documents=paginated_docs,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """Get document by ID"""
    try:
        if document_id not in documents_db:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return documents_db[document_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete document"""
    try:
        if document_id not in documents_db:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = documents_db[document_id]
        
        # Delete from vector DB
        # Determine namespace
        namespace = "default"
        if doc.assigned_agents:
            agent_namespaces = {
                AgentType.ACCOUNTANT: "finance_accounting",
                AgentType.TAX: "finance_tax",
                AgentType.FORECAST: "finance_forecast",
                AgentType.COMPLIANCE: "finance_compliance",
                AgentType.AUDIT: "finance_audit"
            }
            namespace = agent_namespaces.get(doc.assigned_agents[0], "default")
        
        rag_service.delete_document(document_id, namespace)
        
        # Delete from memory
        del documents_db[document_id]
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
