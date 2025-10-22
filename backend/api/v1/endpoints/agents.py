import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from models.database import AgentConfig
from core.database import get_db_session
from agents.dynamic_agent_system import DynamicAgentOrchestrator, init_default_agents
from services.ssh_agent_service import ssh_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Global orchestrator instance
orchestrator = DynamicAgentOrchestrator()


class AgentCreateRequest(BaseModel):
    """Request to create a new agent"""
    id: str = Field(..., description="Unique agent ID (e.g., 'MyCustomAgent')")
    name: str = Field(..., description="Display name")
    role: str = Field(..., description="Agent role/title")
    goal: str = Field(..., description="Agent's primary goal")
    backstory: str = Field(..., description="Agent's background and expertise")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    namespace: str = Field(default="default", description="Qdrant namespace")
    icon: str = Field(default="🤖", description="Icon emoji")
    color: str = Field(default="#64ffda", description="Color hex code")
    
    # SSH Configuration (for remote agents)
    is_remote: bool = Field(default=False, description="Is this a remote SSH agent?")
    ssh_host: Optional[str] = Field(None, description="SSH host (e.g., '192.168.1.10')")
    ssh_port: int = Field(default=22, description="SSH port")
    ssh_username: Optional[str] = Field(None, description="SSH username")
    ssh_password: Optional[str] = Field(None, description="SSH password (will be encrypted)")
    ssh_key_path: Optional[str] = Field(None, description="Path to SSH private key")
    ssh_endpoint: str = Field(default="/process", description="Remote agent endpoint")
    
    keywords: List[str] = Field(default_factory=list, description="Keywords for auto-routing")


class AgentUpdateRequest(BaseModel):
    """Request to update an agent"""
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    system_prompt: Optional[str] = None
    namespace: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    
    # SSH fields
    ssh_host: Optional[str] = None
    ssh_port: Optional[int] = None
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_key_path: Optional[str] = None
    ssh_endpoint: Optional[str] = None
    
    keywords: Optional[List[str]] = None


class SSHTestRequest(BaseModel):
    """Request to test SSH connection"""
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    key_path: Optional[str] = None


@router.get("/agents")
async def list_agents(db: Session = Depends(get_db_session)):
    """List all agents"""
    try:
        agents = db.query(AgentConfig).all()
        return {
            "agents": [agent.to_dict() for agent in agents],
            "total": len(agents)
        }
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_db_session)):
    """Get agent by ID"""
    try:
        agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents")
async def create_agent(request: AgentCreateRequest, db: Session = Depends(get_db_session)):
    """Create a new agent"""
    try:
        # Check if agent already exists
        existing = db.query(AgentConfig).filter(AgentConfig.id == request.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Agent with this ID already exists")
        
        # Validate SSH configuration if remote
        if request.is_remote:
            if not request.ssh_host or not request.ssh_username:
                raise HTTPException(
                    status_code=400,
                    detail="SSH host and username are required for remote agents"
                )
            if not request.ssh_password and not request.ssh_key_path:
                raise HTTPException(
                    status_code=400,
                    detail="Either SSH password or key path must be provided"
                )
        
        # Create agent
        agent = AgentConfig(
            id=request.id,
            name=request.name,
            role=request.role,
            goal=request.goal,
            backstory=request.backstory,
            system_prompt=request.system_prompt,
            namespace=request.namespace,
            icon=request.icon,
            color=request.color,
            is_custom=True,
            is_remote=request.is_remote,
            ssh_host=request.ssh_host,
            ssh_port=request.ssh_port,
            ssh_username=request.ssh_username,
            ssh_password=request.ssh_password,  # TODO: Encrypt in production
            ssh_key_path=request.ssh_key_path,
            ssh_endpoint=request.ssh_endpoint,
            metadata={"keywords": request.keywords}
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        # Reload orchestrator to include new agent
        orchestrator.reload_agents()
        
        logger.info(f"Created new agent: {request.name} (ID: {request.id})")
        
        return {
            "message": "Agent created successfully",
            "agent": agent.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agents/{agent_id}")
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """Update an agent"""
    try:
        agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update fields if provided
        update_data = request.dict(exclude_unset=True)
        
        # Handle keywords specially
        if "keywords" in update_data:
            if agent.metadata is None:
                agent.metadata = {}
            agent.metadata["keywords"] = update_data.pop("keywords")
        
        # Update other fields
        for key, value in update_data.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        db.commit()
        db.refresh(agent)
        
        # Reload orchestrator
        orchestrator.reload_agents()
        
        logger.info(f"Updated agent: {agent_id}")
        
        return {
            "message": "Agent updated successfully",
            "agent": agent.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db_session)):
    """Delete an agent"""
    try:
        agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Prevent deletion of default agents
        if not agent.is_custom:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete default agents. Deactivate them instead."
            )
        
        db.delete(agent)
        db.commit()
        
        # Reload orchestrator
        orchestrator.reload_agents()
        
        logger.info(f"Deleted agent: {agent_id}")
        
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/ssh/test")
async def test_ssh_connection(request: SSHTestRequest):
    """Test SSH connection to remote agent"""
    try:
        result = ssh_service.test_connection(
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            key_path=request.key_path
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "SSH connection successful",
                "details": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"SSH connection failed: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing SSH connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/ssh/status")
async def get_ssh_status():
    """Get status of all SSH connections"""
    try:
        status = ssh_service.get_connection_status()
        return status
    except Exception as e:
        logger.error(f"Error getting SSH status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/reload")
async def reload_agents():
    """Reload all agents from database (hot-reload)"""
    try:
        orchestrator.reload_agents()
        return {
            "message": "Agents reloaded successfully",
            "agent_count": len(orchestrator.list_agents())
        }
    except Exception as e:
        logger.error(f"Error reloading agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/init-defaults")
async def initialize_default_agents(db: Session = Depends(get_db_session)):
    """Initialize default agents (run once)"""
    try:
        init_default_agents(db)
        orchestrator.reload_agents()
        return {
            "message": "Default agents initialized successfully",
            "agent_count": len(orchestrator.list_agents())
        }
    except Exception as e:
        logger.error(f"Error initializing default agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
