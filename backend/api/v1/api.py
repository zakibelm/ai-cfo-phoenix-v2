from fastapi import APIRouter
from api.v1.endpoints import chat, ingestion, agents, monitoring, oracle_cfo, optimized_ingestion

api_router = APIRouter()

# Oracle CFO - Master orchestrator (priority route)
api_router.include_router(oracle_cfo.router, prefix="/oracle", tags=["Oracle CFO"])

# Other endpoints
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(optimized_ingestion.router, prefix="/optimized-ingestion", tags=["Optimized Ingestion"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(monitoring.router, tags=["monitoring"])

