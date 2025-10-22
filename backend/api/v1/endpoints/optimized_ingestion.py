"""
Optimized Ingestion API Endpoints
High-performance document ingestion for large files (up to 600MB)
"""

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional
import tempfile
import os
from pathlib import Path

from services.optimized_rag_service import optimized_rag_service
from services.monitoring_service import monitoring_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-large")
async def upload_large_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    province: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    document_type: Optional[str] = Form(None),
    assigned_agents: Optional[str] = Form(None),
    async_processing: bool = Form(True)
):
    """
    Upload and ingest large document (up to 600MB)
    
    Features:
    - Parallel processing
    - Streaming for large files
    - Intelligent chunking
    - Batch vectorization
    - Optional async processing
    
    Args:
        file: Document file
        document_id: Unique document ID (auto-generated if not provided)
        country: Country code (CA, FR, US, etc.)
        province: Province/state code (QC, ON, etc.)
        year: Document year
        document_type: Type of document
        assigned_agents: Comma-separated agent IDs
        async_processing: Process in background (recommended for large files)
    
    Returns:
        Upload status and processing info
    """
    try:
        # Validate file size
        file_size = 0
        temp_file_path = None
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            temp_file_path = temp_file.name
            
            # Stream file content
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                temp_file.write(chunk)
                file_size += len(chunk)
                
                # Check size limit
                if file_size > optimized_rag_service.MAX_FILE_SIZE:
                    os.unlink(temp_file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large: {file_size} bytes (max: {optimized_rag_service.MAX_FILE_SIZE})"
                    )
        
        logger.info(f"Received file: {file.filename} ({file_size} bytes)")
        
        # Generate document ID if not provided
        if not document_id:
            import uuid
            document_id = str(uuid.uuid4())
        
        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "file_size": file_size,
            "country": country,
            "province": province,
            "year": year,
            "document_type": document_type or "unknown",
            "assigned_agents": assigned_agents.split(",") if assigned_agents else []
        }
        
        # Determine collection name
        collection_name = "documents"
        if country:
            collection_name = f"documents_{country.lower()}"
            if province:
                collection_name = f"documents_{country.lower()}_{province.lower()}"
        
        if async_processing:
            # Process in background
            background_tasks.add_task(
                _process_document_background,
                temp_file_path,
                document_id,
                metadata,
                collection_name
            )
            
            return {
                "success": True,
                "message": "Document uploaded successfully. Processing in background.",
                "document_id": document_id,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "async": True,
                "status": "processing"
            }
        else:
            # Process synchronously
            result = optimized_rag_service.ingest_document(
                file_path=temp_file_path,
                document_id=document_id,
                metadata=metadata,
                collection_name=collection_name
            )
            
            # Cleanup temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            # Track metrics
            if result.get("success"):
                monitoring_service.record_request(
                    agent_id="IngestionService",
                    success=True,
                    response_time=result.get("processing_time_seconds", 0)
                )
            
            return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        
        # Cleanup temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))


def _process_document_background(
    file_path: str,
    document_id: str,
    metadata: dict,
    collection_name: str
):
    """
    Background task for document processing
    
    Args:
        file_path: Path to temporary file
        document_id: Document ID
        metadata: Document metadata
        collection_name: Qdrant collection name
    """
    try:
        logger.info(f"Background processing started for document {document_id}")
        
        result = optimized_rag_service.ingest_document(
            file_path=file_path,
            document_id=document_id,
            metadata=metadata,
            collection_name=collection_name
        )
        
        # Track metrics
        if result.get("success"):
            monitoring_service.record_request(
                agent_id="IngestionService",
                success=True,
                response_time=result.get("processing_time_seconds", 0)
            )
            logger.info(f"Background processing completed for {document_id}: {result}")
        else:
            monitoring_service.record_request(
                agent_id="IngestionService",
                success=False,
                response_time=0
            )
            logger.error(f"Background processing failed for {document_id}: {result}")
        
    except Exception as e:
        logger.error(f"Background processing error for {document_id}: {str(e)}")
        monitoring_service.record_request(
            agent_id="IngestionService",
            success=False,
            response_time=0
        )
    finally:
        # Cleanup temp file
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup temp file {file_path}: {str(e)}")


@router.get("/ingestion-stats")
async def get_ingestion_stats():
    """
    Get ingestion service statistics
    
    Returns:
        Statistics about document ingestion
    """
    try:
        metrics = monitoring_service.get_agent_metrics("IngestionService")
        
        return {
            "service": "OptimizedIngestionService",
            "max_file_size_mb": optimized_rag_service.MAX_FILE_SIZE / (1024 * 1024),
            "chunk_sizes": {
                "small": optimized_rag_service.CHUNK_SIZE_SMALL,
                "medium": optimized_rag_service.CHUNK_SIZE_MEDIUM,
                "large": optimized_rag_service.CHUNK_SIZE_LARGE
            },
            "parallel_processing": {
                "thread_workers": optimized_rag_service.MAX_WORKERS_THREADS,
                "process_workers": optimized_rag_service.MAX_WORKERS_PROCESSES,
                "batch_size": optimized_rag_service.BATCH_SIZE
            },
            "metrics": metrics
        }
    
    except Exception as e:
        logger.error(f"Failed to get ingestion stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-with-reassembly")
async def query_with_reassembly(
    query: str,
    collection_name: str = "documents",
    top_k: int = 10,
    reassemble: bool = True
):
    """
    Query documents with intelligent chunk reassembly
    
    Args:
        query: Search query
        collection_name: Qdrant collection name
        top_k: Number of results
        reassemble: Whether to reassemble adjacent chunks
    
    Returns:
        Query results with reassembled context
    """
    try:
        result = optimized_rag_service.query_with_reassembly(
            query=query,
            collection_name=collection_name,
            top_k=top_k,
            reassemble=reassemble
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
