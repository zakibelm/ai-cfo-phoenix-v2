import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import AgentConfig
from services.rag_service import RAGService
from core.database import get_db

logger = logging.getLogger(__name__)


class DynamicAgent:
    """Dynamic agent that loads configuration from database"""
    
    def __init__(self, config: AgentConfig):
        self.id = config.id
        self.name = config.name
        self.role = config.role
        self.goal = config.goal
        self.backstory = config.backstory
        self.system_prompt = config.system_prompt or self._default_system_prompt()
        self.namespace = config.namespace
        self.is_active = config.is_active
        self.icon = config.icon
        self.color = config.color
        self.tools = config.tools or []
        self.metadata = config.metadata or {}
        
        self.rag_service = RAGService()
        self.query_count = config.query_count
        self.last_query_time = config.last_query_time
    
    def _default_system_prompt(self) -> str:
        """Generate default system prompt"""
        return f"""Tu es {self.name}, un {self.role}.

Ton objectif : {self.goal}

Contexte : {self.backstory}

Instructions :
1. Utilise les informations de la base de connaissances pour répondre avec précision
2. Cite toujours tes sources
3. Si tu ne sais pas, dis-le clairement
4. Reste dans ton domaine d'expertise
5. Sois professionnel et précis

Réponds en français de manière claire et structurée."""
    
    def query_knowledge_base(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query the knowledge base"""
        try:
            results = self.rag_service.query(
                query_text=query,
                namespace=self.namespace,
                filters=filters,
                top_k=top_k
            )
            return results
        except Exception as e:
            logger.error(f"{self.name} query error: {str(e)}")
            return []
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process a query using the agent's configuration"""
        try:
            # Query knowledge base
            kb_results = self.query_knowledge_base(query)
            
            # Build context from results
            context_parts = [r["text"] for r in kb_results[:3]]
            full_context = "\n\n".join(context_parts)
            
            # Build response using system prompt
            response = self._generate_response(query, full_context, kb_results)
            
            # Update statistics in database
            self._update_statistics()
            
            return {
                "agent": self.name,
                "agent_id": self.id,
                "response": response,
                "sources": kb_results,
                "tool_calls": [],
                "system_prompt_used": self.system_prompt[:100] + "..."
            }
            
        except Exception as e:
            logger.error(f"Error processing query with {self.name}: {str(e)}")
            raise
    
    def _generate_response(self, query: str, context: str, sources: List[Dict]) -> str:
        """Generate response based on system prompt and context"""
        # In production, this would call an LLM with the system prompt
        # For now, we simulate a response
        
        response_parts = []
        
        # Add agent introduction
        response_parts.append(f"[{self.name}] {self.role}\n")
        
        # Add context summary
        if context:
            response_parts.append(f"Contexte pertinent trouvé dans la base de connaissances :\n{context[:500]}...\n")
        else:
            response_parts.append("Aucun contexte spécifique trouvé dans la base de connaissances.\n")
        
        # Add analysis based on role
        response_parts.append(f"\nAnalyse selon mon expertise ({self.role}) :\n")
        response_parts.append(self._role_specific_analysis(query))
        
        # Add sources
        if sources:
            response_parts.append(f"\n\nSources consultées : {len(sources)} documents")
        
        return "\n".join(response_parts)
    
    def _role_specific_analysis(self, query: str) -> str:
        """Generate role-specific analysis"""
        # This is a simplified version - in production, use LLM
        query_lower = query.lower()
        
        if "tax" in self.id.lower() or "fiscal" in self.role.lower():
            return """Points clés fiscaux :
- Vérifier les dates limites de déclaration
- Optimiser les déductions disponibles
- Assurer la conformité avec l'ARC et Revenu Québec
- Considérer les implications TPS/TVQ"""
        
        elif "accountant" in self.id.lower() or "comptable" in self.role.lower():
            return """Analyse comptable :
- Vérifier les écritures de journal
- Calculer les ratios financiers clés
- Assurer la conformité IFRS/ASPE
- Examiner la cohérence des données"""
        
        elif "forecast" in self.id.lower() or "prévision" in self.role.lower():
            return """Analyse prévisionnelle :
- Analyser les tendances historiques
- Modéliser les flux de trésorerie futurs
- Identifier les risques et opportunités
- Recommander des scénarios (optimiste, réaliste, pessimiste)"""
        
        elif "compliance" in self.id.lower() or "conformité" in self.role.lower():
            return """Vérification de conformité :
- Examiner les normes applicables
- Identifier les écarts potentiels
- Recommander des actions correctives
- Documenter les processus"""
        
        elif "audit" in self.id.lower():
            return """Procédures d'audit :
- Tester les contrôles internes
- Vérifier la substantiation
- Identifier les anomalies
- Recommander des améliorations"""
        
        else:
            return f"""Analyse selon mon rôle ({self.role}) :
- Examen approfondi de la question
- Recherche dans la documentation disponible
- Recommandations basées sur les meilleures pratiques
- Suivi et documentation"""
    
    def _update_statistics(self):
        """Update agent statistics in database"""
        try:
            with get_db() as db:
                agent_config = db.query(AgentConfig).filter(AgentConfig.id == self.id).first()
                if agent_config:
                    agent_config.query_count += 1
                    agent_config.last_query_time = datetime.now()
                    db.commit()
        except Exception as e:
            logger.error(f"Error updating statistics for {self.name}: {str(e)}")


class DynamicAgentOrchestrator:
    """Orchestrator that manages dynamic agents from database"""
    
    def __init__(self):
        self.agents_cache: Dict[str, DynamicAgent] = {}
        self._load_agents()
        logger.info(f"Initialized orchestrator with {len(self.agents_cache)} agents")
    
    def _load_agents(self):
        """Load all active agents from database"""
        try:
            with get_db() as db:
                configs = db.query(AgentConfig).filter(AgentConfig.is_active == True).all()
                
                for config in configs:
                    agent = DynamicAgent(config)
                    self.agents_cache[config.id] = agent
                    logger.info(f"Loaded agent: {config.name}")
                
        except Exception as e:
            logger.error(f"Error loading agents: {str(e)}")
            # Initialize with empty cache if database not ready
            self.agents_cache = {}
    
    def reload_agents(self):
        """Reload agents from database (hot-reload)"""
        logger.info("Reloading agents from database...")
        self.agents_cache.clear()
        self._load_agents()
    
    def get_agent(self, agent_id: str) -> Optional[DynamicAgent]:
        """Get agent by ID"""
        return self.agents_cache.get(agent_id)
    
    def list_agents(self) -> List[DynamicAgent]:
        """List all active agents"""
        return list(self.agents_cache.values())
    
    def route_query(self, query: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Route query to appropriate agent"""
        # If agent specified, use it
        if agent_id and agent_id in self.agents_cache:
            agent = self.agents_cache[agent_id]
            return agent.process_query(query)
        
        # Otherwise, use simple keyword routing
        agent = self._auto_select_agent(query)
        return agent.process_query(query)
    
    def _auto_select_agent(self, query: str) -> DynamicAgent:
        """Auto-select agent based on query keywords"""
        query_lower = query.lower()
        
        # Try to match by keywords
        for agent_id, agent in self.agents_cache.items():
            keywords = agent.metadata.get("keywords", [])
            if any(keyword.lower() in query_lower for keyword in keywords):
                return agent
        
        # Fallback to first agent
        if self.agents_cache:
            return list(self.agents_cache.values())[0]
        
        # If no agents, raise error
        raise ValueError("No agents available")
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        status_list = []
        for agent in self.agents_cache.values():
            status_list.append({
                "id": agent.id,
                "name": agent.name,
                "role": agent.role,
                "namespace": agent.namespace,
                "is_active": agent.is_active,
                "icon": agent.icon,
                "color": agent.color,
                "query_count": agent.query_count,
                "last_query": agent.last_query_time.isoformat() if agent.last_query_time else None
            })
        return status_list


def init_default_agents(db: Session):
    """Initialize default agents in database"""
    default_agents = [
        {
            "id": "AccountantAgent",
            "name": "Expert Comptable",
            "role": "Expert Comptable Certifié",
            "goal": "Analyser les données comptables, calculer les ratios financiers et produire des rapports conformes aux normes",
            "backstory": "Expert en comptabilité avec 15 ans d'expérience en normes IFRS et ASPE canadiennes. Spécialisé dans l'analyse financière et la production de rapports pour PME.",
            "namespace": "finance_accounting",
            "icon": "📊",
            "color": "#64ffda",
            "metadata": {"keywords": ["comptabilité", "accounting", "ratio", "bilan", "compte de résultat"]}
        },
        {
            "id": "TaxAgent",
            "name": "Spécialiste Fiscal",
            "role": "Expert en Fiscalité Canadienne",
            "goal": "Assurer la conformité fiscale fédérale et provinciale, optimiser les déductions et minimiser l'impôt légalement",
            "backstory": "Expert en fiscalité canadienne (T1, T2, TPS/TVQ) avec certification CPA. Connaissance approfondie de la Loi de l'impôt sur le revenu et des règlements provinciaux.",
            "namespace": "finance_tax",
            "icon": "💰",
            "color": "#f5b971",
            "metadata": {"keywords": ["tax", "fiscal", "impôt", "t1", "t2", "tps", "tvq", "déduction"]}
        },
        {
            "id": "ForecastAgent",
            "name": "Analyste Prévisionnel",
            "role": "Spécialiste en Modélisation Financière",
            "goal": "Créer des prévisions financières précises et analyser les tendances pour guider les décisions stratégiques",
            "backstory": "Spécialiste en modélisation financière et analyse prédictive avec expertise en cashflow, budgets et scénarios financiers.",
            "namespace": "finance_forecast",
            "icon": "📈",
            "color": "#71a6f5",
            "metadata": {"keywords": ["prévision", "forecast", "projection", "budget", "cashflow", "tendance"]}
        },
        {
            "id": "ComplianceAgent",
            "name": "Expert Conformité",
            "role": "Spécialiste en Conformité Réglementaire",
            "goal": "Assurer la conformité aux normes comptables, fiscales et réglementaires canadiennes",
            "backstory": "Expert en réglementation financière canadienne et internationale avec connaissance des normes CPA Canada, IFRS, ASPE et réglementations provinciales.",
            "namespace": "finance_compliance",
            "icon": "✅",
            "color": "#64ffda",
            "metadata": {"keywords": ["conformité", "compliance", "norme", "réglementation", "ifrs", "aspe"]}
        },
        {
            "id": "AuditAgent",
            "name": "Auditeur Financier",
            "role": "Auditeur Certifié",
            "goal": "Effectuer des audits rigoureux et identifier les anomalies pour assurer l'intégrité financière",
            "backstory": "Auditeur certifié avec expertise en détection de fraude, contrôles internes et procédures d'audit selon les normes canadiennes.",
            "namespace": "finance_audit",
            "icon": "🔍",
            "color": "#f57171",
            "metadata": {"keywords": ["audit", "vérification", "contrôle", "anomalie", "fraude"]}
        },
        {
            "id": "ReporterAgent",
            "name": "Générateur de Rapports",
            "role": "Expert en Communication Financière",
            "goal": "Synthétiser les informations financières et créer des rapports professionnels clairs et actionnables",
            "backstory": "Expert en communication financière et visualisation de données. Spécialisé dans la création de rapports exécutifs pour dirigeants et conseils d'administration.",
            "namespace": "default",
            "icon": "📄",
            "color": "#a8b2d1",
            "metadata": {"keywords": ["rapport", "report", "synthèse", "résumé", "présentation"]}
        }
    ]
    
    for agent_data in default_agents:
        existing = db.query(AgentConfig).filter(AgentConfig.id == agent_data["id"]).first()
        if not existing:
            agent = AgentConfig(**agent_data)
            db.add(agent)
            logger.info(f"Created default agent: {agent_data['name']}")
    
    db.commit()
    logger.info("Default agents initialized")
