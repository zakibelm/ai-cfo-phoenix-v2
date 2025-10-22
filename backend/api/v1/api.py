from fastapi import APIRouter
from api.v1.endpoints import chat, ingestion, agents, monitoring, oracle_cfo, optimized_ingestion, preembedded_ingestion, auth, assistant, history

api_router = APIRouter()

# Authentication (public routes)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# AI Assistant (public routes)
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])

# User History (protected routes)
api_router.include_router(history.router, prefix="/history", tags=["History"])

# Oracle CFO - Master orchestrator (priority route)
api_router.include_router(oracle_cfo.router, prefix="/oracle", tags=["Oracle CFO"])

# Other endpoints
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(optimized_ingestion.router, prefix="/optimized-ingestion", tags=["Optimized Ingestion"])
api_router.include_router(preembedded_ingestion.router, prefix="/preembedded-ingestion", tags=["Pre-embedded Ingestion"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(monitoring.router, tags=["monitoring"])

