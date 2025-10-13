import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for monitoring agents, SSH connections, and system metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            "request_count": 0,
            "error_count": 0,
            "total_response_time": 0.0,
            "min_response_time": float('inf'),
            "max_response_time": 0.0,
            "last_request": None,
            "errors": []
        })
        
        self.ssh_metrics = defaultdict(lambda: {
            "connection_attempts": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "last_connection": None,
            "last_error": None,
            "avg_latency": 0.0
        })
        
        self.system_metrics = {
            "uptime_start": datetime.now(),
            "total_requests": 0,
            "total_errors": 0
        }
    
    def record_agent_request(
        self,
        agent_id: str,
        response_time: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Record an agent request"""
        metrics = self.metrics[agent_id]
        
        metrics["request_count"] += 1
        metrics["last_request"] = datetime.now().isoformat()
        
        if success:
            metrics["total_response_time"] += response_time
            metrics["min_response_time"] = min(metrics["min_response_time"], response_time)
            metrics["max_response_time"] = max(metrics["max_response_time"], response_time)
        else:
            metrics["error_count"] += 1
            if error:
                metrics["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "error": error
                })
                # Keep only last 10 errors
                metrics["errors"] = metrics["errors"][-10:]
        
        self.system_metrics["total_requests"] += 1
        if not success:
            self.system_metrics["total_errors"] += 1
    
    def record_ssh_connection(
        self,
        host: str,
        success: bool,
        latency: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Record an SSH connection attempt"""
        metrics = self.ssh_metrics[host]
        
        metrics["connection_attempts"] += 1
        metrics["last_connection"] = datetime.now().isoformat()
        
        if success:
            metrics["successful_connections"] += 1
            if latency:
                # Update average latency
                total_success = metrics["successful_connections"]
                current_avg = metrics["avg_latency"]
                metrics["avg_latency"] = (current_avg * (total_success - 1) + latency) / total_success
        else:
            metrics["failed_connections"] += 1
            if error:
                metrics["last_error"] = {
                    "timestamp": datetime.now().isoformat(),
                    "error": error
                }
    
    def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get metrics for a specific agent"""
        metrics = self.metrics[agent_id]
        
        if metrics["request_count"] == 0:
            return {
                "agent_id": agent_id,
                "request_count": 0,
                "error_count": 0,
                "avg_response_time": 0.0,
                "success_rate": 0.0
            }
        
        avg_response_time = metrics["total_response_time"] / (
            metrics["request_count"] - metrics["error_count"]
        ) if metrics["request_count"] > metrics["error_count"] else 0.0
        
        success_rate = (
            (metrics["request_count"] - metrics["error_count"]) / metrics["request_count"]
        ) * 100
        
        return {
            "agent_id": agent_id,
            "request_count": metrics["request_count"],
            "error_count": metrics["error_count"],
            "avg_response_time": round(avg_response_time, 3),
            "min_response_time": metrics["min_response_time"] if metrics["min_response_time"] != float('inf') else 0.0,
            "max_response_time": metrics["max_response_time"],
            "success_rate": round(success_rate, 2),
            "last_request": metrics["last_request"],
            "recent_errors": metrics["errors"][-5:]  # Last 5 errors
        }
    
    def get_all_agent_metrics(self) -> List[Dict[str, Any]]:
        """Get metrics for all agents"""
        return [
            self.get_agent_metrics(agent_id)
            for agent_id in self.metrics.keys()
        ]
    
    def get_ssh_metrics(self, host: str) -> Dict[str, Any]:
        """Get SSH metrics for a specific host"""
        metrics = self.ssh_metrics[host]
        
        success_rate = (
            (metrics["successful_connections"] / metrics["connection_attempts"]) * 100
            if metrics["connection_attempts"] > 0 else 0.0
        )
        
        return {
            "host": host,
            "connection_attempts": metrics["connection_attempts"],
            "successful_connections": metrics["successful_connections"],
            "failed_connections": metrics["failed_connections"],
            "success_rate": round(success_rate, 2),
            "avg_latency": round(metrics["avg_latency"], 3),
            "last_connection": metrics["last_connection"],
            "last_error": metrics["last_error"]
        }
    
    def get_all_ssh_metrics(self) -> List[Dict[str, Any]]:
        """Get SSH metrics for all hosts"""
        return [
            self.get_ssh_metrics(host)
            for host in self.ssh_metrics.keys()
        ]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""
        uptime = datetime.now() - self.system_metrics["uptime_start"]
        
        error_rate = (
            (self.system_metrics["total_errors"] / self.system_metrics["total_requests"]) * 100
            if self.system_metrics["total_requests"] > 0 else 0.0
        )
        
        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split('.')[0],
            "total_requests": self.system_metrics["total_requests"],
            "total_errors": self.system_metrics["total_errors"],
            "error_rate": round(error_rate, 2),
            "agents_monitored": len(self.metrics),
            "ssh_hosts_monitored": len(self.ssh_metrics)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        system = self.get_system_metrics()
        
        # Determine health status
        if system["error_rate"] > 20:
            status = "unhealthy"
        elif system["error_rate"] > 10:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metrics": system
        }
    
    def reset_metrics(self, agent_id: Optional[str] = None):
        """Reset metrics for an agent or all agents"""
        if agent_id:
            if agent_id in self.metrics:
                del self.metrics[agent_id]
                logger.info(f"Reset metrics for agent: {agent_id}")
        else:
            self.metrics.clear()
            self.ssh_metrics.clear()
            self.system_metrics = {
                "uptime_start": datetime.now(),
                "total_requests": 0,
                "total_errors": 0
            }
            logger.info("Reset all metrics")


# Global monitoring instance
monitoring_service = MonitoringService()
