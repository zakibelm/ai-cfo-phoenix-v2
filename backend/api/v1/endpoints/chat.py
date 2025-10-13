import logging
import time
from fastapi import APIRouter, HTTPException
from models.api_models import QueryRequest, QueryResponse
from agents.agent_system import AgentOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize agent orchestrator
orchestrator = AgentOrchestrator()


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Query an AI agent with RAG context"""
    try:
        start_time = time.time()
        
        # Route to appropriate agent
        agent_name = request.agent.value if request.agent else None
        result = orchestrator.route_query(request.query, agent_name)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            agent=result["agent"],
            response=result["response"],
            sources=result.get("sources", []),
            tool_calls=result.get("tool_calls", []),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """List all available agents and their status"""
    try:
        agents_status = orchestrator.get_all_agents_status()
        return {"agents": agents_status}
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
