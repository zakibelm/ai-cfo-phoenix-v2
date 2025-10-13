from fastapi import APIRouter
from api.v1.endpoints import chat, ingestion, agents, monitoring

api_router = APIRouter()

api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(monitoring.router, tags=["monitoring"])
