import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1.api import api_router
from models.api_models import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered CFO Suite with multi-agent system and RAG",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check services (simplified - in production, actually ping each service)
        services = {
            "database": "online",
            "qdrant": "online",
            "redis": "online",
            "minio": "online"
        }
        
        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            services=services,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            services={"error": str(e)},
            timestamp=datetime.now()
        )


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Qdrant URL: {settings.QDRANT_URL}")
    
    # Initialize database
    try:
        from core.database import init_db
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info(f"Shutting down {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
