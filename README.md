# AI CFO Suite - Phoenix Edition

**Version 3.1.0** | **État : Prêt pour la Production**

---

![Dashboard Screenshot](https://i.imgur.com/YOUR_DASHBOARD_SCREENSHOT.png)

**AI CFO Suite Phoenix** est une plateforme d'analyse financière multi-agents de nouvelle génération, conçue pour automatiser les tâches complexes de la direction financière. Grâce à une architecture RAG (Retrieval-Augmented Generation) avancée et à un système d'agents IA spécialisés, la suite offre des insights précis et contextuels à partir de vos documents financiers.

Cette version "Phoenix" est une refonte complète axée sur la **performance, la sécurité, l'ergonomie et l'évolutivité**.

## ✨ Fonctionnalités Clés

| Fonctionnalité | Description | Statut |
| :--- | :--- | :--- |
| 🤖 **Système Multi-Agents** | Agents spécialisés (Comptable, Fiscal, Audit...) orchestrés par un méta-agent pour des réponses expertes. | ✅ Actif |
| ⚡ **Double Moteur RAG** | Supporte l'**embedding à la volée** pour les nouveaux documents et un **moteur pré-embedded** pour un chargement instantané. | ✅ Actif |
| 🌐 **Accès Multi-LLM** | Intégration avec **OpenRouter** pour un accès flexible à plus de 10 modèles de langage (GPT-4, Claude, etc.). | ✅ Actif |
| 🔐 **Authentification JWT** | Système de sécurité complet avec tokens d'accès et de rafraîchissement. | ✅ Actif |
| 🎨 **UI/UX Premium** | Interface entièrement repensée, responsive, dynamique avec animations fluides (GSAP & Framer Motion). | ✅ Actif |
| 🚀 **Haute Performance** | Backend **FastAPI** asynchrone, frontend **React/Vite** optimisé, gestion d'état avec **React Query**. | ✅ Actif |
| 📦 **Gestion de Documents** | Interface unifiée pour téléverser, visualiser, gérer et supprimer les documents de la base de connaissances. | ✅ Actif |
| 📊 **Monitoring** | (Placeholder) Section prête pour l'intégration d'outils de monitoring des agents et des requêtes. | 🟡 Prêt |

---

## 🏛️ Architecture Technique

Le projet est structuré en deux composants principaux : un backend FastAPI et un frontend React.

### Backend

- **Framework** : [FastAPI](https://fastapi.tiangolo.com/) pour des performances élevées et une API auto-documentée.
- **Gestion des Dépendances** : [Poetry](https://python-poetry.org/) pour une gestion propre et déterministe.
- **Base de Données Vectorielle** : [Qdrant](https://qdrant.tech/) pour le stockage et la recherche d'embeddings.
- **Agents IA** : [CrewAI](https://www.crewai.com/) pour l'orchestration des agents.
- **Authentification** : JWT avec `python-jose` et `passlib`.
- **Base de Données (Utilisateurs)** : PostgreSQL (prêt pour l'intégration, utilise une base en mémoire pour la démo).
- **Cache** : Redis pour la mise en cache des sessions et des requêtes.
- **Stockage Fichiers** : MinIO pour le stockage des documents uploadés.

### Frontend

- **Framework** : [React](https://react.dev/) avec [Vite](https://vitejs.dev/) pour un développement ultra-rapide.
- **Langage** : [TypeScript](https://www.typescriptlang.org/) pour la robustesse et la maintenabilité.
- **Styling** : [Tailwind CSS](https://tailwindcss.com/) avec un **Design System** complet sur-mesure.
- **Gestion d'État** :
    - [React Query (TanStack)](https://tanstack.com/query/latest) pour la gestion des données serveur (cache, revalidation...).
    - [Zustand](https://zustand-demo.pmnd.rs/) pour l'état global de l'interface (thème, état du sidebar...).
- **Animations** : [GSAP](https://gsap.com/) pour les animations complexes et [Framer Motion](https://www.framer.com/motion/) pour les animations de l'interface.
- **Notifications** : [React Hot Toast](https://react-hot-toast.com/) pour des notifications propres et non-bloquantes.

---

## 🚀 Démarrage Rapide

### Prérequis

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Poetry

### 1. Configuration

Clonez le projet et configurez les variables d'environnement.

```bash
# Clonez le projet
git clone https://github.com/votre-repo/ai-cfo-suite-phoenix.git
cd ai-cfo-suite-phoenix

# Copiez les fichiers d'environnement
cp backend/.env.example backend/.env
cp .env.example .env
```

Modifiez les fichiers `.env` avec vos clés API (OpenRouter, etc.) et secrets.

### 2. Lancement avec Docker (Recommandé)

La méthode la plus simple pour tout lancer.

```bash
docker-compose up --build
```

L'application sera disponible :
- **Frontend** : `http://localhost:5173`
- **Backend API Docs** : `http://localhost:8000/docs`

### 3. Lancement Manuel

#### Backend

```bash
cd backend

# Installer les dépendances
poetry install

# Lancer le serveur de développement
poetry run uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Installer les dépendances
pnpm install

# Lancer le serveur de développement
pnpm run dev
```

---

## 🧪 Tests

### Backend

Le backend utilise `pytest`. Pour lancer la suite de tests :

```bash
cd backend
poetry run pytest
```

### Frontend

Le frontend utilise `vitest` (à configurer). Pour lancer les vérifications de types :

```bash
cd frontend
pnpm run type-check
```

---

## 👤 Utilisateurs par Défaut

Pour la démonstration, deux utilisateurs sont créés en mémoire au démarrage du backend :

- **Admin** :
  - **Email** : `admin@aicfo.com`
  - **Mot de passe** : `admin123`
- **Utilisateur Standard** :
  - **Email** : `user@aicfo.com`
  - **Mot de passe** : `user123`

---

## 📖 Documentation Complémentaire

- **`EXPERT_EVALUATION.md`** : Audit complet du projet et recommandations.
- **`MIGRATION_PREEMBEDDED.md`** : Détails sur la migration vers le RAG pré-calculé.
- **`CHANGELOG.md`** : Journal des modifications de la version Phoenix.

---

## Auteurs

- **Développeur Principal** : [Votre Nom]
- **Consultant IA & Refactoring** : Manus AI

