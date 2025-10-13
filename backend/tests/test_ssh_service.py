import pytest
from unittest.mock import Mock, patch, MagicMock
from services.ssh_agent_service import SSHAgentService
import paramiko


@pytest.fixture
def ssh_service():
    """Create an SSHAgentService instance"""
    return SSHAgentService()


@pytest.fixture
def mock_ssh_client():
    """Create a mock SSH client"""
    client = MagicMock(spec=paramiko.SSHClient)
    transport = MagicMock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport
    return client


class TestSSHAgentService:
    """Tests for SSHAgentService"""
    
    def test_connection_key_generation(self, ssh_service):
        """Test connection key is generated correctly"""
        key = ssh_service._get_connection_key("192.168.1.1", 22, "ubuntu")
        assert key == "ubuntu@192.168.1.1:22"
    
    @patch('paramiko.SSHClient')
    def test_successful_connection_with_password(self, mock_ssh_class, ssh_service):
        """Test successful SSH connection with password"""
        mock_client = MagicMock()
        mock_ssh_class.return_value = mock_client
        
        with ssh_service.get_connection(
            host="192.168.1.1",
            port=22,
            username="ubuntu",
            password="testpass"
        ) as client:
            assert client is not None
            mock_client.connect.assert_called_once()
    
    @patch('paramiko.SSHClient')
    def test_successful_connection_with_key(self, mock_ssh_class, ssh_service):
        """Test successful SSH connection with key"""
        mock_client = MagicMock()
        mock_ssh_class.return_value = mock_client
        
        with patch('pathlib.Path.exists', return_value=True):
            with ssh_service.get_connection(
                host="192.168.1.1",
                port=22,
                username="ubuntu",
                key_path="/path/to/key"
            ) as client:
                assert client is not None
                mock_client.connect.assert_called_once()
    
    @patch('paramiko.SSHClient')
    def test_connection_failure_authentication(self, mock_ssh_class, ssh_service):
        """Test SSH connection failure due to authentication"""
        mock_client = MagicMock()
        mock_client.connect.side_effect = paramiko.AuthenticationException("Auth failed")
        mock_ssh_class.return_value = mock_client
        
        with pytest.raises(ConnectionError, match="Authentication failed"):
            with ssh_service.get_connection(
                host="192.168.1.1",
                port=22,
                username="ubuntu",
                password="wrongpass"
            ):
                pass
    
    @patch('paramiko.SSHClient')
    def test_connection_timeout(self, mock_ssh_class, ssh_service):
        """Test SSH connection timeout"""
        mock_client = MagicMock()
        mock_client.connect.side_effect = TimeoutError("Connection timeout")
        mock_ssh_class.return_value = mock_client
        
        with pytest.raises(ConnectionError):
            with ssh_service.get_connection(
                host="192.168.1.1",
                port=22,
                username="ubuntu",
                password="testpass"
            ):
                pass
    
    def test_execute_command_success(self, ssh_service, mock_ssh_client):
        """Test successful command execution"""
        # Mock command execution
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        
        mock_stdout.read.return_value = b"Command output"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        result = ssh_service.execute_command(mock_ssh_client, "echo test")
        
        assert result["success"] == True
        assert result["output"] == "Command output"
        assert result["exit_code"] == 0
    
    def test_execute_command_failure(self, ssh_service, mock_ssh_client):
        """Test failed command execution"""
        # Mock command execution with error
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        
        mock_stdout.read.return_value = b""
        mock_stderr.read.return_value = b"Command error"
        mock_stdout.channel.recv_exit_status.return_value = 1
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        with pytest.raises(RuntimeError, match="Command failed"):
            ssh_service.execute_command(mock_ssh_client, "invalid_command")
    
    @patch('services.ssh_agent_service.SSHAgentService.get_connection')
    @patch('services.ssh_agent_service.SSHAgentService.execute_command')
    def test_call_remote_agent_success(self, mock_execute, mock_get_conn, ssh_service):
        """Test successful remote agent call"""
        # Mock connection
        mock_client = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_client
        
        # Mock command execution
        mock_execute.return_value = {
            "success": True,
            "output": '{"agent": "RemoteAgent", "response": "Test response"}',
            "exit_code": 0
        }
        
        result = ssh_service.call_remote_agent(
            host="192.168.1.1",
            port=22,
            username="ubuntu",
            password="testpass",
            key_path=None,
            endpoint="/process",
            query="test query"
        )
        
        assert result["success"] == True
        assert "agent_response" in result
    
    @patch('services.ssh_agent_service.SSHAgentService.get_connection')
    @patch('services.ssh_agent_service.SSHAgentService.execute_command')
    def test_call_remote_agent_invalid_json(self, mock_execute, mock_get_conn, ssh_service):
        """Test remote agent call with invalid JSON response"""
        # Mock connection
        mock_client = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_client
        
        # Mock command execution with invalid JSON
        mock_execute.return_value = {
            "success": True,
            "output": "Invalid JSON response",
            "exit_code": 0
        }
        
        result = ssh_service.call_remote_agent(
            host="192.168.1.1",
            port=22,
            username="ubuntu",
            password="testpass",
            key_path=None,
            endpoint="/process",
            query="test query"
        )
        
        assert result["success"] == False
        assert "error" in result
    
    @patch('services.ssh_agent_service.SSHAgentService.get_connection')
    @patch('services.ssh_agent_service.SSHAgentService.execute_command')
    def test_test_connection_success(self, mock_execute, mock_get_conn, ssh_service):
        """Test successful connection test"""
        # Mock connection
        mock_client = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_client
        
        # Mock command execution
        mock_execute.return_value = {
            "success": True,
            "output": "Connection successful",
            "exit_code": 0
        }
        
        result = ssh_service.test_connection(
            host="192.168.1.1",
            port=22,
            username="ubuntu",
            password="testpass",
            key_path=None
        )
        
        assert result["success"] == True
        assert "Connection successful" in result["message"]
    
    def test_connection_pool_reuse(self, ssh_service, mock_ssh_client):
        """Test that connections are reused from pool"""
        conn_key = "ubuntu@192.168.1.1:22"
        ssh_service.connection_pool[conn_key] = mock_ssh_client
        
        with ssh_service.get_connection(
            host="192.168.1.1",
            port=22,
            username="ubuntu",
            password="testpass"
        ) as client:
            assert client == mock_ssh_client
    
    def test_close_all_connections(self, ssh_service, mock_ssh_client):
        """Test closing all connections"""
        ssh_service.connection_pool["test1"] = mock_ssh_client
        ssh_service.connection_pool["test2"] = mock_ssh_client
        
        ssh_service.close_all_connections()
        
        assert len(ssh_service.connection_pool) == 0
        assert mock_ssh_client.close.call_count == 2
    
    def test_get_connection_status(self, ssh_service, mock_ssh_client):
        """Test getting connection status"""
        ssh_service.connection_pool["ubuntu@192.168.1.1:22"] = mock_ssh_client
        
        status = ssh_service.get_connection_status()
        
        assert status["total_connections"] == 1
        assert len(status["connections"]) == 1
        assert status["connections"][0]["active"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
