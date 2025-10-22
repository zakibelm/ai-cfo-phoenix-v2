# 🚀 Guide Complet de Déploiement - AI CFO Suite Phoenix v3.0

## 📋 Table des Matières

- [Vue d'Ensemble](#-vue-densemble)
- [Prérequis](#-prérequis)
- [Installation Rapide](#-installation-rapide)
- [Configuration Détaillée](#-configuration-détaillée)
- [Tests et Validation](#-tests-et-validation)
- [Fonctionnalités SSH](#-fonctionnalités-ssh)
- [Troubleshooting](#-troubleshooting)
- [Production](#-production)

## 🎯 Vue d'Ensemble

**AI CFO Suite Phoenix v3.0** est une suite d'IA financière multi-agents avec les capacités suivantes :

### Fonctionnalités Principales

- 🧠 **6 Agents IA Spécialisés** (Comptabilité, Fiscalité, Prévisions, etc.)
- 🌍 **Support Multilingue** (FR/EN) avec i18n
- 🌎 **Multi-Juridictions** (Canada, Québec, France, USA)
- 🤖 **10+ Modèles LLM** via OpenRouter
- 📚 **RAG Optimisé** (fichiers jusqu'à 600 MB)
- 🔗 **Agents SSH Distants** (Architecture hybride)
- 🎯 **MetaOrchestrator** (Routing intelligent)

### Architecture Technique

```
┌─────────────────────────────────────────────────┐
│              Frontend (React)                   │
│          http://localhost:3000                  │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Backend (FastAPI)                  │
│          http://localhost:8000                  │
│                                                 │
│  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ MetaOrchestrator│  │    6 Agents IA      │  │
│  │                 │  │   Spécialisés       │  │
│  └─────────────────┘  └─────────────────────┘  │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            Infrastructure Docker                │
│  • PostgreSQL (Port 5432)                      │
│  • Qdrant Vector DB (Port 6333)                │
│  • Redis Cache (Port 6379)                     │
│  • MinIO Storage (Port 9000/9001)              │
└─────────────────────────────────────────────────┘
```

## 🛠️ Prérequis

### Système

| Composant | Version Minimale | Recommandé |
|-----------|-----------------|------------|
| **OS** | Windows 10/11, macOS 10.15+, Ubuntu 18.04+ | Windows 11, Ubuntu 22.04+ |
| **RAM** | 8 GB | 16 GB+ |
| **Stockage** | 10 GB libre | 50 GB+ |
| **CPU** | 4 cores | 8 cores+ |

### Logiciels Requis

#### 1. Docker & Docker Compose

```powershell
# Windows - Installer Docker Desktop
# Télécharger depuis : https://www.docker.com/products/docker-desktop

# Vérifier l'installation
docker --version
docker-compose --version
```

#### 2. Git (Optionnel)

```powershell
# Windows
winget install Git.Git

# Vérifier
git --version
```

#### 3. Clé API OpenRouter

1. Créez un compte sur [OpenRouter](https://openrouter.ai/)
2. Générez une clé API
3. Notez votre clé : `sk-or-v1-xxxxxxxxxx`

## 🚀 Installation Rapide

### Étape 1 : Téléchargement

Le projet est déjà cloné dans votre répertoire. Si ce n'est pas le cas :

```powershell
git clone https://github.com/zakibelm/ai-cfo-suite-phoenix.git
cd ai-cfo-suite-phoenix
```

### Étape 2 : Configuration Automatique

```powershell
# Utiliser le script de démarrage automatique
.\start-ai-cfo.ps1 -OpenRouterKey "sk-or-v1-votre-clé-ici"

# Ou démarrage simple (configuration manuelle requise)
.\start-ai-cfo.ps1
```

### Étape 3 : Vérification

```powershell
# Tests rapides
.\test-ai-cfo.ps1 -Quick

# Tests complets
.\test-ai-cfo.ps1 -Full
```

## 🔧 Configuration Détaillée

### 1. Fichier .env Backend

Le fichier `.env` a déjà été créé. Voici les paramètres clés :

```env
# AI CFO Suite - Configuration

# OpenRouter (OBLIGATOIRE)
OPENROUTER_API_KEY=sk-or-v1-votre-clé-ici
DEFAULT_LLM_MODEL=mistralai/mistral-7b-instruct

# Base de données
DATABASE_URL=postgresql://aicfo:aicfo_secure_pass_2025@postgres:5432/aicfo_db
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379/0

# Sécurité
SECRET_KEY=test-secret-key-for-local-development-min-32-chars-long
ENCRYPTION_KEY=test-32-byte-key-for-local-dev!!

# i18n
DEFAULT_LANGUAGE=fr
SUPPORTED_LANGUAGES=fr,en
```

### 2. Configuration OpenRouter

#### Modèles Disponibles

| Modèle | Provider | Context | Coût Input/Output ($/1K tokens) |
|--------|----------|---------|----------------------------------|
| `gpt-4-turbo` | OpenAI | 128K | 0.010 / 0.030 |
| `claude-3-sonnet` | Anthropic | 200K | 0.003 / 0.015 |
| `gemini-pro` | Google | 32K | 0.000125 / 0.000375 |
| `mistralai/mistral-7b-instruct` | Mistral | 32K | 0.00027 / 0.00027 |

#### Recommandations par Usage

```env
# Pour tests/développement (économique)
DEFAULT_LLM_MODEL=mistralai/mistral-7b-instruct

# Pour production (qualité)
DEFAULT_LLM_MODEL=claude-3-sonnet

# Pour analyses complexes (contexte large)
DEFAULT_LLM_MODEL=gpt-4-turbo
```

### 3. Démarrage des Services

```powershell
# Démarrage standard
docker-compose up -d

# Avec reconstruction des images
docker-compose up -d --build

# Voir les logs en temps réel
docker-compose logs -f

# Vérifier l'état des services
docker-compose ps
```

## 🧪 Tests et Validation

### Tests Automatisés

```powershell
# Tests infrastructure uniquement
.\test-ai-cfo.ps1 -Quick

# Tests complets avec agents et upload
.\test-ai-cfo.ps1 -Full

# Test avec requête personnalisée
.\test-ai-cfo.ps1 -TestQuery "Comment calculer la TPS au Canada?"
```

### Tests Manuels

#### 1. Accès aux Interfaces

| Interface | URL | Identifiants |
|-----------|-----|--------------|
| **Application Web** | http://localhost:3000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Health Check** | http://localhost:8000/api/v1/monitoring/health | - |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | - |
| **MinIO Console** | http://localhost:9001 | admin/minioadmin123 |

#### 2. Test des Agents

```powershell
# Via PowerShell - Test MetaOrchestrator
$body = @{
    query = "Quelles sont les obligations fiscales d'une PME au Québec?"
    language = "fr"
    jurisdiction = "CA-QC"
    model = "mistralai/mistral-7b-instruct"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/meta/query" -Method POST -Body $body -ContentType "application/json"
```

#### 3. Test Upload de Documents

```powershell
# Créer un fichier test
@"
RAPPORT FINANCIER
================
Revenus: 100,000 CAD
Charges: 70,000 CAD
Bénéfice: 30,000 CAD
"@ | Out-File -FilePath "test.txt"

# Upload via curl (nécessite curl installé)
curl -X POST "http://localhost:8000/api/v1/documents/upload" -F "file=@test.txt" -F "document_type=financial_report"
```

### Tests des Fonctionnalités

#### Multilingue (i18n)

```powershell
# Test en français
$frBody = @{
    query = "Quelle est la date limite pour la déclaration T2?"
    language = "fr"
    jurisdiction = "CA"
} | ConvertTo-Json

# Test en anglais
$enBody = @{
    query = "What is the deadline for T2 filing?"
    language = "en"
    jurisdiction = "CA"
} | ConvertTo-Json
```

## 🔗 Fonctionnalités SSH

### Configuration SSH Locale (WSL)

Consultez le [Guide SSH Complet](SSH_TESTING_GUIDE.md) pour :

- Installation et configuration WSL
- Création d'agents distants
- Tests des connexions SSH
- Monitoring des performances

### Exemple Rapide

```powershell
# Dans WSL Ubuntu
sudo apt update && sudo apt install openssh-server python3
sudo service ssh start
sudo useradd -m aiagent && sudo passwd aiagent

# Obtenir l'IP WSL
ip addr show eth0 | grep inet

# Dans l'interface web AI CFO Suite
# Créer un nouvel agent avec SSH activé
# Host: [IP WSL], User: aiagent, Endpoint: /home/aiagent/script.py
```

## 🛠️ Troubleshooting

### Problèmes Courants

#### 1. Services ne Démarrent Pas

```powershell
# Vérifier Docker
docker info

# Vérifier les ports
netstat -an | findstr "3000 8000 5432 6333"

# Nettoyer et redémarrer
docker-compose down -v
docker system prune -f
.\start-ai-cfo.ps1 -Clean
```

#### 2. "Backend Hors Ligne"

```powershell
# Vérifier le backend
curl http://localhost:8000/api/v1/monitoring/health

# Voir les logs
docker-compose logs backend

# Redémarrer le backend
docker-compose restart backend
```

#### 3. Erreurs OpenRouter

```powershell
# Vérifier la clé API
$headers = @{ "Authorization" = "Bearer sk-or-v1-votre-clé" }
Invoke-RestMethod -Uri "https://openrouter.ai/api/v1/models" -Headers $headers

# Tester un modèle simple
$body = @{
    query = "Test simple"
    model = "mistralai/mistral-7b-instruct"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/meta/query" -Method POST -Body $body -ContentType "application/json"
```

#### 4. Problèmes de Performance

```powershell
# Augmenter la mémoire Docker (Docker Desktop > Settings > Resources)
# RAM recommandée : 8 GB minimum, 16 GB idéal

# Vérifier l'utilisation
docker stats

# Optimiser la base de données
docker-compose exec postgres vacuumdb -U aicfo aicfo_db
```

### Logs de Débogage

```powershell
# Tous les logs
docker-compose logs

# Logs d'un service spécifique
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Logs en temps réel
docker-compose logs -f backend

# Filtrer les logs
docker-compose logs backend | findstr "ERROR"
```

### Commandes Utiles

```powershell
# État des conteneurs
docker-compose ps

# Utilisation des ressources
docker stats

# Accéder à un conteneur
docker-compose exec backend bash
docker-compose exec postgres psql -U aicfo aicfo_db

# Sauvegarder la base de données
docker-compose exec postgres pg_dump -U aicfo aicfo_db > backup.sql

# Restaurer la base de données
docker-compose exec -T postgres psql -U aicfo aicfo_db < backup.sql
```

## 🌐 Production

### Sécurité

#### 1. Variables d'Environnement

```env
# Changez ABSOLUMENT ces valeurs en production
SECRET_KEY=votre-secret-key-production-64-chars-minimum-très-sécurisé
ENCRYPTION_KEY=votre-32-byte-encryption-key-ici!!

# Utilisez des mots de passe forts
POSTGRES_PASSWORD=mot-de-passe-très-fort-et-unique
MINIO_SECRET_KEY=clé-minio-très-sécurisée

# Activez HTTPS
CORS_ORIGINS=https://votre-domaine.com
```

#### 2. Docker Production

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim

# Variables d'environnement de production
ENV DEBUG=False
ENV PYTHONUNBUFFERED=1

# Installation sans cache
RUN pip install --no-cache-dir -r requirements.txt

# Utilisateur non-root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app", "--workers", "4"]
```

#### 3. Reverse Proxy (Nginx)

```nginx
# nginx.conf
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Monitoring Production

#### 1. Health Checks

```bash
# Script de monitoring
#!/bin/bash
# monitor.sh

services=("frontend:3000" "backend:8000" "postgres:5432" "qdrant:6333")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if nc -z localhost "$port"; then
        echo "✅ $name (port $port) : OK"
    else
        echo "❌ $name (port $port) : DOWN"
        # Alertes par email/Slack ici
    fi
done
```

#### 2. Métriques

```python
# Intégration Prometheus/Grafana
# Ajoutez des métriques custom dans votre backend
from prometheus_client import Counter, Histogram

query_counter = Counter('ai_cfo_queries_total', 'Total queries processed')
response_time = Histogram('ai_cfo_response_time_seconds', 'Response time')
```

### Backup et Restauration

```bash
# Backup automatique quotidien
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)

# Base de données
docker-compose exec postgres pg_dump -U aicfo aicfo_db > "backups/postgres_$DATE.sql"

# Qdrant
docker-compose exec qdrant tar -czf - /qdrant/storage > "backups/qdrant_$DATE.tar.gz"

# MinIO
docker-compose exec minio tar -czf - /data > "backups/minio_$DATE.tar.gz"

# Nettoyer les backups > 30 jours
find backups/ -name "*.sql" -mtime +30 -delete
```

## 📈 Optimisation

### Performance

```env
# Optimisations backend/.env
CHUNK_SIZE=1024        # Augmenter pour gros documents
TOP_K=15              # Plus de résultats RAG
RERANK_TOP_K=8        # Meilleur reranking
AGENT_TIMEOUT=600     # Timeout plus long
```

### Scaling

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3        # 3 instances backend
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    
  postgres:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

## 🎯 Prochaines Étapes

1. **✅ Terminer l'installation locale**
2. **🧪 Tester toutes les fonctionnalités**
3. **🔗 Configurer les agents SSH (optionnel)**
4. **📱 Développer vos agents personnalisés**
5. **🌐 Déployer en production avec HTTPS**

---

## 🆘 Support

### Documentation

- **Guide SSH** : [SSH_TESTING_GUIDE.md](SSH_TESTING_GUIDE.md)
- **README Principal** : [README.md](README.md)
- **API Reference** : http://localhost:8000/docs

### Ressources

- **OpenRouter** : https://openrouter.ai/
- **Docker** : https://docs.docker.com/
- **Issues GitHub** : https://github.com/zakibelm/ai-cfo-suite-phoenix/issues

### Scripts Utiles

```powershell
# Commandes principales créées
.\start-ai-cfo.ps1           # Démarrage automatique
.\start-ai-cfo.ps1 -Clean    # Démarrage avec nettoyage
.\start-ai-cfo.ps1 -Logs     # Démarrage avec logs
.\test-ai-cfo.ps1 -Quick     # Tests rapides
.\test-ai-cfo.ps1 -Full      # Tests complets

# Commandes Docker utiles
docker-compose up -d         # Démarrer services
docker-compose down          # Arrêter services
docker-compose logs -f       # Voir logs temps réel
docker-compose ps            # État services
docker-compose restart backend  # Redémarrer un service
```

---

**🎉 Félicitations ! AI CFO Suite Phoenix v3.0 est maintenant prêt à l'emploi !**

Ouvrez http://localhost:3000 et explorez les capacités de votre suite IA financière multi-agents.