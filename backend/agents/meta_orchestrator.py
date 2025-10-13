"""
MetaOrchestrator - Intelligent agent coordination and routing system
Supervises specialized agents, distributes tasks, validates coherence
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from agents.dynamic_agent_system import DynamicAgentOrchestrator, DynamicAgent
from services.openrouter_service import openrouter_service
from services.monitoring_service import monitoring_service
from services.resilience_service import get_circuit_breaker, fallback_handler
from services.i18n_service import i18n_service

logger = logging.getLogger(__name__)


class MetaOrchestrator:
    """
    Meta-orchestrator for intelligent agent coordination
    
    Features:
    - Intelligent task routing based on agent expertise and availability
    - Multi-agent collaboration for complex queries
    - Coherence validation across agent responses
    - Fallback mechanisms for unavailable agents
    - Jurisdiction-aware routing (country, province, regulations)
    - Load balancing and health monitoring
    """
    
    def __init__(self):
        """Initialize the meta-orchestrator"""
        self.agent_orchestrator = DynamicAgentOrchestrator()
        self.language = "fr"  # Default language
        
        # Agent priority matrix (higher = more priority)
        self.agent_priorities = {
            "AccountantAgent": 10,
            "TaxAgent": 10,
            "ForecastAgent": 8,
            "ComplianceAgent": 9,
            "AuditAgent": 9,
            "ReporterAgent": 7
        }
        
        # Jurisdiction mapping
        self.jurisdiction_agents = {
            "CA": ["TaxAgent", "ComplianceAgent", "AccountantAgent"],  # Canada
            "CA-QC": ["TaxAgent", "ComplianceAgent"],  # Quebec
            "CA-ON": ["TaxAgent", "ComplianceAgent"],  # Ontario
            "FR": ["TaxAgent", "ComplianceAgent"],  # France
            "US": ["TaxAgent", "ComplianceAgent"],  # USA
        }
        
        logger.info("MetaOrchestrator initialized")
    
    def set_language(self, language: str):
        """Set the working language"""
        if language in ["fr", "en"]:
            self.language = language
            logger.info(f"Language set to: {language}")
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine intent, required agents, and jurisdiction
        
        Args:
            query: User query
        
        Returns:
            Dict with intent analysis
        """
        query_lower = query.lower()
        
        # Detect intent keywords
        intents = {
            "tax": ["tax", "fiscal", "impôt", "t1", "t2", "tps", "tvq", "déduction", "crédit"],
            "accounting": ["comptable", "accounting", "ratio", "bilan", "compte de résultat", "ifrs", "aspe"],
            "forecast": ["prévision", "forecast", "budget", "cashflow", "projection", "scénario"],
            "compliance": ["conformité", "compliance", "norme", "réglementation", "audit"],
            "audit": ["audit", "vérification", "anomalie", "fraude", "contrôle"],
            "report": ["rapport", "report", "synthèse", "résumé", "présentation"]
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Detect jurisdiction
        jurisdiction = None
        jurisdiction_keywords = {
            "CA": ["canada", "canadian", "canadien"],
            "CA-QC": ["québec", "quebec", "qc"],
            "CA-ON": ["ontario", "on"],
            "FR": ["france", "français", "french"],
            "US": ["usa", "états-unis", "united states", "american"]
        }
        
        for jur, keywords in jurisdiction_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                jurisdiction = jur
                break
        
        # Map intents to agents
        intent_to_agent = {
            "tax": "TaxAgent",
            "accounting": "AccountantAgent",
            "forecast": "ForecastAgent",
            "compliance": "ComplianceAgent",
            "audit": "AuditAgent",
            "report": "ReporterAgent"
        }
        
        suggested_agents = [intent_to_agent[intent] for intent in detected_intents if intent in intent_to_agent]
        
        # If no specific intent detected, use general routing
        if not suggested_agents:
            suggested_agents = ["AccountantAgent"]  # Default
        
        return {
            "intents": detected_intents,
            "jurisdiction": jurisdiction,
            "suggested_agents": suggested_agents,
            "complexity": "complex" if len(detected_intents) > 1 else "simple",
            "requires_collaboration": len(detected_intents) > 1
        }
    
    def select_best_agent(
        self,
        suggested_agents: List[str],
        jurisdiction: Optional[str] = None
    ) -> Optional[DynamicAgent]:
        """
        Select the best available agent based on multiple criteria
        
        Args:
            suggested_agents: List of suggested agent IDs
            jurisdiction: Jurisdiction code (if applicable)
        
        Returns:
            Best agent or None
        """
        available_agents = self.agent_orchestrator.list_agents()
        
        # Filter by suggested agents
        candidates = [
            agent for agent in available_agents
            if agent.id in suggested_agents and agent.is_active
        ]
        
        if not candidates:
            logger.warning(f"No available agents from suggestions: {suggested_agents}")
            # Fallback to any active agent
            candidates = [agent for agent in available_agents if agent.is_active]
        
        if not candidates:
            logger.error("No active agents available")
            return None
        
        # Score agents
        scored_agents = []
        for agent in candidates:
            score = 0
            
            # Priority score
            score += self.agent_priorities.get(agent.id, 5)
            
            # Jurisdiction match
            if jurisdiction and agent.id in self.jurisdiction_agents.get(jurisdiction, []):
                score += 5
            
            # Health score (from monitoring)
            metrics = monitoring_service.get_agent_metrics(agent.id)
            if metrics:
                success_rate = metrics.get("success_rate", 0)
                score += (success_rate / 100) * 10  # Max 10 points
                
                # Penalize slow agents
                avg_time = metrics.get("avg_response_time", 0)
                if avg_time > 30:
                    score -= 3
                elif avg_time > 60:
                    score -= 5
            
            # Remote agent penalty (slightly prefer local)
            if agent.is_remote:
                score -= 2
            
            scored_agents.append((agent, score))
        
        # Sort by score (descending)
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        best_agent = scored_agents[0][0]
        logger.info(f"Selected agent: {best_agent.id} (score: {scored_agents[0][1]:.2f})")
        
        return best_agent
    
    def process_query(
        self,
        query: str,
        context: Optional[List[Dict[str, Any]]] = None,
        jurisdiction: Optional[str] = None,
        language: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a query with intelligent agent routing
        
        Args:
            query: User query
            context: RAG context documents
            jurisdiction: Jurisdiction code
            language: Language (fr/en)
            model: LLM model to use
        
        Returns:
            Dict with response and metadata
        """
        start_time = datetime.now()
        lang = language or self.language
        
        try:
            # Analyze query intent
            analysis = self.analyze_query_intent(query)
            logger.info(f"Query analysis: {analysis}")
            
            # Use provided jurisdiction or detected one
            jur = jurisdiction or analysis.get("jurisdiction")
            
            # Select best agent
            best_agent = self.select_best_agent(
                analysis["suggested_agents"],
                jur
            )
            
            if not best_agent:
                return {
                    "success": False,
                    "error": i18n_service.t("no_agents", lang),
                    "fallback": True
                }
            
            # Prepare enhanced query with jurisdiction context
            enhanced_query = query
            if jur:
                jur_context = i18n_service.t("jurisdiction", lang)
                enhanced_query = f"[{jur_context}: {jur}]\n\n{query}"
            
            # Use circuit breaker for agent call
            cb = get_circuit_breaker(f"agent_{best_agent.id}")
            
            try:
                # Process with selected agent
                result = cb.call(
                    best_agent.process_query,
                    enhanced_query,
                    context,
                    lang,
                    model
                )
                
                # Add meta information
                result["meta"] = {
                    "orchestrator": "MetaOrchestrator",
                    "selected_agent": best_agent.id,
                    "agent_name": best_agent.name,
                    "intent_analysis": analysis,
                    "jurisdiction": jur,
                    "language": lang,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "fallback": False
                }
                
                # Validate coherence if multiple intents
                if analysis["requires_collaboration"]:
                    result["meta"]["coherence_check"] = "Multi-intent query - consider consulting multiple agents"
                
                return result
                
            except Exception as e:
                logger.error(f"Agent {best_agent.id} failed: {str(e)}")
                
                # Try fallback agent
                fallback_agent = self._get_fallback_agent(best_agent.id, analysis["suggested_agents"])
                if fallback_agent:
                    logger.info(f"Trying fallback agent: {fallback_agent.id}")
                    result = fallback_agent.process_query(enhanced_query, context, lang, model)
                    result["meta"] = {
                        "orchestrator": "MetaOrchestrator",
                        "selected_agent": fallback_agent.id,
                        "agent_name": fallback_agent.name,
                        "fallback": True,
                        "original_agent": best_agent.id,
                        "error": str(e)
                    }
                    return result
                
                # No fallback available
                return fallback_handler.get_fallback("agent_response")
        
        except Exception as e:
            logger.error(f"MetaOrchestrator error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def _get_fallback_agent(
        self,
        failed_agent_id: str,
        suggested_agents: List[str]
    ) -> Optional[DynamicAgent]:
        """Get a fallback agent when primary agent fails"""
        # Remove failed agent from suggestions
        remaining = [a for a in suggested_agents if a != failed_agent_id]
        
        if remaining:
            return self.select_best_agent(remaining)
        
        # Try any active agent
        available = self.agent_orchestrator.list_agents()
        active = [a for a in available if a.is_active and a.id != failed_agent_id]
        
        if active:
            return active[0]
        
        return None
    
    def collaborate_agents(
        self,
        query: str,
        agent_ids: List[str],
        context: Optional[List[Dict[str, Any]]] = None,
        language: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collaborate multiple agents on a complex query
        
        Args:
            query: User query
            agent_ids: List of agent IDs to collaborate
            context: RAG context
            language: Language
            model: LLM model
        
        Returns:
            Combined response from all agents
        """
        lang = language or self.language
        responses = []
        
        for agent_id in agent_ids:
            agent = self.agent_orchestrator.get_agent(agent_id)
            if agent and agent.is_active:
                try:
                    result = agent.process_query(query, context, lang, model)
                    responses.append({
                        "agent_id": agent_id,
                        "agent_name": agent.name,
                        "response": result.get("response"),
                        "sources": result.get("sources", [])
                    })
                except Exception as e:
                    logger.error(f"Agent {agent_id} failed in collaboration: {str(e)}")
        
        if not responses:
            return fallback_handler.get_fallback("agent_response")
        
        # Synthesize responses with ReporterAgent
        reporter = self.agent_orchestrator.get_agent("ReporterAgent")
        if reporter:
            synthesis_prompt = self._build_synthesis_prompt(query, responses, lang)
            try:
                synthesis = reporter.process_query(synthesis_prompt, None, lang, model)
                return {
                    "success": True,
                    "response": synthesis.get("response"),
                    "collaboration": responses,
                    "meta": {
                        "orchestrator": "MetaOrchestrator",
                        "mode": "collaboration",
                        "agents_involved": agent_ids,
                        "language": lang
                    }
                }
            except Exception as e:
                logger.error(f"Synthesis failed: {str(e)}")
        
        # Fallback: return all responses
        return {
            "success": True,
            "responses": responses,
            "meta": {
                "orchestrator": "MetaOrchestrator",
                "mode": "collaboration",
                "agents_involved": agent_ids,
                "synthesis_failed": True
            }
        }
    
    def _build_synthesis_prompt(
        self,
        original_query: str,
        responses: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Build a synthesis prompt for ReporterAgent"""
        if language == "fr":
            prompt = f"""Synthétise les réponses suivantes de différents agents experts pour la question :

**Question** : {original_query}

**Réponses des agents** :

"""
            for resp in responses:
                prompt += f"\n### {resp['agent_name']}\n{resp['response']}\n"
            
            prompt += """
**Instructions** :
1. Crée une synthèse cohérente et complète
2. Élimine les redondances
3. Mets en évidence les points clés de chaque agent
4. Indique s'il y a des contradictions
5. Fournis une conclusion claire et actionnelle
"""
        else:
            prompt = f"""Synthesize the following responses from different expert agents for the question:

**Question**: {original_query}

**Agent responses**:

"""
            for resp in responses:
                prompt += f"\n### {resp['agent_name']}\n{resp['response']}\n"
            
            prompt += """
**Instructions**:
1. Create a coherent and comprehensive synthesis
2. Eliminate redundancies
3. Highlight key points from each agent
4. Indicate if there are contradictions
5. Provide a clear and actionable conclusion
"""
        
        return prompt
    
    def get_agent_health_status(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        agents = self.agent_orchestrator.list_agents()
        
        status = {
            "total_agents": len(agents),
            "active_agents": sum(1 for a in agents if a.is_active),
            "inactive_agents": sum(1 for a in agents if not a.is_active),
            "remote_agents": sum(1 for a in agents if a.is_remote),
            "local_agents": sum(1 for a in agents if not a.is_remote),
            "agents": []
        }
        
        for agent in agents:
            metrics = monitoring_service.get_agent_metrics(agent.id)
            agent_status = {
                "id": agent.id,
                "name": agent.name,
                "active": agent.is_active,
                "remote": agent.is_remote,
                "metrics": metrics
            }
            status["agents"].append(agent_status)
        
        return status


# Global instance
meta_orchestrator = MetaOrchestrator()
