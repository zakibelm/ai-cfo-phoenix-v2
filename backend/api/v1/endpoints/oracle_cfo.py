"""
Oracle CFO API Endpoints
Master orchestrator for all 10 financial agents
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from agents.agent_system import oracle_cfo

logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    agent_name: Optional[str] = None
    model: str = "gpt-4-turbo"
    language: str = "fr"
    jurisdiction: str = "CA"


class CollaborationRequest(BaseModel):
    """Multi-agent collaboration request"""
    query: str
    agent_ids: List[str]
    model: str = "gpt-4-turbo"
    language: str = "fr"
    jurisdiction: str = "CA"


@router.post("/query")
async def oracle_query(request: QueryRequest):
    """
    Oracle CFO intelligent query routing
    
    Automatically routes query to the most appropriate agent
    or uses specified agent if provided.
    
    Args:
        query: User question
        agent_name: Optional specific agent to use
        model: LLM model (gpt-4-turbo, claude-3-sonnet, etc.)
        language: Response language (fr, en)
        jurisdiction: Tax jurisdiction (CA, CA-QC, FR, US, etc.)
    
    Returns:
        Agent response with sources and metadata
    """
    try:
        result = oracle_cfo.route_query(
            query=request.query,
            agent_name=request.agent_name,
            model=request.model,
            language=request.language,
            jurisdiction=request.jurisdiction
        )
        return result
    
    except Exception as e:
        logger.error(f"Oracle CFO query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collaborate")
async def oracle_collaborate(request: CollaborationRequest):
    """
    Multi-agent collaboration
    
    Consults multiple agents and synthesizes their responses
    into a coherent strategic recommendation.
    
    Args:
        query: Complex question requiring multiple perspectives
        agent_ids: List of agent names to consult
        model: LLM model
        language: Response language
        jurisdiction: Tax jurisdiction
    
    Returns:
        Individual agent responses + synthesized recommendation
    """
    try:
        result = oracle_cfo.collaborate_agents(
            query=request.query,
            agent_ids=request.agent_ids,
            model=request.model,
            language=request.language,
            jurisdiction=request.jurisdiction
        )
        return result
    
    except Exception as e:
        logger.error(f"Oracle CFO collaboration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_all_agents():
    """
    Get all available agents and their status
    
    Returns:
        List of all 10 agents with metadata and statistics
    """
    try:
        agents_status = oracle_cfo.get_all_agents_status()
        return {
            "total_agents": len(agents_status),
            "agents": agents_status
        }
    
    except Exception as e:
        logger.error(f"Get agents error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}")
async def get_agent_details(agent_name: str):
    """
    Get detailed information about a specific agent
    
    Args:
        agent_name: Name of the agent
    
    Returns:
        Agent details including role, goal, constraints, deliverables
    """
    try:
        agent = oracle_cfo.agents.get(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
        return {
            "name": agent.name,
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "constraints": agent.constraints,
            "deliverables": agent.deliverables,
            "namespace": agent.namespace,
            "query_count": agent.query_count,
            "last_query": agent.last_query_time.isoformat() if agent.last_query_time else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get agent details error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-coherence")
async def validate_coherence(results: List[dict]):
    """
    Validate coherence between multiple agent responses
    
    Uses SupervisorAgent to check for contradictions,
    identify synergies, and provide consolidated recommendations.
    
    Args:
        results: List of agent responses to validate
    
    Returns:
        Coherence validation report
    """
    try:
        validation = oracle_cfo.validate_coherence(results)
        return validation
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """
    Get list of available LLM models via OpenRouter
    
    Returns:
        List of models with pricing and capabilities
    """
    return {
        "models": [
            {
                "id": "gpt-4-turbo",
                "provider": "OpenAI",
                "context": "128K",
                "cost_per_1k": {"input": 0.01, "output": 0.03},
                "recommended_for": "Complex analysis, high accuracy"
            },
            {
                "id": "claude-3-sonnet",
                "provider": "Anthropic",
                "context": "200K",
                "cost_per_1k": {"input": 0.003, "output": 0.015},
                "recommended_for": "Best quality/price ratio"
            },
            {
                "id": "gemini-pro",
                "provider": "Google",
                "context": "32K",
                "cost_per_1k": {"input": 0.000125, "output": 0.000375},
                "recommended_for": "High volume, cost-effective"
            },
            {
                "id": "mixtral-8x7b",
                "provider": "Mistral",
                "context": "32K",
                "cost_per_1k": {"input": 0.00027, "output": 0.00027},
                "recommended_for": "Open source, balanced"
            },
            {
                "id": "llama-3-70b",
                "provider": "Meta",
                "context": "8K",
                "cost_per_1k": {"input": 0.00059, "output": 0.00079},
                "recommended_for": "Open source, fast"
            }
        ]
    }


@router.get("/jurisdictions")
async def get_supported_jurisdictions():
    """
    Get list of supported tax jurisdictions
    
    Returns:
        List of jurisdictions with tax details
    """
    return {
        "jurisdictions": [
            {
                "code": "CA",
                "name": "Canada (Fédéral)",
                "laws": "LIR",
                "taxes": "T1/T2, TPS 5%",
                "authority": "ARC"
            },
            {
                "code": "CA-QC",
                "name": "Québec",
                "laws": "LIR + Loi QC",
                "taxes": "TP-1/CO-17, TPS+TVQ 14.975%",
                "authority": "ARC + Revenu Québec"
            },
            {
                "code": "CA-ON",
                "name": "Ontario",
                "laws": "LIR",
                "taxes": "T1/T2, HST 13%",
                "authority": "ARC"
            },
            {
                "code": "FR",
                "name": "France",
                "laws": "CGI, PCG",
                "taxes": "IR/IS, TVA 20%",
                "authority": "DGFiP"
            },
            {
                "code": "US",
                "name": "États-Unis",
                "laws": "IRC",
                "taxes": "1040/1120, Sales Tax",
                "authority": "IRS"
            }
        ]
    }

