"""
Pre-embedded Ingestion API Endpoints
Charge directement les fichiers JSON avec embeddings pré-calculés
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
from pydantic import BaseModel

from services.preembedded_rag_service import preembedded_rag_service
from services.monitoring_service import monitoring_service

logger = logging.getLogger(__name__)

router = APIRouter()


class LoadPreEmbeddedRequest(BaseModel):
    """Request model for loading pre-embedded JSON"""
    json_path: str
    document_id: Optional[str] = None
    collection_name: str = "documents"
    metadata: Optional[Dict[str, Any]] = None


class LoadDirectoryRequest(BaseModel):
    """Request model for loading directory of pre-embedded JSONs"""
    directory_path: str
    collection_name: str = "documents"
    metadata: Optional[Dict[str, Any]] = None


@router.post("/load-json")
async def load_preembedded_json(request: LoadPreEmbeddedRequest):
    """
    Charge un fichier JSON avec embeddings pré-calculés dans Qdrant
    
    Args:
        request: Request with JSON path and metadata
    
    Returns:
        Loading result with statistics
    """
    try:
        logger.info(f"Loading pre-embedded JSON: {request.json_path}")
        
        result = preembedded_rag_service.load_preembedded_json(
            json_path=request.json_path,
            document_id=request.document_id,
            metadata=request.metadata,
            collection_name=request.collection_name
        )
        
        # Track metrics
        if result.get("success"):
            monitoring_service.record_request(
                agent_id="PreEmbeddedIngestionService",
                success=True,
                response_time=result.get("processing_time_seconds", 0)
            )
        else:
            monitoring_service.record_request(
                agent_id="PreEmbeddedIngestionService",
                success=False,
                response_time=0
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to load pre-embedded JSON: {str(e)}")
        monitoring_service.record_request(
            agent_id="PreEmbeddedIngestionService",
            success=False,
            response_time=0
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-directory")
async def load_preembedded_directory(
    request: LoadDirectoryRequest,
    background_tasks: BackgroundTasks = None,
    async_processing: bool = False
):
    """
    Charge tous les fichiers JSON d'un répertoire avec embeddings pré-calculés
    
    Args:
        request: Request with directory path and metadata
        background_tasks: Background tasks handler
        async_processing: Process in background
    
    Returns:
        Loading summary
    """
    try:
        logger.info(f"Loading pre-embedded directory: {request.directory_path}")
        
        if async_processing and background_tasks:
            # Process in background
            background_tasks.add_task(
                _load_directory_background,
                request.directory_path,
                request.collection_name,
                request.metadata
            )
            
            return {
                "success": True,
                "message": "Directory loading started in background",
                "directory": request.directory_path,
                "collection": request.collection_name,
                "async": True
            }
        else:
            # Process synchronously
            result = preembedded_rag_service.load_preembedded_directory(
                directory_path=request.directory_path,
                collection_name=request.collection_name,
                metadata=request.metadata
            )
            
            # Track metrics
            if result.get("success"):
                monitoring_service.record_request(
                    agent_id="PreEmbeddedIngestionService",
                    success=True,
                    response_time=result.get("processing_time_seconds", 0)
                )
            
            return result
    
    except Exception as e:
        logger.error(f"Failed to load directory: {str(e)}")
        monitoring_service.record_request(
            agent_id="PreEmbeddedIngestionService",
            success=False,
            response_time=0
        )
        raise HTTPException(status_code=500, detail=str(e))


def _load_directory_background(
    directory_path: str,
    collection_name: str,
    metadata: Dict[str, Any]
):
    """
    Background task for directory loading
    
    Args:
        directory_path: Path to directory
        collection_name: Qdrant collection name
        metadata: Common metadata
    """
    try:
        logger.info(f"Background loading started for directory {directory_path}")
        
        result = preembedded_rag_service.load_preembedded_directory(
            directory_path=directory_path,
            collection_name=collection_name,
            metadata=metadata
        )
        
        # Track metrics
        if result.get("success"):
            monitoring_service.record_request(
                agent_id="PreEmbeddedIngestionService",
                success=True,
                response_time=result.get("processing_time_seconds", 0)
            )
            logger.info(f"Background loading completed: {result}")
        else:
            monitoring_service.record_request(
                agent_id="PreEmbeddedIngestionService",
                success=False,
                response_time=0
            )
            logger.error(f"Background loading failed: {result}")
    
    except Exception as e:
        logger.error(f"Background loading error: {str(e)}")
        monitoring_service.record_request(
            agent_id="PreEmbeddedIngestionService",
            success=False,
            response_time=0
        )


@router.get("/collection-info/{collection_name}")
async def get_collection_info(collection_name: str = "documents"):
    """
    Obtenir des informations sur une collection Qdrant
    
    Args:
        collection_name: Collection name
    
    Returns:
        Collection information
    """
    try:
        info = preembedded_rag_service.get_collection_info(collection_name)
        
        if "error" in info:
            raise HTTPException(status_code=404, detail=info["error"])
        
        return info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-info")
async def get_service_info():
    """
    Obtenir des informations sur le service d'ingestion pré-embedded
    
    Returns:
        Service information
    """
    try:
        metrics = monitoring_service.get_agent_metrics("PreEmbeddedIngestionService")
        
        return {
            "service": "PreEmbeddedIngestionService",
            "description": "Direct loading of pre-computed embeddings (no re-embedding)",
            "advantages": [
                "No embedding computation needed",
                "Fast loading into Qdrant",
                "No LlamaIndex dependency for embeddings",
                "Reduced CPU/GPU usage",
                "Lower latency"
            ],
            "supported_vector_size": preembedded_rag_service.VECTOR_SIZE,
            "metrics": metrics
        }
    
    except Exception as e:
        logger.error(f"Failed to get service info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


'''
from fastapi.responses import Response

@router.get("/documents/{collection_name}")
async def list_documents(collection_name: str = "documents"):
    """List all unique documents in a collection."""
    try:
        documents = preembedded_rag_service.list_documents(collection_name)
        return {"success": True, "documents": documents}
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{collection_name}/{document_id}")
async def delete_document(collection_name: str, document_id: str):
    """Delete a document and its vectors from a collection."""
    try:
        result = preembedded_rag_service.delete_document(collection_name, document_id)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{collection_name}/{document_id}/download")
async def download_document_content(collection_name: str, document_id: str):
    """Download the full text content of a document by reassembling its chunks."""
    try:
        # Retrieve document metadata to get the original filename
        # This part assumes you have a way to get metadata. We'll use the first chunk's metadata.
        response = preembedded_rag_service.qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]),
            limit=1, with_payload=True
        )
        if not response[0]:
            raise HTTPException(status_code=404, detail="Document not found.")

        metadata = response[0][0].payload
        filename = metadata.get("filename", f"{document_id}.txt")
        # Ensure filename has a .txt extension for text content
        filename = Path(filename).stem + ".txt"

        chunks = preembedded_rag_service.get_document_chunks(collection_name, document_id)
        if not chunks:
            raise HTTPException(status_code=404, detail="Document has no content or does not exist.")

        full_text = "\n\n---\n\n".join(chunks)

        return Response(
            content=full_text,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download document content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
'''
