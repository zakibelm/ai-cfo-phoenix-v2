"""
Agent System v3.0 - With OpenRouter Integration
Financial AI agents with RAG and LLM capabilities
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.rag_service import RAGService
from services.openrouter_service import openrouter_service

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents with OpenRouter integration"""
    
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
    
    def _build_prompt(self, query: str, rag_context: str, language: str = "fr") -> str:
        """Build prompt with RAG context"""
        lang_instruction = "Réponds en français de manière professionnelle" if language == "fr" else "Answer in English professionally"
        
        prompt = f"""Tu es {self.role}.

{self.backstory}

Objectif : {self.goal}

Contexte pertinent de la base de connaissances :
{rag_context}

Question : {query}

Instructions :
- {lang_instruction}
- Base ta réponse sur le contexte fourni
- Cite les sources quand pertinent
- Sois précis et professionnel
- Structure ta réponse clairement avec sections

Réponse :"""
        return prompt
    
    def process_query(
        self,
        query: str,
        context: Optional[str] = None,
        model: str = "gpt-4-turbo",
        language: str = "fr"
    ) -> Dict[str, Any]]:
        """Process query with RAG + LLM"""
        try:
            # 1. Query knowledge base
            kb_results = self.query_knowledge_base(query)
            
            # 2. Build RAG context
            if kb_results:
                rag_context = "\n\n".join([
                    f"Source {i+1} ({r.get('filename', 'unknown')}):\n{r['text']}"
                    for i, r in enumerate(kb_results[:3])
                ])
            else:
                rag_context = "Aucun document pertinent trouvé dans la base de connaissances."
            
            # 3. Build prompt
            prompt = self._build_prompt(query, rag_context, language)
            
            # 4. Call OpenRouter LLM
            llm_response = openrouter_service.generate(
                prompt=prompt,
                model=model,
                max_tokens=2000,
                temperature=0.7
            )
            
            response_text = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "agent": self.name,
                "response": response_text,
                "sources": kb_results,
                "model_used": model,
                "language": language,
                "tokens_used": llm_response.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"{self.name} process_query error: {str(e)}")
            return {
                "agent": self.name,
                "response": f"Erreur lors du traitement de la requête : {str(e)}",
                "sources": [],
                "error": str(e)
            }


class AccountantAgent(BaseAgent):
    """Agent specialized in accounting and bookkeeping"""
    
    def __init__(self):
        super().__init__(
            name="AccountantAgent",
            role="Expert Comptable Certifié CPA",
            goal="Analyser les données comptables, calculer les ratios financiers et produire des rapports conformes aux normes IFRS/ASPE",
            backstory="Expert en comptabilité avec 15 ans d'expérience en normes IFRS et ASPE canadiennes. Spécialisé dans l'analyse des états financiers, le calcul de ratios et la détection d'anomalies comptables."
        )
        self.namespace = "finance_accounting"


class TaxAgent(BaseAgent):
    """Agent specialized in Canadian tax compliance"""
    
    def __init__(self):
        super().__init__(
            name="TaxAgent",
            role="Spécialiste Fiscal Canadien Certifié",
            goal="Assurer la conformité fiscale fédérale et provinciale, optimiser les déductions et crédits d'impôt",
            backstory="Expert en fiscalité canadienne (T1, T2, TPS/TVQ) avec certification CPA. Connaissance approfondie de la Loi de l'impôt sur le revenu (LIR) et des lois provinciales."
        )
        self.namespace = "finance_tax"


class ForecastAgent(BaseAgent):
    """Agent specialized in financial forecasting"""
    
    def __init__(self):
        super().__init__(
            name="ForecastAgent",
            role="Analyste Prévisionnel Senior",
            goal="Créer des prévisions financières robustes et analyser les tendances pour anticiper les besoins futurs",
            backstory="Spécialiste en modélisation financière et analyse prédictive avec 10 ans d'expérience. Expert en projections de flux de trésorerie et analyse de scénarios."
        )
        self.namespace = "finance_forecast"


class ComplianceAgent(BaseAgent):
    """Agent specialized in regulatory compliance"""
    
    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            role="Expert en Conformité Réglementaire",
            goal="Assurer la conformité aux normes comptables, fiscales et réglementaires canadiennes et internationales",
            backstory="Expert en réglementation financière canadienne et internationale. Connaissance approfondie des normes IFRS, ASPE, et des exigences réglementaires de l'ARC et Revenu Québec."
        )
        self.namespace = "finance_compliance"


class AuditAgent(BaseAgent):
    """Agent specialized in auditing"""
    
    def __init__(self):
        super().__init__(
            name="AuditAgent",
            role="Auditeur Financier Certifié",
            goal="Effectuer des audits rigoureux, identifier les anomalies et recommander des améliorations des contrôles internes",
            backstory="Auditeur certifié avec expertise en détection de fraude et analyse forensique. 12 ans d'expérience en audit externe et interne."
        )
        self.namespace = "finance_audit"


class ReporterAgent(BaseAgent):
    """Agent specialized in report generation"""
    
    def __init__(self):
        super().__init__(
            name="ReporterAgent",
            role="Générateur de Rapports Professionnels",
            goal="Synthétiser les informations complexes et créer des rapports clairs et actionnables pour la direction",
            backstory="Expert en communication financière et visualisation de données. Spécialisé dans la création de rapports exécutifs et tableaux de bord."
        )
        self.namespace = "default"


class AgentOrchestrator:
    """Orchestrates multiple agents with OpenRouter"""
    
    def __init__(self):
        self.agents = {
            "AccountantAgent": AccountantAgent(),
            "TaxAgent": TaxAgent(),
            "ForecastAgent": ForecastAgent(),
            "ComplianceAgent": ComplianceAgent(),
            "AuditAgent": AuditAgent(),
            "ReporterAgent": ReporterAgent()
        }
        logger.info(f"Initialized {len(self.agents)} agents with OpenRouter integration")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(agent_name)
    
    def route_query(
        self,
        query: str,
        agent_name: Optional[str] = None,
        model: str = "gpt-4-turbo",
        language: str = "fr"
    ) -> Dict[str, Any]:
        """Route query to appropriate agent"""
        # If agent specified, use it
        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
            return agent.process_query(query, model=model, language=language)
        
        # Otherwise, use simple keyword routing
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["tax", "fiscal", "t1", "t2", "tps", "tvq", "impôt"]):
            agent = self.agents["TaxAgent"]
        elif any(word in query_lower for word in ["forecast", "prévision", "projection", "cashflow"]):
            agent = self.agents["ForecastAgent"]
        elif any(word in query_lower for word in ["audit", "vérification", "contrôle", "anomalie"]):
            agent = self.agents["AuditAgent"]
        elif any(word in query_lower for word in ["compliance", "conformité", "réglementation", "norme"]):
            agent = self.agents["ComplianceAgent"]
        elif any(word in query_lower for word in ["rapport", "report", "synthèse", "résumé"]):
            agent = self.agents["ReporterAgent"]
        else:
            agent = self.agents["AccountantAgent"]  # Default
        
        logger.info(f"Routing query to {agent.name}")
        return agent.process_query(query, model=model, language=language)
    
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


# Global instance
agent_orchestrator = AgentOrchestrator()

