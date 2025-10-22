# AI CFO Suite - Phoenix v2.0

**Solution agentic complète pour la gestion financière avec intelligence artificielle**

## 🚀 Vue d'ensemble

AI CFO Suite Phoenix est une plateforme intelligente qui combine un système multi-agents avec un système RAG (Retrieval-Augmented Generation) pour automatiser et améliorer les tâches financières. La solution intègre des agents IA spécialisés qui collaborent pour fournir des analyses comptables, fiscales, prévisionnelles et de conformité.

### Caractéristiques Principales

- **Système Multi-Agents** : 6 agents spécialisés (Comptabilité, Fiscalité, Prévisions, Conformité, Audit, Reporting)
- **RAG Avancé** : Vectorisation et recherche sémantique avec Qdrant
- **Architecture Hybride** : Vectorisation locale → Stockage cloud → Accès distribué
- **Stack Open-Source** : CrewAI, LlamaIndex, FastAPI, React
- **Scalable** : Docker Compose pour déploiement facile

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│  Dashboard | Upload | Explore | Playground | Admin          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Ingestion    │  │ RAG Service  │  │ Agent System │      │
│  │ Service      │  │ (LlamaIndex) │  │ (CrewAI)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │   Qdrant     │  │    Redis     │
│  (Metadata)  │  │  (Vectors)   │  │   (Cache)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 🧠 Agents Disponibles

| Agent | Spécialisation | Namespace |
|-------|---------------|-----------|
| **AccountantAgent** | Comptabilité, ratios financiers, IFRS/ASPE | `finance_accounting` |
| **TaxAgent** | Fiscalité canadienne (T1, T2, TPS/TVQ) | `finance_tax` |
| **ForecastAgent** | Prévisions financières, cashflow | `finance_forecast` |
| **ComplianceAgent** | Conformité réglementaire | `finance_compliance` |
| **AuditAgent** | Audit financier, détection d'anomalies | `finance_audit` |
| **ReporterAgent** | Génération de rapports synthétiques | `default` |

## 📦 Stack Technique

### Backend
- **FastAPI** : API REST moderne et performante
- **LlamaIndex** : Pipeline RAG et gestion des documents
- **Qdrant** : Base de données vectorielle
- **CrewAI** : Orchestration multi-agents
- **PostgreSQL** : Stockage des métadonnées
- **Redis** : Cache et sessions
- **MinIO** : Stockage d'objets

### Frontend
- **React 18** : Interface utilisateur moderne
- **TypeScript** : Typage statique
- **Vite** : Build tool ultra-rapide
- **Tailwind CSS** : Framework CSS utility-first
- **GSAP** : Animations fluides

### Embeddings & LLM
- **BGE-small-en-v1.5** : Modèle d'embeddings léger et performant
- **Mistral-7B** : Modèle LLM open-source (via OpenRouter)

## 🚀 Installation et Démarrage

### Prérequis

- Docker et Docker Compose
- Node.js 20+ (pour développement local)
- Python 3.11+ (pour développement local)

### Démarrage Rapide avec Docker

1. **Cloner le repository**
```bash
git clone <repository-url>
cd ai-cfo-suite-v2
```

2. **Configurer les variables d'environnement**
```bash
cp backend/.env.example backend/.env
# Éditer backend/.env avec vos clés API (optionnel pour MVP)
```

3. **Lancer tous les services**
```bash
docker-compose up -d
```

4. **Accéder à l'application**
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- API Docs : http://localhost:8000/docs
- Qdrant Dashboard : http://localhost:6333/dashboard
- MinIO Console : http://localhost:9001

### Développement Local

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📖 Utilisation

### 1. Upload de Documents

1. Accédez à la page **Upload**
2. Glissez-déposez vos documents (PDF, DOCX, CSV, TXT)
3. Sélectionnez les agents à assigner
4. Cliquez sur "Démarrer l'Ingestion"

Les documents sont automatiquement :
- Extraits et nettoyés
- Découpés en chunks (800 tokens)
- Vectorisés avec BGE-small
- Indexés dans Qdrant

### 2. Exploration des Documents

1. Accédez à la page **Explorer**
2. Recherchez par nom, agent ou tag
3. Cliquez sur "Utiliser comme Contexte" pour activer un document

### 3. Interaction avec les Agents

1. Accédez au **Playground**
2. Posez vos questions en langage naturel
3. Les agents utilisent le RAG pour répondre avec précision
4. Les sources sont citées automatiquement

### 4. Administration

1. Accédez à la page **Admin**
2. Vérifiez l'état des services
3. Gérez la configuration des agents
4. Consultez les statistiques système

## 🔧 Configuration Avancée

### Variables d'Environnement

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/db
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
OPENROUTER_API_KEY=your_key_here  # Optionnel
EMBED_MODEL=BAAI/bge-small-en-v1.5
DEFAULT_LLM=mistralai/mistral-7b-instruct
```

### Paramètres RAG

```python
# backend/core/config.py
CHUNK_SIZE = 800              # Taille des chunks
CHUNK_OVERLAP = 100           # Chevauchement
TOP_K = 10                    # Nombre de résultats
SIMILARITY_THRESHOLD = 0.7    # Seuil de similarité
```

## 📊 API Endpoints

### Ingestion

- `POST /api/v1/upload` : Upload et vectorisation de documents
- `GET /api/v1/documents` : Liste des documents
- `GET /api/v1/documents/{id}` : Détails d'un document
- `DELETE /api/v1/documents/{id}` : Suppression d'un document

### Chat & Agents

- `POST /api/v1/query` : Envoyer une requête aux agents
- `GET /api/v1/agents` : Liste des agents et leur statut

### Système

- `GET /health` : Health check
- `GET /` : Informations système

Documentation complète : http://localhost:8000/docs

## 🧪 Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## 🔒 Sécurité

- Validation des entrées utilisateur
- Sanitization des fichiers uploadés
- Chiffrement des données sensibles
- Authentification JWT (à configurer)
- CORS configuré
- Logs d'audit

## 📈 Performance

- **Latence RAG** : < 2s (P95)
- **Upload** : ~30s pour un PDF de 50 pages
- **Vectorisation** : ~1s par page
- **Cache Redis** : Hit rate > 70%

## 🛠️ Dépannage

### Backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Reconstruire l'image
docker-compose build backend
docker-compose up -d backend
```

### Qdrant ne répond pas

```bash
# Vérifier le service
docker-compose ps qdrant
docker-compose restart qdrant
```

### Erreur d'embeddings

Assurez-vous que le modèle est téléchargé :
```bash
docker-compose exec backend python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Forker le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commiter vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pusher vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT.

## 👥 Auteurs

- **Manus AI** - Développement initial

## 🙏 Remerciements

- **CrewAI** : Framework multi-agents
- **LlamaIndex** : Pipeline RAG
- **Qdrant** : Base de données vectorielle
- **FastAPI** : Framework backend
- **React** : Framework frontend

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation : `/docs`
- Email : support@ai-cfo-suite.com

---

**Construit avec ❤️ pour révolutionner la gestion financière avec l'IA**
