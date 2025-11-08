# Guide de Déploiement Rapide - AI CFO Suite Phoenix v2

## 🎯 Objectif
Ce guide vous permet de déployer rapidement le backend AI CFO Suite Phoenix après les corrections.

---

## ✅ Prérequis

### Logiciels requis
- **Docker** 20.10+ et **Docker Compose** 2.0+
- **Git** pour cloner le projet
- **Éditeur de texte** pour configurer les variables d'environnement

### Ports requis (doivent être libres)
- `5432` - PostgreSQL
- `6333`, `6334` - Qdrant
- `6379` - Redis
- `9000`, `9001` - MinIO
- `8000` - Backend API
- `3000` - Frontend

---

## 🚀 Déploiement en 5 étapes

### Étape 1 : Cloner le projet
```bash
git clone git@github.com:zakibelm/ai-cfo-phoenix-v2.git
cd ai-cfo-phoenix-v2
```

### Étape 2 : Configurer les variables d'environnement
```bash
# Le fichier .env existe déjà, il faut le configurer
cd backend
nano .env  # ou vim, code, etc.
```

**Variables critiques à configurer** :

```bash
# OpenRouter API (OBLIGATOIRE pour les LLMs)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# Sécurité (OBLIGATOIRE en production)
SECRET_KEY=votre-cle-secrete-minimum-32-caracteres-aleatoires
ENCRYPTION_KEY=votre-cle-chiffrement-32-bytes

# HuggingFace (OPTIONNEL - pour embeddings personnalisés)
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
```

**Comment obtenir les clés** :
- **OpenRouter** : https://openrouter.ai/keys
- **HuggingFace** : https://huggingface.co/settings/tokens

### Étape 3 : Démarrer avec Docker Compose
```bash
# Retourner à la racine du projet
cd ..

# Démarrer tous les services
docker-compose up --build
```

**Temps estimé** : 10-15 minutes (téléchargement des images + build)

### Étape 4 : Vérifier le démarrage
Ouvrir un nouveau terminal et vérifier :

```bash
# Vérifier que tous les conteneurs sont running
docker-compose ps

# Vérifier les logs du backend
docker-compose logs backend

# Tester le health check
curl http://localhost:8000/api/v1/monitoring/health
```

**Réponse attendue** :
```json
{
    "status": "healthy",
    "timestamp": "2025-11-04T...",
    "version": "3.1.0",
    "services": {
        "api": "running",
        "database": "connected",
        "vector_db": "connected",
        "cache": "connected",
        "storage": "connected"
    }
}
```

### Étape 5 : Accéder à l'application
- **Frontend** : http://localhost:3000
- **Backend API Docs** : http://localhost:8000/docs
- **MinIO Console** : http://localhost:9001 (minioadmin / minioadmin123)

---

## 🔧 Dépannage

### Problème : Port déjà utilisé
**Erreur** : `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution** :
```bash
# Trouver le processus utilisant le port
sudo lsof -i :8000

# Tuer le processus
sudo kill -9 <PID>

# Ou changer le port dans docker-compose.yml
```

### Problème : Conteneur backend ne démarre pas
**Symptômes** : Le conteneur backend redémarre en boucle

**Solution** :
```bash
# Voir les logs détaillés
docker-compose logs -f backend

# Vérifier que le fichier .env est bien configuré
cat backend/.env | grep -E "OPENROUTER|SECRET_KEY"

# Redémarrer uniquement le backend
docker-compose restart backend
```

### Problème : Dépendances manquantes
**Erreur** : `ModuleNotFoundError: No module named 'xxx'`

**Solution** :
```bash
# Reconstruire l'image backend
docker-compose build --no-cache backend

# Redémarrer
docker-compose up backend
```

### Problème : Base de données non accessible
**Erreur** : `could not connect to server: Connection refused`

**Solution** :
```bash
# Vérifier que PostgreSQL est healthy
docker-compose ps postgres

# Voir les logs PostgreSQL
docker-compose logs postgres

# Redémarrer PostgreSQL
docker-compose restart postgres
```

---

## 🧪 Tests de validation

### Test 1 : Backend API
```bash
# Root endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/api/v1/monitoring/health

# Liste des agents
curl http://localhost:8000/api/v1/agents
```

### Test 2 : Requête à un agent
```bash
curl -X POST http://localhost:8000/api/v1/meta/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quelles sont les obligations fiscales d'une PME au Québec?",
    "language": "fr",
    "jurisdiction": "CA-QC"
  }'
```

### Test 3 : Documentation interactive
Ouvrir dans un navigateur : http://localhost:8000/docs

Tester les endpoints directement depuis l'interface Swagger.

---

## 📊 Monitoring

### Vérifier l'état des services
```bash
# État général
curl http://localhost:8000/api/v1/monitoring/health

# Métriques système
curl http://localhost:8000/api/v1/monitoring/metrics

# Dashboard complet
curl http://localhost:8000/api/v1/monitoring/dashboard
```

### Logs en temps réel
```bash
# Tous les services
docker-compose logs -f

# Backend uniquement
docker-compose logs -f backend

# PostgreSQL uniquement
docker-compose logs -f postgres
```

### Utilisation des ressources
```bash
# Stats des conteneurs
docker stats

# Espace disque utilisé
docker system df
```

---

## 🛑 Arrêter l'application

### Arrêt propre
```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
docker-compose down -v
```

### Arrêt d'urgence
```bash
# Tuer tous les conteneurs
docker-compose kill
```

---

## 🔄 Mise à jour

### Mettre à jour le code
```bash
# Récupérer les dernières modifications
git pull origin main

# Reconstruire et redémarrer
docker-compose up --build
```

### Mettre à jour uniquement le backend
```bash
# Arrêter le backend
docker-compose stop backend

# Reconstruire
docker-compose build backend

# Redémarrer
docker-compose up -d backend
```

---

## 📝 Mode développement local (sans Docker)

### Prérequis supplémentaires
- Python 3.11+
- PostgreSQL 15+
- Qdrant
- Redis
- MinIO

### Installation
```bash
cd backend

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
python3 main.py
```

### Utiliser le script de démarrage
```bash
# À la racine du projet
./start-backend.sh local
```

---

## 🔐 Sécurité en production

### Checklist de sécurité
- [ ] Changer tous les mots de passe par défaut
- [ ] Générer des clés secrètes fortes (SECRET_KEY, ENCRYPTION_KEY)
- [ ] Configurer HTTPS avec un certificat SSL
- [ ] Restreindre les CORS_ORIGINS aux domaines autorisés
- [ ] Utiliser un reverse proxy (nginx, traefik)
- [ ] Activer les logs d'audit
- [ ] Configurer des backups automatiques
- [ ] Limiter les ressources des conteneurs
- [ ] Utiliser Docker secrets pour les variables sensibles

### Générer des clés sécurisées
```bash
# SECRET_KEY (32+ caractères)
openssl rand -base64 32

# ENCRYPTION_KEY (exactement 32 bytes)
openssl rand -base64 32 | cut -c1-32
```

---

## 📚 Ressources supplémentaires

### Documentation
- **README principal** : `README.md`
- **Corrections appliquées** : `CORRECTIONS_BACKEND.md`
- **Guide des agents SSH** : `GUIDE_AGENTS_SSH.md`
- **Migration RAG** : `MIGRATION_PREEMBEDDED.md`

### Endpoints utiles
- Documentation API : http://localhost:8000/docs
- Documentation alternative : http://localhost:8000/redoc
- OpenAPI JSON : http://localhost:8000/openapi.json

### Support
- **Issues GitHub** : https://github.com/zakibelm/ai-cfo-phoenix-v2/issues
- **Documentation OpenRouter** : https://openrouter.ai/docs
- **Documentation FastAPI** : https://fastapi.tiangolo.com/

---

## ✨ Fonctionnalités principales

### Agents disponibles
1. **TaxAgent** - Expert fiscal (Canada, Québec)
2. **AccountantAgent** - Expert comptable (IFRS, ASPE)
3. **ForecastAgent** - Analyste prévisionnel
4. **ComplianceAgent** - Expert conformité
5. **AuditAgent** - Auditeur IA
6. **ReporterAgent** - Générateur de rapports

### Capacités RAG
- Upload de documents (PDF, DOCX, TXT)
- Embedding automatique ou pré-calculé
- Recherche sémantique avec Qdrant
- Reranking pour améliorer la pertinence

### Authentification
- JWT avec tokens d'accès et de rafraîchissement
- Utilisateurs par défaut (voir README.md)
- Gestion des sessions avec Redis

---

## 🎉 Félicitations !

Votre backend AI CFO Suite Phoenix est maintenant déployé et opérationnel !

**Prochaines étapes suggérées** :
1. Tester tous les agents via l'interface Swagger
2. Uploader des documents financiers
3. Configurer le frontend
4. Personnaliser les prompts des agents
5. Mettre en place le monitoring en production
