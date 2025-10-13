import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.dynamic_agent_system import DynamicAgent, DynamicAgentOrchestrator
from models.database import AgentConfig


@pytest.fixture
def mock_agent_config():
    """Create a mock agent configuration"""
    config = Mock(spec=AgentConfig)
    config.id = "TestAgent"
    config.name = "Test Agent"
    config.role = "Test Role"
    config.goal = "Test Goal"
    config.backstory = "Test Backstory"
    config.system_prompt = "Test system prompt"
    config.namespace = "test"
    config.is_active = True
    config.icon = "🧪"
    config.color = "#ffffff"
    config.tools = []
    config.metadata = {"keywords": ["test"]}
    config.query_count = 0
    config.last_query_time = None
    return config


@pytest.fixture
def dynamic_agent(mock_agent_config):
    """Create a DynamicAgent instance"""
    return DynamicAgent(mock_agent_config)


class TestDynamicAgent:
    """Tests for DynamicAgent class"""
    
    def test_agent_initialization(self, dynamic_agent, mock_agent_config):
        """Test agent is properly initialized"""
        assert dynamic_agent.id == mock_agent_config.id
        assert dynamic_agent.name == mock_agent_config.name
        assert dynamic_agent.role == mock_agent_config.role
        assert dynamic_agent.goal == mock_agent_config.goal
        assert dynamic_agent.is_active == True
    
    def test_default_system_prompt_generation(self, mock_agent_config):
        """Test default system prompt is generated when none provided"""
        mock_agent_config.system_prompt = None
        agent = DynamicAgent(mock_agent_config)
        
        assert agent.system_prompt is not None
        assert mock_agent_config.name in agent.system_prompt
        assert mock_agent_config.role in agent.system_prompt
    
    @patch('agents.dynamic_agent_system.RAGService')
    def test_query_knowledge_base(self, mock_rag_service, dynamic_agent):
        """Test querying the knowledge base"""
        # Mock RAG service response
        mock_results = [
            {"text": "Test result 1", "score": 0.9},
            {"text": "Test result 2", "score": 0.8}
        ]
        dynamic_agent.rag_service.query = Mock(return_value=mock_results)
        
        results = dynamic_agent.query_knowledge_base("test query")
        
        assert len(results) == 2
        assert results[0]["text"] == "Test result 1"
        dynamic_agent.rag_service.query.assert_called_once()
    
    @patch('agents.dynamic_agent_system.get_db')
    def test_process_query(self, mock_get_db, dynamic_agent):
        """Test processing a query"""
        # Mock database context
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        # Mock RAG results
        dynamic_agent.query_knowledge_base = Mock(return_value=[
            {"text": "Test context", "score": 0.9}
        ])
        
        result = dynamic_agent.process_query("test query")
        
        assert result["agent"] == dynamic_agent.name
        assert result["agent_id"] == dynamic_agent.id
        assert "response" in result
        assert "sources" in result
    
    def test_role_specific_analysis_tax(self, mock_agent_config):
        """Test role-specific analysis for tax agent"""
        mock_agent_config.id = "TaxAgent"
        mock_agent_config.role = "Expert Fiscal"
        agent = DynamicAgent(mock_agent_config)
        
        analysis = agent._role_specific_analysis("tax query")
        
        assert "fiscal" in analysis.lower() or "tax" in analysis.lower()
    
    def test_role_specific_analysis_accountant(self, mock_agent_config):
        """Test role-specific analysis for accountant agent"""
        mock_agent_config.id = "AccountantAgent"
        mock_agent_config.role = "Expert Comptable"
        agent = DynamicAgent(mock_agent_config)
        
        analysis = agent._role_specific_analysis("accounting query")
        
        assert "comptable" in analysis.lower() or "ratio" in analysis.lower()


class TestDynamicAgentOrchestrator:
    """Tests for DynamicAgentOrchestrator class"""
    
    @patch('agents.dynamic_agent_system.get_db')
    def test_orchestrator_initialization(self, mock_get_db):
        """Test orchestrator initializes correctly"""
        # Mock database with agents
        mock_db = MagicMock()
        mock_agent_config = Mock(spec=AgentConfig)
        mock_agent_config.id = "TestAgent"
        mock_agent_config.name = "Test Agent"
        mock_agent_config.is_active = True
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_agent_config]
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        orchestrator = DynamicAgentOrchestrator()
        
        assert len(orchestrator.agents_cache) > 0
    
    @patch('agents.dynamic_agent_system.get_db')
    def test_get_agent(self, mock_get_db, mock_agent_config):
        """Test getting an agent by ID"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_agent_config]
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        orchestrator = DynamicAgentOrchestrator()
        agent = orchestrator.get_agent("TestAgent")
        
        assert agent is not None
        assert agent.id == "TestAgent"
    
    @patch('agents.dynamic_agent_system.get_db')
    def test_list_agents(self, mock_get_db, mock_agent_config):
        """Test listing all agents"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_agent_config]
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        orchestrator = DynamicAgentOrchestrator()
        agents = orchestrator.list_agents()
        
        assert len(agents) > 0
        assert all(isinstance(agent, DynamicAgent) for agent in agents)
    
    @patch('agents.dynamic_agent_system.get_db')
    def test_reload_agents(self, mock_get_db, mock_agent_config):
        """Test reloading agents"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_agent_config]
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        orchestrator = DynamicAgentOrchestrator()
        initial_count = len(orchestrator.agents_cache)
        
        orchestrator.reload_agents()
        
        assert len(orchestrator.agents_cache) == initial_count
    
    @patch('agents.dynamic_agent_system.get_db')
    def test_auto_select_agent_by_keywords(self, mock_get_db):
        """Test auto-selecting agent based on query keywords"""
        # Create mock agents with different keywords
        tax_agent = Mock(spec=AgentConfig)
        tax_agent.id = "TaxAgent"
        tax_agent.name = "Tax Agent"
        tax_agent.is_active = True
        tax_agent.metadata = {"keywords": ["tax", "fiscal", "impôt"]}
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [tax_agent]
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        orchestrator = DynamicAgentOrchestrator()
        
        # Mock the agent's process_query method
        orchestrator.agents_cache["TaxAgent"].process_query = Mock(return_value={"agent": "TaxAgent"})
        
        result = orchestrator.route_query("What are the tax implications?")
        
        assert result["agent"] == "TaxAgent"


@pytest.fixture
def sample_agent_templates():
    """Sample agent templates for testing"""
    return {
        "TestAgent": {
            "id": "TestAgent",
            "name": "Test Agent",
            "role": "Test Role",
            "goal": "Test Goal",
            "backstory": "Test Backstory",
            "system_prompt": "Test Prompt",
            "namespace": "test",
            "icon": "🧪",
            "color": "#ffffff",
            "metadata": {"keywords": ["test"]}
        }
    }


class TestAgentTemplates:
    """Tests for agent templates"""
    
    def test_template_structure(self, sample_agent_templates):
        """Test that templates have required fields"""
        template = sample_agent_templates["TestAgent"]
        
        required_fields = ["id", "name", "role", "goal", "backstory", "namespace"]
        for field in required_fields:
            assert field in template
    
    def test_template_system_prompt(self, sample_agent_templates):
        """Test that templates have system prompts"""
        template = sample_agent_templates["TestAgent"]
        
        assert "system_prompt" in template
        assert len(template["system_prompt"]) > 0
    
    def test_template_metadata(self, sample_agent_templates):
        """Test that templates have metadata"""
        template = sample_agent_templates["TestAgent"]
        
        assert "metadata" in template
        assert "keywords" in template["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
