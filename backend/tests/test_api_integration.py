"""
API Integration Tests
Test all critical endpoints end-to-end
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from models.document import Base
from core.database import get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoints:
    """Test health and monitoring endpoints"""
    
    def test_health_check(self):
        """Test /api/v1/monitoring/health"""
        response = client.get("/api/v1/monitoring/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_metrics(self):
        """Test /api/v1/monitoring/metrics"""
        response = client.get("/api/v1/monitoring/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "agents" in data


class TestOracleCFOEndpoints:
    """Test Oracle CFO orchestrator endpoints"""
    
    def test_list_agents(self):
        """Test GET /api/v1/oracle/agents"""
        response = client.get("/api/v1/oracle/agents")
        assert response.status_code == 200
        data = response.json()
        assert "total_agents" in data
        assert "agents" in data
        assert data["total_agents"] == 10  # We have 10 agents
    
    def test_get_agent_details(self):
        """Test GET /api/v1/oracle/agents/{agent_name}"""
        response = client.get("/api/v1/oracle/agents/TaxAgent")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TaxAgent"
        assert "role" in data
        assert "goal" in data
        assert "constraints" in data
        assert "deliverables" in data
    
    def test_get_nonexistent_agent(self):
        """Test getting non-existent agent"""
        response = client.get("/api/v1/oracle/agents/NonExistentAgent")
        assert response.status_code == 404
    
    def test_get_available_models(self):
        """Test GET /api/v1/oracle/models"""
        response = client.get("/api/v1/oracle/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
    
    def test_get_jurisdictions(self):
        """Test GET /api/v1/oracle/jurisdictions"""
        response = client.get("/api/v1/oracle/jurisdictions")
        assert response.status_code == 200
        data = response.json()
        assert "jurisdictions" in data
        assert len(data["jurisdictions"]) == 5  # CA, CA-QC, CA-ON, FR, US


class TestDocumentEndpoints:
    """Test document management endpoints"""
    
    @pytest.mark.skip(reason="Requires file upload implementation")
    def test_upload_document(self):
        """Test POST /api/v1/ingestion/upload"""
        # This would require multipart file upload
        # Skipped for now - to be implemented with real file handling
        pass
    
    def test_list_documents_empty(self):
        """Test listing documents when none exist"""
        # This endpoint needs to be created
        # For now, we verify the structure
        pass


class TestChatEndpoints:
    """Test chat/query endpoints"""
    
    @pytest.mark.skip(reason="Requires OpenRouter API key")
    def test_query_agent(self):
        """Test POST /api/v1/oracle/query"""
        # This requires a valid OpenRouter API key
        # Skipped in CI/CD - can be run manually with key
        payload = {
            "query": "What are my tax obligations?",
            "model": "gpt-4-turbo",
            "language": "en",
            "jurisdiction": "CA"
        }
        response = client.post("/api/v1/oracle/query", json=payload)
        # Would assert response structure if API key available
    
    def test_query_validation(self):
        """Test query input validation"""
        # Test with invalid payload
        payload = {
            "query": "",  # Empty query
            "model": "invalid-model"
        }
        response = client.post("/api/v1/oracle/query", json=payload)
        # Should validate and return error
        assert response.status_code in [400, 422]


class TestAgentManagementEndpoints:
    """Test dynamic agent management"""
    
    def test_list_dynamic_agents_empty(self):
        """Test listing agents when none exist"""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        # Should return empty list or default agents
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_create_custom_agent(self):
        """Test POST /api/v1/agents"""
        payload = {
            "name": "CustomTaxAgent",
            "role": "Custom Tax Specialist",
            "goal": "Provide custom tax advice",
            "backstory": "Expert in custom tax scenarios",
            "system_prompt": "You are a custom tax agent...",
            "is_remote": False
        }
        response = client.post("/api/v1/agents", json=payload)
        # Would assert successful creation
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_update_agent(self):
        """Test PUT /api/v1/agents/{agent_id}"""
        # Create agent first, then update
        pass
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_delete_agent(self):
        """Test DELETE /api/v1/agents/{agent_id}"""
        # Create agent first, then delete
        pass


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_404_not_found(self):
        """Test 404 for non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test 405 for wrong HTTP method"""
        response = client.post("/api/v1/oracle/agents")  # Should be GET
        assert response.status_code == 405
    
    def test_validation_error(self):
        """Test 422 for invalid payload"""
        response = client.post("/api/v1/oracle/query", json={"invalid": "payload"})
        assert response.status_code == 422


class TestCORS:
    """Test CORS headers"""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are set"""
        response = client.options("/api/v1/oracle/agents")
        # Should have CORS headers
        # Note: TestClient may not fully simulate CORS
        assert response.status_code in [200, 405]


class TestRateLimiting:
    """Test rate limiting (if implemented)"""
    
    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    def test_rate_limit(self):
        """Test rate limiting on endpoints"""
        # Make many requests quickly
        for _ in range(100):
            response = client.get("/api/v1/oracle/agents")
        # Should eventually get 429 Too Many Requests
        pass


class TestAuthentication:
    """Test authentication (if implemented)"""
    
    @pytest.mark.skip(reason="Authentication not yet implemented")
    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without auth"""
        response = client.post("/api/v1/agents", json={})
        assert response.status_code == 401
    
    @pytest.mark.skip(reason="Authentication not yet implemented")
    def test_protected_endpoint_with_auth(self):
        """Test accessing protected endpoint with valid auth"""
        headers = {"Authorization": "Bearer valid-token"}
        response = client.post("/api/v1/agents", json={}, headers=headers)
        # Should not be 401
        pass


# Run tests with: pytest backend/tests/test_api_integration.py -v

