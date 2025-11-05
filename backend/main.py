#!/usr/bin/env python3
"""
AI CFO Suite Phoenix - Backend Principal
Version 3.1.0 - Production Ready
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration and core modules
try:
    from core.config import settings
    from api.v1.api import api_router
    from models.document import Base
    from core.database import engine
    USE_FULL_VERSION = True
except ImportError as e:
    logging.warning(f"Could not import full modules: {e}. Using simplified version.")
    USE_FULL_VERSION = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
if USE_FULL_VERSION:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered CFO Suite with multi-agent system and RAG",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS with settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database tables
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on startup"""
        try:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            logger.warning("Continuing without database initialization")
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "online",
            "docs": "/docs"
        }

else:
    # Simplified version fallback
    from pydantic import BaseModel
    from typing import Dict, List, Optional
    
    app = FastAPI(
        title="AI CFO Suite Phoenix",
        description="Suite IA financière multi-agents",
        version="3.1.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Modèles Pydantic simplifiés
    class HealthResponse(BaseModel):
        status: str
        timestamp: str
        version: str
        services: Dict[str, str]
    
    @app.get("/")
    async def root():
        return {
            "message": "AI CFO Suite Phoenix API",
            "version": "3.1.0",
            "status": "running (simplified mode)",
            "note": "Some dependencies are missing. Install full requirements for complete functionality."
        }
    
    @app.get("/api/v1/monitoring/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="3.1.0",
            services={
                "api": "running",
                "mode": "simplified",
                "database": "not_configured",
                "vector_db": "not_configured",
                "cache": "not_configured",
                "storage": "not_configured"
            }
        )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting AI CFO Suite Phoenix Backend in {'FULL' if USE_FULL_VERSION else 'SIMPLIFIED'} mode")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
