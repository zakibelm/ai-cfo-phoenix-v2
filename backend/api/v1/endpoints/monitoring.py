import logging
from fastapi import APIRouter, HTTPException
from typing import Optional
from services.monitoring_service import monitoring_service
from services.resilience_service import circuit_breakers

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/monitoring/health")
async def get_health_status():
    """Get overall system health status"""
    try:
        return monitoring_service.get_health_status()
    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/metrics")
async def get_system_metrics():
    """Get overall system metrics"""
    try:
        return monitoring_service.get_system_metrics()
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/agents")
async def get_all_agent_metrics():
    """Get metrics for all agents"""
    try:
        return {
            "agents": monitoring_service.get_all_agent_metrics()
        }
    except Exception as e:
        logger.error(f"Error getting agent metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/agents/{agent_id}")
async def get_agent_metrics(agent_id: str):
    """Get metrics for a specific agent"""
    try:
        return monitoring_service.get_agent_metrics(agent_id)
    except Exception as e:
        logger.error(f"Error getting metrics for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/ssh")
async def get_all_ssh_metrics():
    """Get SSH connection metrics for all hosts"""
    try:
        return {
            "hosts": monitoring_service.get_all_ssh_metrics()
        }
    except Exception as e:
        logger.error(f"Error getting SSH metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/ssh/{host}")
async def get_ssh_metrics(host: str):
    """Get SSH metrics for a specific host"""
    try:
        return monitoring_service.get_ssh_metrics(host)
    except Exception as e:
        logger.error(f"Error getting SSH metrics for {host}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/circuit-breakers")
async def get_circuit_breaker_status():
    """Get status of all circuit breakers"""
    try:
        status = {}
        for name, cb in circuit_breakers.items():
            status[name] = cb.get_state()
        return {"circuit_breakers": status}
    except Exception as e:
        logger.error(f"Error getting circuit breaker status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/reset")
async def reset_metrics(agent_id: Optional[str] = None):
    """Reset metrics for an agent or all agents"""
    try:
        monitoring_service.reset_metrics(agent_id)
        return {
            "message": f"Metrics reset successfully" + (f" for agent {agent_id}" if agent_id else "")
        }
    except Exception as e:
        logger.error(f"Error resetting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/dashboard")
async def get_monitoring_dashboard():
    """Get comprehensive monitoring dashboard data"""
    try:
        return {
            "health": monitoring_service.get_health_status(),
            "system": monitoring_service.get_system_metrics(),
            "agents": monitoring_service.get_all_agent_metrics(),
            "ssh": monitoring_service.get_all_ssh_metrics(),
            "circuit_breakers": {
                name: cb.get_state()
                for name, cb in circuit_breakers.items()
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
