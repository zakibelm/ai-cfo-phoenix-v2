import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from services.rag_service import RAGService

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.rag_service = RAGService()
        self.namespace = "default"
        self.query_count = 0
        self.last_query_time: Optional[datetime] = None
    
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
            self.query_count += 1
            self.last_query_time = datetime.now()
            return results
        except Exception as e:
            logger.error(f"{self.name} query error: {str(e)}")
            return []
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process a query - to be implemented by subclasses"""
        raise NotImplementedError


class AccountantAgent(BaseAgent):
    """Agent specialized in accounting and bookkeeping"""
    
    def __init__(self):
        super().__init__(
            name="AccountantAgent",
            role="Expert Comptable",
            goal="Analyser les données comptables, calculer les ratios financiers et produire des rapports",
            backstory="Expert en comptabilité avec 15 ans d'expérience en normes IFRS et ASPE canadiennes"
        )
        self.namespace = "finance_accounting"
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process accounting-related queries"""
        # Query knowledge base
        kb_results = self.query_knowledge_base(query, filters={"country": "CA"})
        
        # Build context from results
        context_parts = [r["text"] for r in kb_results[:3]]
        full_context = "\n\n".join(context_parts)
        
        # Simulate agent reasoning (in production, this would call an LLM)
        response = f"""En tant qu'expert comptable, voici mon analyse :

Contexte pertinent trouvé dans la base de connaissances :
{full_context[:500]}...

Recommandations :
1. Vérifier la conformité avec les normes IFRS/ASPE
2. Analyser les ratios de liquidité et de solvabilité
3. Examiner les écritures de journal pour détecter les anomalies

Sources consultées : {len(kb_results)} documents"""
        
        return {
            "agent": self.name,
            "response": response,
            "sources": kb_results,
            "tool_calls": []
        }


class TaxAgent(BaseAgent):
    """Agent specialized in Canadian tax compliance"""
    
    def __init__(self):
        super().__init__(
            name="TaxAgent",
            role="Spécialiste Fiscal Canadien",
            goal="Assurer la conformité fiscale fédérale et provinciale, optimiser les déductions",
            backstory="Expert en fiscalité canadienne (T1, T2, TPS/TVQ) avec certification CPA"
        )
        self.namespace = "finance_tax"
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process tax-related queries"""
        kb_results = self.query_knowledge_base(query, filters={"country": "CA"})
        
        context_parts = [r["text"] for r in kb_results[:3]]
        full_context = "\n\n".join(context_parts)
        
        response = f"""Analyse fiscale canadienne :

Réglementation applicable :
{full_context[:500]}...

Points clés :
- Vérifier les dates limites de déclaration (T1: 30 avril, T2: 6 mois après fin d'exercice)
- Optimiser les déductions fiscales disponibles
- Assurer la conformité TPS/TVQ
- Considérer les crédits d'impôt provinciaux

Références : {len(kb_results)} documents fiscaux consultés"""
        
        return {
            "agent": self.name,
            "response": response,
            "sources": kb_results,
            "tool_calls": []
        }


class ForecastAgent(BaseAgent):
    """Agent specialized in financial forecasting"""
    
    def __init__(self):
        super().__init__(
            name="ForecastAgent",
            role="Analyste Prévisionnel",
            goal="Créer des prévisions financières et analyser les tendances",
            backstory="Spécialiste en modélisation financière et analyse prédictive"
        )
        self.namespace = "finance_forecast"
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process forecasting queries"""
        kb_results = self.query_knowledge_base(query)
        
        response = f"""Analyse prévisionnelle :

Méthodologie :
- Analyse des tendances historiques
- Modélisation des flux de trésorerie
- Scénarios (optimiste, réaliste, pessimiste)

Recommandations :
1. Surveiller les indicateurs clés de performance
2. Ajuster les prévisions mensuellement
3. Maintenir une réserve de trésorerie

Données analysées : {len(kb_results)} sources"""
        
        return {
            "agent": self.name,
            "response": response,
            "sources": kb_results,
            "tool_calls": []
        }


class ComplianceAgent(BaseAgent):
    """Agent specialized in regulatory compliance"""
    
    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            role="Expert en Conformité Réglementaire",
            goal="Assurer la conformité aux normes et réglementations",
            backstory="Expert en réglementation financière canadienne et internationale"
        )
        self.namespace = "finance_compliance"
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process compliance queries"""
        kb_results = self.query_knowledge_base(query)
        
        response = f"""Analyse de conformité :

Normes applicables :
- IFRS / ASPE
- Réglementations CPA Canada
- Lois provinciales

Vérifications requises :
1. Audit des processus
2. Documentation complète
3. Formation continue du personnel

Documents de référence : {len(kb_results)}"""
        
        return {
            "agent": self.name,
            "response": response,
            "sources": kb_results,
            "tool_calls": []
        }


class AuditAgent(BaseAgent):
    """Agent specialized in auditing"""
    
    def __init__(self):
        super().__init__(
            name="AuditAgent",
            role="Auditeur Financier",
            goal="Effectuer des audits et identifier les anomalies",
            backstory="Auditeur certifié avec expertise en détection de fraude"
        )
        self.namespace = "finance_audit"
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process audit queries"""
        kb_results = self.query_knowledge_base(query)
        
        response = f"""Rapport d'audit :

Procédures d'audit :
- Vérification des contrôles internes
- Test de substantiation
- Analyse des anomalies

Recommandations :
1. Renforcer les contrôles
2. Documenter les processus
3. Former le personnel

Sources consultées : {len(kb_results)}"""
        
        return {
            "agent": self.name,
            "response": response,
            "sources": kb_results,
            "tool_calls": []
        }


class ReporterAgent(BaseAgent):
    """Agent specialized in report generation"""
    
    def __init__(self):
        super().__init__(
            name="ReporterAgent",
            role="Générateur de Rapports",
            goal="Synthétiser les informations et créer des rapports professionnels",
            backstory="Expert en communication financière et visualisation de données"
        )
        self.namespace = "default"
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Process reporting queries"""
        kb_results = self.query_knowledge_base(query)
        
        response = f"""Rapport synthétique :

Résumé exécutif :
Les analyses effectuées par les agents spécialisés ont été compilées.

Sections du rapport :
1. Situation financière actuelle
2. Conformité et risques
3. Prévisions et recommandations

Le rapport complet est disponible en PDF.

Données sources : {len(kb_results)} documents"""
        
        return {
            "agent": self.name,
            "response": response,
            "sources": kb_results,
            "tool_calls": []
        }


class AgentOrchestrator:
    """Orchestrates multiple agents"""
    
    def __init__(self):
        self.agents = {
            "AccountantAgent": AccountantAgent(),
            "TaxAgent": TaxAgent(),
            "ForecastAgent": ForecastAgent(),
            "ComplianceAgent": ComplianceAgent(),
            "AuditAgent": AuditAgent(),
            "ReporterAgent": ReporterAgent()
        }
        logger.info(f"Initialized {len(self.agents)} agents")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(agent_name)
    
    def route_query(self, query: str, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Route query to appropriate agent"""
        # If agent specified, use it
        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
            return agent.process_query(query)
        
        # Otherwise, use simple keyword routing
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["tax", "fiscal", "t1", "t2", "tps", "tvq"]):
            agent = self.agents["TaxAgent"]
        elif any(word in query_lower for word in ["forecast", "prévision", "projection"]):
            agent = self.agents["ForecastAgent"]
        elif any(word in query_lower for word in ["audit", "vérification", "contrôle"]):
            agent = self.agents["AuditAgent"]
        elif any(word in query_lower for word in ["compliance", "conformité", "réglementation"]):
            agent = self.agents["ComplianceAgent"]
        elif any(word in query_lower for word in ["rapport", "report", "synthèse"]):
            agent = self.agents["ReporterAgent"]
        else:
            agent = self.agents["AccountantAgent"]  # Default
        
        return agent.process_query(query)
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        status_list = []
        for agent in self.agents.values():
            status_list.append({
                "name": agent.name,
                "role": agent.role,
                "namespace": agent.namespace,
                "query_count": agent.query_count,
                "last_query": agent.last_query_time.isoformat() if agent.last_query_time else None
            })
        return status_list
