#!/usr/bin/env python3
"""
AI CFO Suite Phoenix - Backend Simplifié pour Tests
Version minimale fonctionnelle pour validation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

# Configuration simplifiée
app = FastAPI(
    title="AI CFO Suite Phoenix",
    description="Suite IA financière multi-agents",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "fr"
    jurisdiction: Optional[str] = "CA-QC"
    model: Optional[str] = "mistralai/mistral-7b-instruct"
    agent_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    agent: str
    timestamp: str
    sources: List[str] = []
    success: bool = True

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

class Agent(BaseModel):
    id: str
    name: str
    role: str
    is_active: bool
    query_count: int = 0
    last_query: Optional[str] = None

# Données de démo
DEMO_AGENTS = [
    Agent(
        id="TaxAgent",
        name="Expert Fiscal",
        role="Spécialiste en fiscalité canadienne et québécoise",
        is_active=True
    ),
    Agent(
        id="AccountantAgent", 
        name="Expert Comptable",
        role="Spécialiste en comptabilité IFRS et ASPE",
        is_active=True
    ),
    Agent(
        id="ForecastAgent",
        name="Analyste Prévisionnel",
        role="Expert en prévisions financières et cashflow",
        is_active=True
    ),
    Agent(
        id="ComplianceAgent",
        name="Expert Conformité", 
        role="Spécialiste en conformité réglementaire",
        is_active=True
    ),
    Agent(
        id="AuditAgent",
        name="Auditeur IA",
        role="Expert en audit et détection d'anomalies",
        is_active=True
    ),
    Agent(
        id="ReporterAgent",
        name="Générateur de Rapports",
        role="Spécialiste en synthèse et reporting",
        is_active=True
    )
]

def get_demo_response(query: str, agent_id: str = None, language: str = "fr") -> str:
    """Génère une réponse de démonstration basée sur la requête"""
    query_lower = query.lower()
    
    if "tps" in query_lower or "gst" in query_lower:
        if language == "en":
            return """
**GST in Canada**:
- Rate: 5%
- Filing frequency: Quarterly or annually based on revenue
- Deadline: 15th of the month following the reporting period
- Refunds available for businesses

This is a demo response from AI CFO Suite Phoenix backend.
            """.strip()
        else:
            return """
**TPS au Canada** :
- Taux : 5%
- Période de déclaration : Trimestrielle ou annuelle selon le chiffre d'affaires
- Date limite : Le 15 du mois suivant la fin de la période
- Remboursement possible pour les entreprises

Ceci est une réponse de démonstration du backend AI CFO Suite Phoenix.
            """.strip()
    
    elif "tvq" in query_lower:
        return """
**TVQ au Québec** :
- Taux : 9,975%
- Combiné avec TPS : 14,975% total
- Déclaration harmonisée avec Revenu Québec
- Remboursement pour les entreprises exportatrices

Ceci est une réponse de démonstration du backend AI CFO Suite Phoenix.
        """.strip()
    
    elif "obligation" in query_lower and "pme" in query_lower:
        return """
**Obligations fiscales PME au Québec** :

1. **Fédéral (ARC)** :
   - T2 (Corporations) : Dans les 6 mois de fin d'année fiscale
   - TPS : Trimestrielle ou annuelle

2. **Provincial (RQ)** :
   - CO-17 : Dans les 6 mois de fin d'année fiscale
   - TVQ : Harmonisée avec TPS

3. **Obligations employeurs** :
   - Remises mensuelles : T4, Relevé 1
   - Assurance emploi, RRQ, RQAP

Ceci est une réponse de démonstration du backend AI CFO Suite Phoenix.
        """.strip()
    
    else:
        agent_name = agent_id if agent_id else "MetaOrchestrator"
        if language == "en":
            return f"""
Hello! I am the {agent_name} from AI CFO Suite Phoenix.

Your query: "{query}"

This is a demo response showing that the backend is working correctly. In a full implementation, I would:

1. Analyze your financial query using advanced AI
2. Search through your uploaded documents using RAG
3. Provide precise, jurisdiction-specific advice
4. Cite relevant sources and regulations

Available agents:
- TaxAgent: Tax and fiscal expertise
- AccountantAgent: Accounting standards (IFRS, ASPE, GAAP)
- ForecastAgent: Financial forecasting and cash flow
- ComplianceAgent: Regulatory compliance
- AuditAgent: Audit and anomaly detection
- ReporterAgent: Report generation and synthesis

The backend is running successfully! 🚀
            """.strip()
        else:
            return f"""
Bonjour ! Je suis l'{agent_name} d'AI CFO Suite Phoenix.

Votre requête : "{query}"

Ceci est une réponse de démonstration montrant que le backend fonctionne correctement. Dans une implémentation complète, je :

1. Analyserais votre requête financière avec une IA avancée
2. Rechercherais dans vos documents téléchargés via RAG
3. Fournirais des conseils précis et spécifiques à votre juridiction
4. Citerais les sources et réglementations pertinentes

Agents disponibles :
- TaxAgent : Expertise fiscale et taxation
- AccountantAgent : Normes comptables (IFRS, ASPE, GAAP)
- ForecastAgent : Prévisions financières et cashflow
- ComplianceAgent : Conformité réglementaire
- AuditAgent : Audit et détection d'anomalies
- ReporterAgent : Génération de rapports et synthèse

Le backend fonctionne avec succès ! 🚀
            """.strip()

# Routes API

@app.get("/", response_model=Dict[str, str])
async def root():
    return {
        "message": "AI CFO Suite Phoenix API",
        "version": "3.0.0",
        "status": "running"
    }

@app.get("/api/v1/monitoring/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="3.0.0",
        services={
            "api": "running",
            "database": "simulated",
            "vector_db": "simulated",
            "cache": "simulated",
            "storage": "simulated"
        }
    )

@app.get("/api/v1/agents", response_model=Dict[str, List[Agent]])
async def list_agents():
    """Liste tous les agents disponibles"""
    return {"agents": DEMO_AGENTS}

@app.get("/api/v1/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Récupère un agent spécifique"""
    for agent in DEMO_AGENTS:
        if agent.id == agent_id:
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")

@app.post("/api/v1/meta/query", response_model=QueryResponse)
async def meta_query(request: QueryRequest):
    """MetaOrchestrator - Route les requêtes vers le bon agent"""
    
    # Simulation du routing intelligent
    agent_id = "MetaOrchestrator"
    if "tax" in request.query.lower() or "tps" in request.query.lower() or "tvq" in request.query.lower():
        agent_id = "TaxAgent"
    elif "comptab" in request.query.lower() or "account" in request.query.lower():
        agent_id = "AccountantAgent"
    elif "prévision" in request.query.lower() or "forecast" in request.query.lower():
        agent_id = "ForecastAgent"
    elif "conformité" in request.query.lower() or "compliance" in request.query.lower():
        agent_id = "ComplianceAgent"
    elif "audit" in request.query.lower():
        agent_id = "AuditAgent"
    elif "rapport" in request.query.lower() or "report" in request.query.lower():
        agent_id = "ReporterAgent"
    
    response_text = get_demo_response(request.query, agent_id, request.language)
    
    return QueryResponse(
        response=response_text,
        agent=agent_id,
        timestamp=datetime.now().isoformat(),
        sources=["Demo Knowledge Base", "AI CFO Suite Phoenix v3.0"],
        success=True
    )

@app.post("/api/v1/agents/{agent_id}/query", response_model=QueryResponse)
async def agent_query(agent_id: str, request: QueryRequest):
    """Requête directe vers un agent spécifique"""
    
    # Vérifier que l'agent existe
    agent_exists = any(agent.id == agent_id for agent in DEMO_AGENTS)
    if not agent_exists:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    response_text = get_demo_response(request.query, agent_id, request.language)
    
    return QueryResponse(
        response=response_text,
        agent=agent_id,
        timestamp=datetime.now().isoformat(),
        sources=[f"{agent_id} Knowledge Base", "AI CFO Suite Phoenix v3.0"],
        success=True
    )

@app.post("/api/v1/agents/init-defaults")
async def init_default_agents():
    """Initialise les agents par défaut"""
    return {
        "message": "Default agents initialized successfully",
        "agents": [agent.id for agent in DEMO_AGENTS],
        "count": len(DEMO_AGENTS)
    }

@app.get("/api/v1/agents/ssh/status")
async def ssh_status():
    """Statut des connexions SSH (demo)"""
    return {
        "ssh_connections": [],
        "total_connections": 0,
        "healthy_connections": 0,
        "note": "SSH agents functionality available in full version"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)