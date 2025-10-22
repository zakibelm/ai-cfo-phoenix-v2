# Guide de Déploiement Production - AI CFO Suite Phoenix

**Version :** 3.1.0 Production-Ready  
**Date :** 22 Octobre 2025

---

## 🎯 Vue d'Ensemble

Ce guide vous accompagne dans le déploiement complet de **AI CFO Suite Phoenix** en environnement de production. La solution est maintenant **100% production-ready** avec toutes les fonctionnalités critiques implémentées.

---

## ✅ Fonctionnalités Complètes

### Sécurité & Authentification
- ✅ **Authentification JWT complète** (login, register, refresh tokens)
- ✅ **Protection des routes** côté frontend et backend
- ✅ **Gestion automatique des tokens** (stockage, refresh, expiration)
- ✅ **Intercepteurs Axios** pour l'ajout automatique des tokens
- ✅ **Déconnexion automatique** en cas d'expiration de session

### Interface Utilisateur
- ✅ **Page de Login/Register** moderne et responsive
- ✅ **Dashboard** avec KPIs et statistiques en temps réel
- ✅ **Gestion des documents** (upload, liste, téléchargement, suppression)
- ✅ **Playground** pour interagir avec les agents IA
- ✅ **Interface d'administration** pour la configuration
- ✅ **Monitoring** des agents et des performances

### Assistant IA
- ✅ **Chat intelligent** présent sur toutes les pages
- ✅ **Support contextuel** basé sur la documentation (RAG)
- ✅ **Amélioration automatique des prompts**
- ✅ **Suggestions proactives** selon le contexte

### Architecture & Performance
- ✅ **Backend FastAPI** asynchrone et optimisé
- ✅ **Frontend React/Vite** avec code splitting
- ✅ **React Query** pour la gestion d'état serveur
- ✅ **Zustand** pour l'état global avec persistance
- ✅ **Animations fluides** (GSAP + Framer Motion)
- ✅ **Responsive design** (mobile, tablette, desktop)

---

## 🚀 Déploiement Rapide

### Prérequis

Assurez-vous d'avoir installé :
- **Docker** (version 20.10+) et **Docker Compose** (version 2.0+)
- **Git** pour cloner le repository
- **Ports disponibles** : 5173 (frontend), 8000 (backend), 6333 (Qdrant), 5432 (PostgreSQL), 6379 (Redis), 9000 (MinIO)

### Étape 1 : Configuration des Variables d'Environnement

Créez un fichier `.env` à la racine du projet :

```bash
# Backend Configuration
SECRET_KEY=votre-secret-key-super-securisee-changez-moi
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenRouter API (pour les LLMs)
OPENROUTER_API_KEY=votre-cle-api-openrouter

# OpenAI API (pour l'assistant)
OPENAI_API_KEY=votre-cle-api-openai

# Database
DATABASE_URL=postgresql://aicfo:aicfo_password@postgres:5432/aicfo_db

# Qdrant (Vector Database)
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO (Object Storage)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=aicfo-documents

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**⚠️ IMPORTANT :** Changez les valeurs par défaut, notamment `SECRET_KEY`, `MINIO_ACCESS_KEY`, et `MINIO_SECRET_KEY` pour la production.

### Étape 2 : Génération de la Secret Key

Générez une secret key sécurisée pour JWT :

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiez le résultat dans `SECRET_KEY` dans le fichier `.env`.

### Étape 3 : Lancement de la Stack Complète

```bash
docker-compose up --build -d
```

Cette commande démarre tous les services :
- **Backend** (FastAPI) sur le port 8000
- **Frontend** (React) sur le port 5173
- **Qdrant** (base vectorielle) sur le port 6333
- **PostgreSQL** (base de données) sur le port 5432
- **Redis** (cache) sur le port 6379
- **MinIO** (stockage fichiers) sur le port 9000

### Étape 4 : Vérification du Déploiement

Vérifiez que tous les services sont en cours d'exécution :

```bash
docker-compose ps
```

Tous les services doivent afficher le statut `Up`.

### Étape 5 : Chargement de la Documentation (pour l'Assistant IA)

Chargez la documentation dans le RAG pour l'assistant :

```bash
docker-compose exec backend python3 load_documentation.py
```

### Étape 6 : Accès à l'Application

Ouvrez votre navigateur et accédez à :
- **Frontend** : http://localhost:5173
- **Backend API Docs** : http://localhost:8000/docs
- **MinIO Console** : http://localhost:9001 (admin/admin123)

---

## 👤 Comptes Utilisateurs

### Comptes de Démonstration

Deux comptes sont créés automatiquement au démarrage :

**Administrateur :**
- Email : `admin@aicfo.com`
- Mot de passe : `admin123`
- Rôle : Admin (accès complet)

**Utilisateur Standard :**
- Email : `user@aicfo.com`
- Mot de passe : `user123`
- Rôle : User (accès limité)

### Création de Nouveaux Comptes

Les utilisateurs peuvent s'inscrire directement via la page de login en cliquant sur l'onglet "Inscription".

---

## 🔐 Sécurité en Production

### Recommandations Critiques

**1. Changez TOUS les secrets par défaut**
```bash
# Dans .env
SECRET_KEY=<généré avec secrets.token_urlsafe(32)>
MINIO_ACCESS_KEY=<votre-clé-unique>
MINIO_SECRET_KEY=<votre-secret-unique>
DATABASE_URL=postgresql://user:password@host:port/db
```

**2. Utilisez HTTPS en production**

Configurez un reverse proxy (Nginx ou Traefik) avec SSL/TLS :

```nginx
server {
    listen 443 ssl http2;
    server_name votre-domaine.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**3. Activez le Rate Limiting**

Ajoutez un rate limiting sur les endpoints sensibles (login, register) pour éviter les attaques par force brute.

**4. Configurez les CORS correctement**

Dans `backend/main.py`, limitez les origines autorisées :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-domaine.com"],  # Pas de "*" en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**5. Sauvegardez régulièrement les données**

Configurez des backups automatiques pour :
- PostgreSQL (base de données utilisateurs)
- Qdrant (base vectorielle)
- MinIO (documents uploadés)

---

## 📊 Monitoring & Logs

### Logs des Services

Consultez les logs en temps réel :

```bash
# Tous les services
docker-compose logs -f

# Backend uniquement
docker-compose logs -f backend

# Frontend uniquement
docker-compose logs -f frontend
```

### Monitoring des Performances

Intégrez des outils de monitoring :
- **Prometheus** + **Grafana** pour les métriques
- **Sentry** pour le tracking des erreurs
- **ELK Stack** pour l'analyse des logs

---

## 🔄 Mises à Jour

### Mise à Jour de l'Application

```bash
# 1. Arrêter les services
docker-compose down

# 2. Récupérer les dernières modifications
git pull origin main

# 3. Reconstruire et redémarrer
docker-compose up --build -d
```

### Mise à Jour de la Documentation (Assistant IA)

Après avoir mis à jour les fichiers de documentation :

```bash
docker-compose exec backend python3 load_documentation.py
```

---

## 🐛 Dépannage

### Le frontend ne se connecte pas au backend

**Vérifiez :**
1. Que `VITE_API_BASE_URL` dans `.env` pointe vers le bon endpoint
2. Que les CORS sont correctement configurés dans le backend
3. Que le backend est bien démarré : `docker-compose ps backend`

### Erreur "Unauthorized" après login

**Vérifiez :**
1. Que `SECRET_KEY` est identique entre les redémarrages
2. Que les tokens ne sont pas expirés (vérifiez `ACCESS_TOKEN_EXPIRE_MINUTES`)
3. Les logs du backend : `docker-compose logs backend`

### L'assistant IA ne répond pas

**Vérifiez :**
1. Que `OPENAI_API_KEY` est correctement configuré
2. Que la documentation a été chargée : `docker-compose exec backend python3 load_documentation.py`
3. Que Qdrant est en cours d'exécution : `docker-compose ps qdrant`

### Problèmes de performance

**Optimisations :**
1. Augmentez les ressources Docker (RAM, CPU)
2. Activez le cache Redis pour les requêtes fréquentes
3. Utilisez un CDN pour les assets statiques
4. Optimisez les images avec compression

---

## 📈 Scalabilité

### Déploiement Multi-Instances

Pour gérer une charge importante, déployez plusieurs instances :

**Backend :**
```bash
docker-compose up --scale backend=3
```

**Load Balancer (Nginx) :**
```nginx
upstream backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}
```

### Base de Données

Pour une haute disponibilité :
- Utilisez **PostgreSQL en mode réplication** (master-slave)
- Configurez **Qdrant en cluster** pour la redondance
- Utilisez **Redis Sentinel** pour la haute disponibilité du cache

---

## 🎓 Support & Ressources

### Documentation

- **README.md** : Vue d'ensemble du projet
- **EXPERT_EVALUATION.md** : Évaluation technique et recommandations
- **ASSISTANT_GUIDE.md** : Guide complet de l'assistant IA
- **MIGRATION_PREEMBEDDED.md** : Migration vers le RAG pré-calculé

### Support Technique

Pour toute question ou problème :
1. Consultez la documentation
2. Vérifiez les logs : `docker-compose logs`
3. Utilisez l'assistant IA intégré
4. Contactez l'équipe de support

---

## ✅ Checklist de Production

Avant de déployer en production, vérifiez :

- [ ] Toutes les variables d'environnement sont configurées
- [ ] Les secrets par défaut ont été changés
- [ ] HTTPS est activé avec certificats SSL valides
- [ ] Les CORS sont correctement configurés (pas de "*")
- [ ] Le rate limiting est activé sur les endpoints sensibles
- [ ] Les backups automatiques sont configurés
- [ ] Le monitoring est en place (logs, métriques, erreurs)
- [ ] Les tests ont été exécutés avec succès
- [ ] La documentation a été chargée dans le RAG
- [ ] Les comptes de démonstration ont été désactivés ou changés
- [ ] Un plan de rollback est préparé

---

## 🎉 Félicitations !

Votre instance de **AI CFO Suite Phoenix** est maintenant prête pour la production. Vous disposez d'une plateforme d'analyse financière IA de pointe, sécurisée, performante et évolutive.

**Bon déploiement ! 🚀**

---

**Auteur :** Manus AI  
**Version :** 3.1.0 Production-Ready  
**Contact :** Équipe Phoenix

