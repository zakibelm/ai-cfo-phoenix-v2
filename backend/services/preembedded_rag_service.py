"""
Pre-embedded RAG Service - Direct use of pre-computed embeddings
Utilise directement les fichiers JSON avec embeddings déjà calculés
Supprime le traitement d'embedding avec LlamaIndex
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from core.config import settings

logger = logging.getLogger(__name__)


class PreEmbeddedRAGService:
    """
    Service RAG optimisé pour utiliser directement des embeddings pré-calculés
    
    Avantages:
    - Pas de recalcul d'embeddings (gain de temps et ressources)
    - Utilisation directe des fichiers JSON embedded
    - Chargement rapide dans Qdrant
    - Pas de dépendance à LlamaIndex pour l'embedding
    """
    
    # Configuration
    VECTOR_SIZE = 768  # Taille des vecteurs (détectée: 768 dimensions)
    
    def __init__(self):
        """Initialize pre-embedded RAG service"""
        
        # Qdrant client
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        
        logger.info("PreEmbeddedRAGService initialized (no embedding model needed)")
    
    def _ensure_collection(self, collection_name: str, vector_size: int = None):
        """
        Ensure Qdrant collection exists
        
        Args:
            collection_name: Collection name
            vector_size: Vector dimension size
        """
        vector_size = vector_size or self.VECTOR_SIZE
        
        try:
            self.qdrant_client.get_collection(collection_name)
            logger.debug(f"Collection {collection_name} already exists")
        except:
            # Create collection
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {collection_name} with vector size {vector_size}")
    
    def load_preembedded_json(
        self,
        json_path: str,
        document_id: str = None,
        metadata: Dict[str, Any] = None,
        collection_name: str = "documents"
    ) -> Dict[str, Any]:
        """
        Load pre-embedded JSON file directly into Qdrant
        
        Args:
            json_path: Path to JSON file with embedded vectors
            document_id: Unique document ID (auto-generated from file if not provided)
            metadata: Additional metadata
            collection_name: Qdrant collection name
        
        Returns:
            Loading result with statistics
        """
        start_time = datetime.now()
        
        try:
            # Load JSON file
            logger.info(f"Loading pre-embedded JSON: {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract data
            file_id = data.get('id', '')
            file_name = data.get('name', Path(json_path).name)
            file_size = data.get('size', 0)
            created_at = data.get('createdAt', '')
            chunks = data.get('chunks', [])
            vectors = data.get('vectors', [])
            
            # Validate data
            if not chunks or not vectors:
                raise ValueError(f"Invalid JSON format: missing chunks or vectors")
            
            if len(chunks) != len(vectors):
                raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(vectors)} vectors")
            
            # Detect vector size
            vector_size = len(vectors[0]) if vectors else self.VECTOR_SIZE
            logger.info(f"Detected vector size: {vector_size}")
            
            # Ensure collection exists
            self._ensure_collection(collection_name, vector_size)
            
            # Generate document ID if not provided
            if not document_id:
                document_id = file_id or hashlib.md5(file_name.encode()).hexdigest()
            
            # Prepare metadata
            enhanced_metadata = {
                **(metadata or {}),
                "document_id": document_id,
                "filename": file_name,
                "file_size": file_size,
                "created_at": created_at,
                "total_chunks": len(chunks),
                "vector_size": vector_size,
                "ingestion_date": datetime.now().isoformat(),
                "source": "pre_embedded"
            }
            
            # Prepare points for Qdrant
            points = []
            for idx, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
                point_id = hashlib.md5(
                    f"{document_id}_{idx}".encode()
                ).hexdigest()
                
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": chunk_text,
                        "chunk_index": idx,
                        **enhanced_metadata
                    }
                )
                points.append(point)
            
            # Upload to Qdrant in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.qdrant_client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                logger.debug(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            
            # Calculate statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "document_id": document_id,
                "filename": file_name,
                "file_size": file_size,
                "total_chunks": len(chunks),
                "total_vectors": len(vectors),
                "vector_size": vector_size,
                "processing_time_seconds": round(processing_time, 2),
                "collection": collection_name,
                "source": "pre_embedded"
            }
            
            logger.info(f"Pre-embedded document loaded successfully: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load pre-embedded JSON {json_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id or "unknown"
            }
    
    def load_preembedded_directory(
        self,
        directory_path: str,
        collection_name: str = "documents",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Load all pre-embedded JSON files from a directory
        
        Args:
            directory_path: Path to directory containing JSON files
            collection_name: Qdrant collection name
            metadata: Common metadata for all documents
        
        Returns:
            Summary of loading results
        """
        start_time = datetime.now()
        
        try:
            directory = Path(directory_path)
            json_files = list(directory.glob("*.json"))
            
            logger.info(f"Found {len(json_files)} JSON files in {directory_path}")
            
            results = []
            success_count = 0
            error_count = 0
            
            for json_file in json_files:
                result = self.load_preembedded_json(
                    json_path=str(json_file),
                    metadata=metadata,
                    collection_name=collection_name
                )
                
                results.append(result)
                
                if result.get("success"):
                    success_count += 1
                else:
                    error_count += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            summary = {
                "success": True,
                "total_files": len(json_files),
                "success_count": success_count,
                "error_count": error_count,
                "processing_time_seconds": round(processing_time, 2),
                "collection": collection_name,
                "results": results
            }
            
            logger.info(f"Directory loading complete: {success_count}/{len(json_files)} successful")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to load directory {directory_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def query(
        self,
        query_vector: List[float],
        collection_name: str = "documents",
        top_k: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Query using pre-computed query vector
        
        Args:
            query_vector: Pre-computed query embedding vector
            collection_name: Qdrant collection name
            top_k: Number of results
            filters: Optional filters (country, province, year, etc.)
        
        Returns:
            Search results
        """
        try:
            # Build filter if provided
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k
            )
            
            # Format results
            results = [
                {
                    "text": hit.payload.get("text"),
                    "score": hit.score,
                    "document_id": hit.payload.get("document_id"),
                    "filename": hit.payload.get("filename"),
                    "chunk_index": hit.payload.get("chunk_index"),
                    "metadata": {k: v for k, v in hit.payload.items() 
                               if k not in ["text", "document_id", "filename", "chunk_index"]}
                }
                for hit in search_results
            ]
            
            logger.info(f"Query returned {len(results)} results from {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return []
    
    def get_collection_info(self, collection_name: str = "documents") -> Dict[str, Any]:
        """
        Get information about a collection
        
        Args:
            collection_name: Collection name
        
        Returns:
            Collection information
        """
        try:
            collection = self.qdrant_client.get_collection(collection_name)
            
            return {
                "name": collection_name,
                "vectors_count": collection.vectors_count,
                "points_count": collection.points_count,
                "status": collection.status,
                "config": {
                    "vector_size": collection.config.params.vectors.size,
                    "distance": collection.config.params.vectors.distance
                }
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return {
                "error": str(e)
            }


# Global instance
preembedded_rag_service = PreEmbeddedRAGService()


'''
    def list_documents(self, collection_name: str = "documents") -> List[Dict[str, Any]]:
        """List all unique documents in a collection."""
        try:
            response = self.qdrant_client.scroll(
                collection_name=collection_name,
                limit=10000,  # Assuming max 10k points, for real app might need pagination
                with_payload=True,
                with_vectors=False
            )
            
            documents = {}
            for point in response[0]:
                doc_id = point.payload.get("document_id")
                if doc_id and doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": point.payload.get("filename", "N/A"),
                        "file_size": point.payload.get("file_size", 0),
                        "total_chunks": point.payload.get("total_chunks", 0),
                        "created_at": point.payload.get("created_at") or point.payload.get("ingestion_date"),
                    }
            
            logger.info(f"Found {len(documents)} unique documents in {collection_name}")
            return list(documents.values())

        except Exception as e:
            # If collection not found, return empty list
            logger.warning(f"Could not list documents from {collection_name}: {str(e)}")
            return []

    def delete_document(self, collection_name: str, document_id: str) -> Dict[str, Any]:
        """Delete all vectors associated with a document_id."""
        try:
            result = self.qdrant_client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            
            logger.info(f"Deletion task for document {document_id} in {collection_name} finished. Result: {result.status}")
            return {"success": True, "document_id": document_id, "status": result.status}
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return {"success": False, "error": str(e)}
'''


    def get_document_chunks(self, collection_name: str, document_id: str) -> List[str]:
        """Retrieve all text chunks for a specific document."""
        try:
            response = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                ),
                limit=10000, # Assuming max 10k chunks per doc
                with_payload=True,
                with_vectors=False
            )
            
            points = response[0]
            # Sort by chunk_index to ensure correct order
            points.sort(key=lambda p: p.payload.get("chunk_index", 0))
            
            chunks = [point.payload.get("text", "") for point in points]
            logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
            return chunks

        except Exception as e:
            logger.error(f"Could not retrieve chunks for document {document_id}: {str(e)}")
            return []

