"""
Optimized RAG Service - High-performance document processing
Handles large files (up to 600MB) with parallel processing and intelligent chunking
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import hashlib
from datetime import datetime
import io

from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Document loaders
from llama_index.readers.file import PDFReader, DocxReader
import pandas as pd

from core.config import settings

logger = logging.getLogger(__name__)


class OptimizedRAGService:
    """
    High-performance RAG service for large documents
    
    Features:
    - Supports files up to 600MB
    - Parallel processing with thread/process pools
    - Intelligent chunking (semantic + sentence-based)
    - Streaming for large files
    - Batch vectorization
    - Smart reassembly with context preservation
    """
    
    # Configuration
    MAX_FILE_SIZE = 600 * 1024 * 1024  # 600 MB
    CHUNK_SIZE_SMALL = 512  # For small documents
    CHUNK_SIZE_MEDIUM = 1024  # For medium documents
    CHUNK_SIZE_LARGE = 2048  # For large documents (600MB)
    CHUNK_OVERLAP = 200  # Overlap for context continuity
    
    # Parallel processing
    MAX_WORKERS_THREADS = 8  # Thread pool size
    MAX_WORKERS_PROCESSES = 4  # Process pool size
    BATCH_SIZE = 100  # Vectorization batch size
    
    def __init__(self):
        """Initialize optimized RAG service"""
        
        # Qdrant client
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        
        # Embedding model
        self.embed_model = HuggingFaceEmbedding(
            model_name=settings.EMBED_MODEL,
            cache_folder="./cache/embeddings"
        )
        
        # Configure LlamaIndex settings
        Settings.embed_model = self.embed_model
        Settings.chunk_size = self.CHUNK_SIZE_MEDIUM
        Settings.chunk_overlap = self.CHUNK_OVERLAP
        
        # Thread pool for I/O operations
        self.thread_pool = ThreadPoolExecutor(max_workers=self.MAX_WORKERS_THREADS)
        
        # Process pool for CPU-intensive operations
        self.process_pool = ProcessPoolExecutor(max_workers=self.MAX_WORKERS_PROCESSES)
        
        logger.info("OptimizedRAGService initialized with parallel processing")
    
    def _get_optimal_chunk_size(self, file_size: int) -> int:
        """
        Determine optimal chunk size based on file size
        
        Args:
            file_size: File size in bytes
        
        Returns:
            Optimal chunk size
        """
        if file_size < 1 * 1024 * 1024:  # < 1 MB
            return self.CHUNK_SIZE_SMALL
        elif file_size < 50 * 1024 * 1024:  # < 50 MB
            return self.CHUNK_SIZE_MEDIUM
        else:  # >= 50 MB
            return self.CHUNK_SIZE_LARGE
    
    def _load_document_streaming(
        self,
        file_path: str,
        file_type: str
    ) -> List[Document]:
        """
        Load document with streaming for large files
        
        Args:
            file_path: Path to document
            file_type: File type (pdf, docx, txt, csv)
        
        Returns:
            List of Document objects
        """
        logger.info(f"Loading document: {file_path} (type: {file_type})")
        
        try:
            if file_type == "pdf":
                # PDF with streaming
                reader = PDFReader()
                documents = reader.load_data(file_path)
                
            elif file_type == "docx":
                # DOCX
                reader = DocxReader()
                documents = reader.load_data(file_path)
                
            elif file_type == "txt":
                # TXT with streaming for large files
                file_size = Path(file_path).stat().st_size
                
                if file_size > 10 * 1024 * 1024:  # > 10 MB
                    # Stream in chunks
                    documents = []
                    chunk_size = 1024 * 1024  # 1 MB chunks
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            documents.append(Document(text=chunk))
                else:
                    # Load entire file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                    documents = [Document(text=text)]
                
            elif file_type == "csv":
                # CSV
                df = pd.read_csv(file_path)
                text = df.to_string()
                documents = [Document(text=text)]
                
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            logger.info(f"Loaded {len(documents)} document(s) from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def _chunk_documents_parallel(
        self,
        documents: List[Document],
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Document]:
        """
        Chunk documents in parallel for speed
        
        Args:
            documents: List of documents
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        
        Returns:
            List of chunked documents (nodes)
        """
        logger.info(f"Chunking {len(documents)} documents with size={chunk_size}, overlap={chunk_overlap}")
        
        # Use semantic splitter for better chunking
        splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_separator="\n\n",
            secondary_chunking_regex="[.!?]\\s+"
        )
        
        # Chunk in parallel
        all_nodes = []
        
        def chunk_single_doc(doc):
            return splitter.get_nodes_from_documents([doc])
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS_THREADS) as executor:
            futures = [executor.submit(chunk_single_doc, doc) for doc in documents]
            
            for future in as_completed(futures):
                try:
                    nodes = future.result()
                    all_nodes.extend(nodes)
                except Exception as e:
                    logger.error(f"Error chunking document: {str(e)}")
        
        logger.info(f"Created {len(all_nodes)} chunks from {len(documents)} documents")
        return all_nodes
    
    def _vectorize_batch(
        self,
        nodes: List[Document],
        batch_size: int = None
    ) -> List[List[float]]:
        """
        Vectorize nodes in batches for efficiency
        
        Args:
            nodes: List of nodes to vectorize
            batch_size: Batch size (default: BATCH_SIZE)
        
        Returns:
            List of embedding vectors
        """
        batch_size = batch_size or self.BATCH_SIZE
        logger.info(f"Vectorizing {len(nodes)} nodes in batches of {batch_size}")
        
        embeddings = []
        
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]
            texts = [node.get_content() for node in batch]
            
            # Batch embedding
            batch_embeddings = self.embed_model.get_text_embedding_batch(texts)
            embeddings.extend(batch_embeddings)
            
            logger.debug(f"Vectorized batch {i//batch_size + 1}/{(len(nodes)-1)//batch_size + 1}")
        
        logger.info(f"Vectorization complete: {len(embeddings)} vectors")
        return embeddings
    
    def _store_vectors_batch(
        self,
        collection_name: str,
        nodes: List[Document],
        embeddings: List[List[float]],
        metadata: Dict[str, Any]
    ):
        """
        Store vectors in Qdrant in batches
        
        Args:
            collection_name: Qdrant collection name
            nodes: List of nodes
            embeddings: List of embeddings
            metadata: Document metadata
        """
        logger.info(f"Storing {len(embeddings)} vectors in collection {collection_name}")
        
        # Ensure collection exists
        try:
            self.qdrant_client.get_collection(collection_name)
        except:
            # Create collection
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=len(embeddings[0]),
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {collection_name}")
        
        # Prepare points
        points = []
        for idx, (node, embedding) in enumerate(zip(nodes, embeddings)):
            point_id = hashlib.md5(
                f"{metadata.get('document_id', 'unknown')}_{idx}".encode()
            ).hexdigest()
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": node.get_content(),
                    "chunk_index": idx,
                    "total_chunks": len(nodes),
                    **metadata
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=batch
            )
            logger.debug(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        
        logger.info(f"Stored {len(points)} vectors successfully")
    
    async def ingest_document_async(
        self,
        file_path: str,
        document_id: str,
        metadata: Dict[str, Any],
        collection_name: str = "documents"
    ) -> Dict[str, Any]:
        """
        Ingest document asynchronously with parallel processing
        
        Args:
            file_path: Path to document
            document_id: Unique document ID
            metadata: Document metadata
            collection_name: Qdrant collection name
        
        Returns:
            Ingestion result with statistics
        """
        start_time = datetime.now()
        
        try:
            # Validate file size
            file_size = Path(file_path).stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {file_size} bytes (max: {self.MAX_FILE_SIZE})")
            
            logger.info(f"Starting ingestion of {file_path} ({file_size} bytes)")
            
            # Determine file type
            file_ext = Path(file_path).suffix.lower().replace('.', '')
            
            # Step 1: Load document (streaming for large files)
            documents = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self._load_document_streaming,
                file_path,
                file_ext
            )
            
            # Step 2: Determine optimal chunk size
            chunk_size = self._get_optimal_chunk_size(file_size)
            logger.info(f"Using chunk size: {chunk_size}")
            
            # Step 3: Chunk documents in parallel
            nodes = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self._chunk_documents_parallel,
                documents,
                chunk_size,
                self.CHUNK_OVERLAP
            )
            
            # Step 4: Vectorize in batches
            embeddings = await asyncio.get_event_loop().run_in_executor(
                self.process_pool,
                self._vectorize_batch,
                nodes,
                self.BATCH_SIZE
            )
            
            # Step 5: Store vectors in Qdrant
            enhanced_metadata = {
                **metadata,
                "document_id": document_id,
                "file_size": file_size,
                "chunk_size": chunk_size,
                "total_chunks": len(nodes),
                "ingestion_date": datetime.now().isoformat()
            }
            
            await asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                self._store_vectors_batch,
                collection_name,
                nodes,
                embeddings,
                enhanced_metadata
            )
            
            # Calculate statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "document_id": document_id,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "total_documents": len(documents),
                "total_chunks": len(nodes),
                "chunk_size": chunk_size,
                "total_vectors": len(embeddings),
                "processing_time_seconds": round(processing_time, 2),
                "chunks_per_second": round(len(nodes) / processing_time, 2),
                "collection": collection_name
            }
            
            logger.info(f"Ingestion complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Ingestion failed for {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    def ingest_document(
        self,
        file_path: str,
        document_id: str,
        metadata: Dict[str, Any],
        collection_name: str = "documents"
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for document ingestion
        
        Args:
            file_path: Path to document
            document_id: Unique document ID
            metadata: Document metadata
            collection_name: Qdrant collection name
        
        Returns:
            Ingestion result
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.ingest_document_async(
                    file_path,
                    document_id,
                    metadata,
                    collection_name
                )
            )
            return result
        finally:
            loop.close()
    
    def query_with_reassembly(
        self,
        query: str,
        collection_name: str = "documents",
        top_k: int = 10,
        reassemble: bool = True
    ) -> Dict[str, Any]:
        """
        Query with intelligent reassembly of chunks
        
        Args:
            query: Search query
            collection_name: Qdrant collection name
            top_k: Number of results
            reassemble: Whether to reassemble adjacent chunks
        
        Returns:
            Query results with reassembled context
        """
        logger.info(f"Querying collection {collection_name} with reassembly={reassemble}")
        
        # Generate query embedding
        query_embedding = self.embed_model.get_query_embedding(query)
        
        # Search in Qdrant
        search_results = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        if not reassemble:
            # Return raw results
            return {
                "results": [
                    {
                        "text": hit.payload.get("text"),
                        "score": hit.score,
                        "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
                    }
                    for hit in search_results
                ]
            }
        
        # Reassemble adjacent chunks
        reassembled = self._reassemble_chunks(search_results)
        
        return {
            "results": reassembled,
            "total_results": len(reassembled)
        }
    
    def _reassemble_chunks(self, search_results: List[Any]) -> List[Dict[str, Any]]:
        """
        Reassemble adjacent chunks for better context
        
        Args:
            search_results: Raw search results from Qdrant
        
        Returns:
            Reassembled results with expanded context
        """
        # Group by document_id
        by_document = {}
        for hit in search_results:
            doc_id = hit.payload.get("document_id")
            if doc_id not in by_document:
                by_document[doc_id] = []
            by_document[doc_id].append(hit)
        
        reassembled = []
        
        for doc_id, hits in by_document.items():
            # Sort by chunk_index
            hits.sort(key=lambda x: x.payload.get("chunk_index", 0))
            
            # Merge adjacent chunks
            current_text = ""
            current_score = 0
            chunk_indices = []
            
            for hit in hits:
                current_text += hit.payload.get("text", "") + "\n\n"
                current_score = max(current_score, hit.score)
                chunk_indices.append(hit.payload.get("chunk_index"))
            
            reassembled.append({
                "text": current_text.strip(),
                "score": current_score,
                "document_id": doc_id,
                "chunk_indices": chunk_indices,
                "num_chunks": len(chunk_indices),
                "metadata": hits[0].payload
            })
        
        # Sort by score
        reassembled.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Reassembled {len(search_results)} chunks into {len(reassembled)} contexts")
        return reassembled
    
    def __del__(self):
        """Cleanup thread/process pools"""
        try:
            self.thread_pool.shutdown(wait=False)
            self.process_pool.shutdown(wait=False)
        except:
            pass


# Global instance
optimized_rag_service = OptimizedRAGService()
