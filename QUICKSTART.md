# 🚀 Guide de Démarrage Rapide - AI CFO Suite Phoenix v2.0

## Installation en 5 Minutes

### Étape 1 : Prérequis

Assurez-vous d'avoir installé :
- **Docker** (version 20+)
- **Docker Compose** (version 2+)

Vérification :
```bash
docker --version
docker-compose --version
```

### Étape 2 : Démarrage

```bash
# 1. Extraire l'archive (si nécessaire)
tar -xzf ai-cfo-suite-v2.tar.gz
cd ai-cfo-suite-v2

# 2. Lancer tous les services
docker-compose up -d

# 3. Vérifier que tous les services sont démarrés
docker-compose ps
```

Attendez environ 2-3 minutes que tous les services démarrent.

### Étape 3 : Accès

Ouvrez votre navigateur et accédez à :

**🌐 Frontend** : http://localhost:3000

Autres URLs utiles :
- **📚 API Documentation** : http://localhost:8000/docs
- **🔍 Qdrant Dashboard** : http://localhost:6333/dashboard
- **💾 MinIO Console** : http://localhost:9001 (admin/minioadmin123)

### Étape 4 : Premier Test

1. **Accédez au Dashboard** : Vous verrez les KPIs et les agents disponibles

2. **Uploadez un document** :
   - Cliquez sur "Upload" dans la sidebar
   - Glissez-déposez un fichier PDF, DOCX ou TXT
   - Sélectionnez un ou plusieurs agents (ex: TaxAgent)
   - Cliquez sur "Démarrer l'Ingestion"
   - Attendez ~30 secondes

3. **Explorez vos documents** :
   - Cliquez sur "Explorer"
   - Recherchez votre document
   - Cliquez sur "Utiliser comme Contexte"

4. **Interagissez avec les agents** :
   - Cliquez sur "Playground"
   - Posez une question : "Quelles sont les dates limites de déclaration T2 ?"
   - L'agent TaxAgent répondra avec le contexte de vos documents

## 🎯 Exemples de Questions

### Pour TaxAgent
- "Quelles sont les déductions fiscales disponibles pour une PME au Canada ?"
- "Comment calculer la TPS et la TVQ ?"
- "Quelle est la date limite pour le T2 ?"

### Pour AccountantAgent
- "Comment calculer le ratio de liquidité ?"
- "Explique-moi les normes IFRS pour les immobilisations"
- "Quels sont les principaux ratios financiers à surveiller ?"

### Pour ForecastAgent
- "Crée une prévision de cashflow pour les 6 prochains mois"
- "Quels sont les indicateurs clés pour prévoir la croissance ?"

## 🛠️ Commandes Utiles

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Redémarrer un service
```bash
docker-compose restart backend
docker-compose restart qdrant
```

### Arrêter tous les services
```bash
docker-compose down
```

### Arrêter et supprimer les données
```bash
docker-compose down -v
```

## 🔧 Résolution de Problèmes

### Le frontend ne charge pas

```bash
# Vérifier les logs
docker-compose logs frontend

# Reconstruire
docker-compose build frontend
docker-compose up -d frontend
```

### Le backend retourne des erreurs 500

```bash
# Vérifier que Qdrant est démarré
docker-compose ps qdrant

# Redémarrer le backend
docker-compose restart backend
```

### "Backend Hors Ligne" dans le Playground

```bash
# Vérifier la santé du backend
curl http://localhost:8000/health

# Si pas de réponse, redémarrer
docker-compose restart backend
```

## 📊 Architecture Simplifiée

```
┌─────────────┐
│  Frontend   │ ← Vous êtes ici (localhost:3000)
│  (React)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Backend   │ ← API REST (localhost:8000)
│  (FastAPI)  │
└──────┬──────┘
       │
       ├─→ Qdrant (Vecteurs)
       ├─→ PostgreSQL (Métadonnées)
       ├─→ Redis (Cache)
       └─→ MinIO (Fichiers)
```

## 🎓 Prochaines Étapes

1. **Explorez les agents** : Testez chaque agent avec différentes questions
2. **Uploadez vos documents** : Ajoutez vos propres documents financiers
3. **Configurez les agents** : Allez dans Admin pour voir la configuration
4. **Lisez la documentation** : Consultez README.md pour plus de détails

## 💡 Conseils

- **Documents de qualité** : Plus vos documents sont structurés, meilleures seront les réponses
- **Contexte spécifique** : Activez un document dans Explorer pour des réponses plus précises
- **Agents appropriés** : Assignez les bons agents aux bons types de documents
- **Patience** : La première requête peut prendre quelques secondes (téléchargement des modèles)

## 🆘 Besoin d'Aide ?

- **Documentation complète** : Lisez README.md
- **API Docs** : http://localhost:8000/docs
- **Logs** : `docker-compose logs -f`

---

**Bon démarrage avec AI CFO Suite ! 🚀**
