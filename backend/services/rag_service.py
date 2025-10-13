import hashlib
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SimpleNodeParser
from core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations with Qdrant"""
    
    def __init__(self):
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)
        self.embed_model = SentenceTransformer(settings.EMBED_MODEL)
        self.node_parser = SimpleNodeParser.from_defaults(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.vector_size = self.embed_model.get_sentence_embedding_dimension()
        logger.info(f"RAG Service initialized with embed model: {settings.EMBED_MODEL}")
    
    def _get_collection_name(self, namespace: str = "default") -> str:
        """Get collection name with prefix"""
        return f"{settings.QDRANT_COLLECTION_PREFIX}{namespace}"
    
    def _ensure_collection(self, namespace: str = "default"):
        """Ensure collection exists"""
        collection_name = self._get_collection_name(namespace)
        collections = self.qdrant_client.get_collections().collections
        
        if not any(c.name == collection_name for c in collections):
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {collection_name}")
    
    def _compute_sha256(self, text: str) -> str:
        """Compute SHA256 hash of text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def ingest_document(
        self,
        document_id: str,
        filename: str,
        content: str,
        metadata: Dict[str, Any],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """Ingest document into vector database"""
        try:
            self._ensure_collection(namespace)
            collection_name = self._get_collection_name(namespace)
            
            # Create LlamaIndex document
            doc = LlamaDocument(text=content, metadata=metadata)
            
            # Parse into nodes (chunks)
            nodes = self.node_parser.get_nodes_from_documents([doc])
            
            # Create embeddings and points
            points = []
            for idx, node in enumerate(nodes):
                text = node.get_content()
                embedding = self.embed_model.encode(text).tolist()
                
                point_id = f"{document_id}_{idx}"
                payload = {
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": idx,
                    "text": text,
                    "sha256": self._compute_sha256(text),
                    **metadata
                }
                
                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                ))
            
            # Upload to Qdrant
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Ingested {len(points)} chunks for document {document_id}")
            
            return {
                "document_id": document_id,
                "chunk_count": len(points),
                "namespace": namespace
            }
            
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            raise
    
    def query(
        self,
        query_text: str,
        namespace: str = "default",
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Query vector database"""
        try:
            collection_name = self._get_collection_name(namespace)
            
            # Create query embedding
            query_embedding = self.embed_model.encode(query_text).tolist()
            
            # Build filter if provided
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Search
            results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=top_k
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": {
                        k: v for k, v in result.payload.items()
                        if k not in ["text", "sha256"]
                    }
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying: {str(e)}")
            raise
    
    def delete_document(self, document_id: str, namespace: str = "default"):
        """Delete document from vector database"""
        try:
            collection_name = self._get_collection_name(namespace)
            
            # Delete all points with this document_id
            self.qdrant_client.delete(
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
            
            logger.info(f"Deleted document {document_id} from {namespace}")
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_collection_stats(self, namespace: str = "default") -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection_name = self._get_collection_name(namespace)
            info = self.qdrant_client.get_collection(collection_name)
            
            return {
                "namespace": namespace,
                "vector_count": info.points_count,
                "status": info.status
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"namespace": namespace, "error": str(e)}
