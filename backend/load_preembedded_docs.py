#!/usr/bin/env python3
"""
Script pour charger tous les documents pré-embedded du dossier docs/
Utilise le nouveau service PreEmbeddedRAGService
"""

import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.preembedded_rag_service import preembedded_rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to load all pre-embedded documents"""
    
    # Path to docs directory
    docs_dir = Path(__file__).parent.parent / "docs"
    
    if not docs_dir.exists():
        logger.error(f"Directory not found: {docs_dir}")
        return 1
    
    logger.info(f"Loading pre-embedded documents from: {docs_dir}")
    logger.info("=" * 80)
    
    # Load all documents
    result = preembedded_rag_service.load_preembedded_directory(
        directory_path=str(docs_dir),
        collection_name="documents",
        metadata={
            "source": "docs_directory",
            "loaded_by": "load_preembedded_docs.py"
        }
    )
    
    # Display results
    logger.info("=" * 80)
    logger.info("LOADING SUMMARY")
    logger.info("=" * 80)
    
    if result.get("success"):
        logger.info(f"✓ Total files: {result['total_files']}")
        logger.info(f"✓ Successful: {result['success_count']}")
        logger.info(f"✗ Errors: {result['error_count']}")
        logger.info(f"⏱ Processing time: {result['processing_time_seconds']}s")
        logger.info(f"📦 Collection: {result['collection']}")
        
        # Display individual results
        logger.info("\nDETAILED RESULTS:")
        logger.info("-" * 80)
        
        for idx, doc_result in enumerate(result.get("results", []), 1):
            if doc_result.get("success"):
                logger.info(f"{idx}. ✓ {doc_result['filename']}")
                logger.info(f"   - Chunks: {doc_result['total_chunks']}")
                logger.info(f"   - Vectors: {doc_result['total_vectors']}")
                logger.info(f"   - Time: {doc_result['processing_time_seconds']}s")
            else:
                logger.error(f"{idx}. ✗ {doc_result.get('document_id', 'unknown')}")
                logger.error(f"   - Error: {doc_result.get('error', 'unknown')}")
        
        # Get collection info
        logger.info("\n" + "=" * 80)
        logger.info("COLLECTION INFO")
        logger.info("=" * 80)
        
        collection_info = preembedded_rag_service.get_collection_info("documents")
        if "error" not in collection_info:
            logger.info(f"Collection: {collection_info['name']}")
            logger.info(f"Points count: {collection_info['points_count']}")
            logger.info(f"Vectors count: {collection_info['vectors_count']}")
            logger.info(f"Vector size: {collection_info['config']['vector_size']}")
            logger.info(f"Distance metric: {collection_info['config']['distance']}")
        
        logger.info("\n✓ All documents loaded successfully!")
        return 0
    else:
        logger.error(f"✗ Loading failed: {result.get('error', 'unknown')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

