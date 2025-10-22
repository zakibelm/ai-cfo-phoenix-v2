import paramiko
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import socket
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SSHAgentService:
    """Service to connect and communicate with remote SSH agents"""
    
    def __init__(self):
        self.connection_pool: Dict[str, paramiko.SSHClient] = {}
        self.connection_timeout = 10  # seconds
        self.command_timeout = 60  # seconds
    
    def _get_connection_key(self, host: str, port: int, username: str) -> str:
        """Generate unique key for connection"""
        return f"{username}@{host}:{port}"
    
    @contextmanager
    def get_connection(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        password: Optional[str] = None,
        key_path: Optional[str] = None
    ) -> paramiko.SSHClient:
        """Get or create SSH connection"""
        conn_key = self._get_connection_key(host, port, username)
        
        # Check if connection exists and is alive
        if conn_key in self.connection_pool:
            client = self.connection_pool[conn_key]
            try:
                # Test connection
                transport = client.get_transport()
                if transport and transport.is_active():
                    yield client
                    return
                else:
                    # Connection dead, remove it
                    del self.connection_pool[conn_key]
            except Exception:
                # Connection error, remove it
                if conn_key in self.connection_pool:
                    del self.connection_pool[conn_key]
        
        # Create new connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Connect with key or password
            if key_path and Path(key_path).exists():
                logger.info(f"Connecting to {host}:{port} with key authentication")
                client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    key_filename=key_path,
                    timeout=self.connection_timeout,
                    look_for_keys=False,
                    allow_agent=False
                )
            elif password:
                logger.info(f"Connecting to {host}:{port} with password authentication")
                client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=self.connection_timeout,
                    look_for_keys=False,
                    allow_agent=False
                )
            else:
                raise ValueError("Either password or key_path must be provided")
            
            # Store in pool
            self.connection_pool[conn_key] = client
            logger.info(f"Successfully connected to {conn_key}")
            
            yield client
            
        except paramiko.AuthenticationException as e:
            logger.error(f"Authentication failed for {conn_key}: {str(e)}")
            raise ConnectionError(f"Authentication failed: {str(e)}")
        except socket.timeout as e:
            logger.error(f"Connection timeout for {conn_key}: {str(e)}")
            raise ConnectionError(f"Connection timeout: {str(e)}")
        except Exception as e:
            logger.error(f"Connection error for {conn_key}: {str(e)}")
            raise ConnectionError(f"Connection error: {str(e)}")
    
    def execute_command(
        self,
        client: paramiko.SSHClient,
        command: str
    ) -> Dict[str, Any]:
        """Execute command on remote agent"""
        try:
            stdin, stdout, stderr = client.exec_command(
                command,
                timeout=self.command_timeout
            )
            
            # Read output
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code != 0:
                logger.error(f"Command failed with exit code {exit_code}: {error}")
                raise RuntimeError(f"Command failed: {error}")
            
            return {
                "success": True,
                "output": output,
                "error": error,
                "exit_code": exit_code
            }
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise
    
    def call_remote_agent(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str],
        key_path: Optional[str],
        endpoint: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call remote agent via SSH"""
        try:
            with self.get_connection(host, port, username, password, key_path) as client:
                # Prepare payload
                payload = {
                    "query": query,
                    "context": context or {}
                }
                
                # Build command to call remote agent
                # Assuming remote agent has a CLI or API endpoint
                json_payload = json.dumps(payload).replace('"', '\\"')
                
                # Option 1: If remote agent has HTTP API, use curl
                if endpoint.startswith("http"):
                    command = f'curl -X POST {endpoint} -H "Content-Type: application/json" -d "{json_payload}"'
                
                # Option 2: If remote agent has Python CLI
                else:
                    command = f'python3 {endpoint} process \'{json_payload}\''
                
                logger.info(f"Executing command on remote agent: {command[:100]}...")
                
                # Execute command
                result = self.execute_command(client, command)
                
                # Parse JSON response
                try:
                    response_data = json.loads(result["output"])
                    return {
                        "success": True,
                        "agent_response": response_data,
                        "remote_host": f"{username}@{host}:{port}"
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse agent response: {str(e)}")
                    return {
                        "success": False,
                        "error": f"Invalid JSON response: {result['output'][:200]}",
                        "raw_output": result["output"]
                    }
                    
        except Exception as e:
            logger.error(f"Error calling remote agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "remote_host": f"{username}@{host}:{port}"
            }
    
    def test_connection(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str],
        key_path: Optional[str]
    ) -> Dict[str, Any]:
        """Test SSH connection to remote agent"""
        try:
            with self.get_connection(host, port, username, password, key_path) as client:
                # Execute simple test command
                result = self.execute_command(client, "echo 'Connection successful'")
                
                return {
                    "success": True,
                    "message": "Connection successful",
                    "host": f"{username}@{host}:{port}",
                    "output": result["output"].strip()
                }
                
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "host": f"{username}@{host}:{port}"
            }
    
    def close_all_connections(self):
        """Close all SSH connections"""
        for conn_key, client in self.connection_pool.items():
            try:
                client.close()
                logger.info(f"Closed connection: {conn_key}")
            except Exception as e:
                logger.error(f"Error closing connection {conn_key}: {str(e)}")
        
        self.connection_pool.clear()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all connections"""
        status = {
            "total_connections": len(self.connection_pool),
            "connections": []
        }
        
        for conn_key, client in self.connection_pool.items():
            try:
                transport = client.get_transport()
                is_active = transport and transport.is_active()
                
                status["connections"].append({
                    "key": conn_key,
                    "active": is_active
                })
            except Exception:
                status["connections"].append({
                    "key": conn_key,
                    "active": False
                })
        
        return status


# Global instance
ssh_service = SSHAgentService()
