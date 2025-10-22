"""
Complete Agent System v3.0 - 10 Financial AI Agents
Optimized prompts with Cartels++ methodology
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.rag_service import RAGService
from services.openrouter_service import openrouter_service
from services.i18n_service import i18n_service

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents with optimized prompt engineering"""
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        constraints: List[str],
        deliverables: List[str]
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.constraints = constraints
        self.deliverables = deliverables
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
        """Query RAG knowledge base"""
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
    
    def _build_optimized_prompt(
        self,
        query: str,
        rag_context: str,
        language: str = "fr",
        jurisdiction: str = "CA"
    ) -> str:
        """Build optimized prompt (Cartels++ methodology - condensed)"""
        
        # Language-specific instructions
        lang_map = {
            "fr": "Réponds en français professionnel",
            "en": "Answer in professional English"
        }
        lang_instruction = lang_map.get(language, lang_map["fr"])
        
        # Jurisdiction context
        jurisdiction_context = self._get_jurisdiction_context(jurisdiction)
        
        # Condensed prompt (300-500 tokens)
        prompt = f"""**RÔLE** : {self.role}
**EXPERTISE** : {self.backstory}

**OBJECTIF** : {self.goal}

**JURIDICTION** : {jurisdiction_context}

**CONTEXTE RAG** :
{rag_context[:800]}

**CONTRAINTES** :
{chr(10).join(f'- {c}' for c in self.constraints[:3])}

**LIVRABLES ATTENDUS** :
{chr(10).join(f'{i+1}. {d}' for i, d in enumerate(self.deliverables[:3]))}

**QUESTION** : {query}

**INSTRUCTIONS** :
- {lang_instruction}
- Base-toi sur le contexte RAG fourni
- Cite les sources pertinentes
- Structure ta réponse clairement
- Fournis des chiffres concrets

**RÉPONSE** :"""
        
        return prompt
    
    def _get_jurisdiction_context(self, jurisdiction: str) -> str:
        """Get jurisdiction-specific context"""
        contexts = {
            "CA": "Canada (Fédéral) - LIR, T1/T2, TPS 5%, ARC",
            "CA-QC": "Québec - LIR + Loi QC, TP-1/CO-17, TPS+TVQ 14.975%, ARC+Revenu QC",
            "CA-ON": "Ontario - LIR, T1/T2, HST 13%, ARC",
            "FR": "France - CGI, PCG, IR/IS, TVA 20%, DGFiP",
            "US": "États-Unis - IRC, 1040/1120, Sales Tax, IRS"
        }
        return contexts.get(jurisdiction, contexts["CA"])
    
    def process_query(
        self,
        query: str,
        model: str = "gpt-4-turbo",
        language: str = "fr",
        jurisdiction: str = "CA",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process query with RAG + LLM"""
        try:
            # 1. Query RAG
            filters = {"country": jurisdiction.split("-")[0]} if jurisdiction else None
            kb_results = self.query_knowledge_base(query, filters=filters)
            
            # 2. Build RAG context
            if kb_results:
                rag_context = "\n\n".join([
                    f"[Source {i+1}: {r.get('filename', 'N/A')}]\n{r['text'][:300]}"
                    for i, r in enumerate(kb_results[:3])
                ])
            else:
                rag_context = i18n_service.translate("no_relevant_documents", language)
            
            # 3. Build optimized prompt
            prompt = self._build_optimized_prompt(query, rag_context, language, jurisdiction)
            
            # 4. Call OpenRouter
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
                "jurisdiction": jurisdiction,
                "tokens_used": llm_response.get("usage", {}),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"{self.name} error: {str(e)}")
            return {
                "agent": self.name,
                "response": f"Erreur: {str(e)}",
                "sources": [],
                "success": False,
                "error": str(e)
            }


# ==================== EXISTING AGENTS (Optimized) ====================

class AccountantAgent(BaseAgent):
    """Accounting & Bookkeeping Expert"""
    
    def __init__(self):
        super().__init__(
            name="AccountantAgent",
            role="Expert Comptable Certifié CPA",
            goal="Produire le grand livre ajusté, états financiers et journal d'anomalies",
            backstory="15 ans d'expérience IFRS/ASPE. Expert en analyse états financiers, ratios, détection anomalies.",
            constraints=[
                "Actif = Passif (équilibre obligatoire)",
                "Toute correction doit être tracée (audit trail)",
                "Respecter plan de comptes et normes comptables"
            ],
            deliverables=[
                "Grand livre ajusté avec réconciliations",
                "États financiers (Bilan, Résultats, Flux)",
                "Journal d'anomalies avec corrections proposées"
            ]
        )
        self.namespace = "finance_accounting"


class TaxAgent(BaseAgent):
    """Canadian Tax Specialist"""
    
    def __init__(self):
        super().__init__(
            name="TaxAgent",
            role="Spécialiste Fiscal Canadien Certifié",
            goal="Rapport d'optimisation fiscale + plan de conformité avec simulation d'impact",
            backstory="Expert fiscalité canadienne (T1, T2, TPS/TVQ). Connaissance LIR et lois provinciales.",
            constraints=[
                "Respect strict des lois fiscales",
                "Chaque proposition doit avoir simulation chiffrée",
                "Aucune stratégie non justifiée légalement"
            ],
            deliverables=[
                "Postes fiscalement optimisables identifiés",
                "Simulation d'impact pour chaque stratégie",
                "Plan de mise en œuvre priorisé (coût/ROI/risque)"
            ]
        )
        self.namespace = "finance_tax"


class ForecastAgent(BaseAgent):
    """Financial Forecasting Specialist"""
    
    def __init__(self):
        super().__init__(
            name="ForecastAgent",
            role="Analyste Prévisionnel Senior",
            goal="Matrice de scénarios (optimiste/médian/pessimiste) + plan de contingence",
            backstory="10 ans en modélisation financière. Expert projections flux de trésorerie et analyse scénarios.",
            constraints=[
                "Scénarios cohérents et comparables entre eux",
                "Limiter variables non expliquées",
                "Respecter hypothèses macro (croissance, inflation, taux)"
            ],
            deliverables=[
                "3 scénarios avec drivers critiques identifiés",
                "Indicateurs clés (cash-flow, marge, point mort)",
                "Recommandations de réallocation/ajustements"
            ]
        )
        self.namespace = "finance_forecast"


class ComplianceAgent(BaseAgent):
    """Regulatory Compliance Expert"""
    
    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            role="Expert Conformité Réglementaire",
            goal="Assurer conformité normes comptables, fiscales et réglementaires",
            backstory="Expert réglementation canadienne/internationale. Connaissance IFRS, ASPE, ARC, Revenu QC.",
            constraints=[
                "Classement risques par gravité",
                "Fournir preuves/traces pour chaque anomalie",
                "Ne pas proposer corrections illégales"
            ],
            deliverables=[
                "Rapport risques-anomalies-conformité",
                "Mesures correctives proposées",
                "Tableau de bord de suivi"
            ]
        )
        self.namespace = "finance_compliance"


class AuditAgent(BaseAgent):
    """Financial Auditor"""
    
    def __init__(self):
        super().__init__(
            name="AuditAgent",
            role="Auditeur Financier Certifié",
            goal="Rapport risques-anomalies-conformité avec propositions correctives",
            backstory="12 ans audit externe/interne. Expert détection fraude et analyse forensique.",
            constraints=[
                "Classement risques par gravité",
                "Preuves/traces pour chaque anomalie",
                "Propositions correctives conformes"
            ],
            deliverables=[
                "Analyse flux et rapports avec incohérences",
                "Risques classés par domaine",
                "Tableau de bord de suivi des mesures"
            ]
        )
        self.namespace = "finance_audit"


class ReporterAgent(BaseAgent):
    """Professional Report Generator"""
    
    def __init__(self):
        super().__init__(
            name="ReporterAgent",
            role="Générateur de Rapports Professionnels",
            goal="Rapports clairs, tableaux de bord, présentations pour dirigeants/investisseurs",
            backstory="Expert communication financière et visualisation données. Spécialisé rapports exécutifs.",
            constraints=[
                "Simplicité + clarté",
                "Aligné aux priorités stratégiques",
                "Aucun biais/omission"
            ],
            deliverables=[
                "Résumé exécutif + notes explicatives",
                "Visuels (tableaux, graphiques)",
                "Cohérence texte-chiffres vérifiée"
            ]
        )
        self.namespace = "default"


# ==================== NEW AGENTS ====================

class InvestmentAgent(BaseAgent):
    """Investment & Asset Management Specialist"""
    
    def __init__(self):
        super().__init__(
            name="InvestmentAgent",
            role="Gestionnaire d'Actifs Senior",
            goal="Stratégie optimale de portefeuille + recommandations d'investissement/cession",
            backstory="Expert gestion de portefeuille. 15 ans analyse marché et santé financière entreprises.",
            constraints=[
                "Risque/rendement mesurables",
                "Diversification minimale selon seuil",
                "Cohérence avec stratégie globale"
            ],
            deliverables=[
                "Évaluation patrimoine existant",
                "Opportunités identifiées avec projections",
                "Recommandations ajustements (achat, vente, couverture)"
            ]
        )
        self.namespace = "finance_investment"


class CommsAgent(BaseAgent):
    """Financial Communication Specialist"""
    
    def __init__(self):
        super().__init__(
            name="CommsAgent",
            role="Spécialiste Communication Financière",
            goal="Rapports financiers, mises à jour investisseurs, communications internes",
            backstory="Expert communication financière. 10 ans création rapports pour investisseurs et direction.",
            constraints=[
                "Clarté et précision",
                "Alignement avec stratégie globale",
                "Transparence totale"
            ],
            deliverables=[
                "Rapports financiers structurés",
                "Mises à jour pour investisseurs",
                "Communications internes ciblées"
            ]
        )
        self.namespace = "finance_comms"


class DerivativePricingAgent(BaseAgent):
    """Derivative Pricing & Risk Analysis Specialist"""
    
    def __init__(self):
        super().__init__(
            name="DerivativePricingAgent",
            role="Expert Produits Dérivés et Risques",
            goal="Stratégies de couverture + simulation stress test + tableau de risque",
            backstory="Expert gestion risques. Spécialisé tarification dérivés complexes et analyse profils de risque.",
            constraints=[
                "Méthodologies reconnues (VaR, stress test)",
                "Transparence dans hypothèses",
                "Pas d'exposition excessive non justifiée"
            ],
            deliverables=[
                "Expositions identifiées (marché, crédit, liquidité)",
                "Scénarios de stress appliqués",
                "Instruments de couverture proposés avec simulations"
            ]
        )
        self.namespace = "finance_derivatives"


class SupervisorAgent(BaseAgent):
    """Quality Assurance & Conformity Supervisor"""
    
    def __init__(self):
        super().__init__(
            name="SupervisorAgent",
            role="Superviseur Qualité et Conformité",
            goal="S'assurer que toutes instructions sont suivies et qualité du résultat répond aux normes",
            backstory="Expert supervision stratégique. Supervise collaboration entre agents et valide cohérence.",
            constraints=[
                "Cohérence interne entre tous rapports",
                "Priorisation claire",
                "Justification stratégique pour chaque décision"
            ],
            deliverables=[
                "Validation alignement entre propositions",
                "Décisions validées avec priorités",
                "Feuille de route stratégique globale"
            ]
        )
        self.namespace = "default"


# ==================== ORACLE CFO (Enhanced MetaOrchestrator) ====================

class OracleCFO:
    """
    Oracle CFO - Master Orchestrator
    Coordinates all 10 specialized agents with intelligent routing
    """
    
    def __init__(self):
        self.agents = {
            "AccountantAgent": AccountantAgent(),
            "TaxAgent": TaxAgent(),
            "ForecastAgent": ForecastAgent(),
            "ComplianceAgent": ComplianceAgent(),
            "AuditAgent": AuditAgent(),
            "ReporterAgent": ReporterAgent(),
            "InvestmentAgent": InvestmentAgent(),
            "CommsAgent": CommsAgent(),
            "DerivativePricingAgent": DerivativePricingAgent(),
            "SupervisorAgent": SupervisorAgent()
        }
        logger.info(f"Oracle CFO initialized with {len(self.agents)} agents")
    
    def route_query(
        self,
        query: str,
        agent_name: Optional[str] = None,
        model: str = "gpt-4-turbo",
        language: str = "fr",
        jurisdiction: str = "CA"
    ) -> Dict[str, Any]:
        """Intelligent query routing"""
        
        # If agent specified, use it
        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
            logger.info(f"Oracle CFO: Routing to specified agent {agent_name}")
            return agent.process_query(query, model, language, jurisdiction)
        
        # Otherwise, intelligent routing based on keywords
        query_lower = query.lower()
        
        routing_rules = [
            (["tax", "fiscal", "t1", "t2", "tps", "tvq", "impôt"], "TaxAgent"),
            (["forecast", "prévision", "projection", "cashflow", "flux"], "ForecastAgent"),
            (["audit", "vérification", "contrôle", "anomalie", "fraude"], "AuditAgent"),
            (["compliance", "conformité", "réglementation", "norme"], "ComplianceAgent"),
            (["invest", "investissement", "portefeuille", "actif"], "InvestmentAgent"),
            (["dérivé", "derivative", "risque", "couverture", "hedge"], "DerivativePricingAgent"),
            (["rapport", "report", "communication", "présentation"], "CommsAgent"),
            (["supervision", "qualité", "validation", "cohérence"], "SupervisorAgent"),
            (["comptab", "accounting", "grand livre", "bilan"], "AccountantAgent")
        ]
        
        for keywords, agent_name in routing_rules:
            if any(kw in query_lower for kw in keywords):
                agent = self.agents[agent_name]
                logger.info(f"Oracle CFO: Intelligent routing to {agent_name}")
                return agent.process_query(query, model, language, jurisdiction)
        
        # Default: AccountantAgent
        logger.info("Oracle CFO: Default routing to AccountantAgent")
        return self.agents["AccountantAgent"].process_query(query, model, language, jurisdiction)
    
    def collaborate_agents(
        self,
        query: str,
        agent_ids: List[str],
        model: str = "gpt-4-turbo",
        language: str = "fr",
        jurisdiction: str = "CA"
    ) -> Dict[str, Any]:
        """Multi-agent collaboration"""
        
        results = []
        for agent_id in agent_ids:
            if agent_id in self.agents:
                result = self.agents[agent_id].process_query(query, model, language, jurisdiction)
                results.append(result)
        
        # Synthesize with ReporterAgent
        synthesis_query = f"Synthétise les analyses suivantes:\n\n" + "\n\n".join([
            f"**{r['agent']}**:\n{r['response'][:500]}"
            for r in results if r.get('success')
        ])
        
        synthesis = self.agents["ReporterAgent"].process_query(
            synthesis_query, model, language, jurisdiction
        )
        
        return {
            "collaboration": True,
            "agents_consulted": agent_ids,
            "individual_results": results,
            "synthesis": synthesis,
            "model_used": model,
            "language": language,
            "jurisdiction": jurisdiction
        }
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        status_list = []
        for agent in self.agents.values():
            status_list.append({
                "name": agent.name,
                "role": agent.role,
                "namespace": agent.namespace,
                "query_count": agent.query_count,
                "last_query": agent.last_query_time.isoformat() if agent.last_query_time else None,
                "constraints_count": len(agent.constraints),
                "deliverables_count": len(agent.deliverables)
            })
        return status_list
    
    def validate_coherence(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate coherence between agent responses (SupervisorAgent)"""
        
        validation_query = f"""Valide la cohérence entre ces analyses:

{chr(10).join([f"**{r['agent']}**: {r['response'][:300]}" for r in results if r.get('success')])}

Identifie:
1. Contradictions
2. Synergies
3. Zones d'incertitude
4. Recommandations consolidées"""
        
        return self.agents["SupervisorAgent"].process_query(validation_query)


# Global instance
oracle_cfo = OracleCFO()

