"""
Load Documentation into RAG
Indexes all documentation files for the AI Assistant
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.preembedded_rag_service import PreEmbeddedRAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_markdown_file(filepath: Path) -> str:
    """Read markdown file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {str(e)}")
        return ""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:
                chunk = text[start:start + break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def create_embeddings_for_docs(rag_service: PreEmbeddedRAGService, docs_dir: Path):
    """Create embeddings for all documentation files"""
    
    # Documentation files to index
    doc_files = [
        "README.md",
        "EXPERT_EVALUATION.md",
        "MIGRATION_PREEMBEDDED.md",
        "MODIFICATIONS_SUMMARY.md",
        "CHANGELOG.md",
        "QUICKSTART.md",
    ]
    
    all_chunks = []
    
    for doc_file in doc_files:
        filepath = docs_dir / doc_file
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            continue
        
        logger.info(f"Processing {doc_file}...")
        
        content = read_markdown_file(filepath)
        if not content:
            continue
        
        # Split into chunks
        chunks = chunk_text(content)
        logger.info(f"  Created {len(chunks)} chunks")
        
        # Create chunk objects
        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "text": chunk_text,
                "filename": doc_file,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "document_type": "documentation",
                "created_at": datetime.utcnow().isoformat()
            })
    
    logger.info(f"\nTotal chunks to embed: {len(all_chunks)}")
    
    # Note: Since we don't have the embedding model here,
    # we'll create a JSON file that can be processed by the embedding service
    output_file = docs_dir / "documentation.embedded.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "chunks": all_chunks,
            "metadata": {
                "total_documents": len(doc_files),
                "total_chunks": len(all_chunks),
                "created_at": datetime.utcnow().isoformat(),
                "embedding_model": "BAAI/bge-small-en-v1.5",
                "collection_name": "documentation"
            }
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✅ Documentation chunks saved to: {output_file}")
    logger.info("⚠️  Note: You need to run the embedding service to generate vectors")
    logger.info("    This file is ready to be processed by the embedding pipeline")


def main():
    """Main function"""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    logger.info("=" * 60)
    logger.info("AI CFO Suite - Documentation Loader")
    logger.info("=" * 60)
    
    # Initialize RAG service
    rag_service = PreEmbeddedRAGService()
    
    # Create embeddings for documentation
    create_embeddings_for_docs(rag_service, project_root)
    
    logger.info("\n" + "=" * 60)
    logger.info("Documentation preparation complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

