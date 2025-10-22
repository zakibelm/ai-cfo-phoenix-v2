# Guide de l'Assistant IA

L'**Assistant IA** est un chatbot intelligent intégré à toutes les pages de l'application AI CFO Suite Phoenix. Il utilise la technologie RAG (Retrieval-Augmented Generation) pour fournir un support contextuel basé sur la documentation complète de la plateforme.

---

## 🎯 Fonctionnalités Principales

### 1. Support Technique Contextuel

L'assistant a accès à toute la documentation de la plateforme et peut répondre à des questions sur :
- Comment utiliser les différentes fonctionnalités
- L'architecture technique du système
- Les bonnes pratiques d'utilisation
- Le dépannage des problèmes courants

**Exemple de questions :**
- "Comment téléverser un document ?"
- "Quels sont les formats de fichiers supportés ?"
- "Comment fonctionne le système d'agents ?"

### 2. Amélioration Automatique des Prompts

Lorsque l'assistant détecte qu'un prompt utilisateur est mal formulé (trop court, manque de contexte, etc.), il propose automatiquement une version améliorée.

**Exemple :**
- **Prompt initial :** "agents"
- **Prompt amélioré :** "Quels sont les différents types d'agents disponibles dans AI CFO Suite et quels sont leurs rôles spécifiques ?"

L'utilisateur peut copier le prompt amélioré en un clic.

### 3. Suggestions Contextuelles

En fonction de la page actuelle et du contexte de la conversation, l'assistant propose des questions pertinentes que l'utilisateur pourrait vouloir poser.

**Exemples de suggestions :**
- Sur la page **Documents** : "Quels formats de fichiers sont supportés ?"
- Sur la page **Dashboard** : "Comment interpréter les KPIs ?"
- Sur la page **Playground** : "Comment formuler une bonne question ?"

### 4. Historique de Conversation

L'assistant garde en mémoire les 6 derniers messages de la conversation pour maintenir le contexte et fournir des réponses cohérentes.

---

## 🚀 Utilisation

### Ouvrir l'Assistant

Cliquez sur le bouton flottant en bas à droite de l'écran (icône de bulle de message).

### Poser une Question

1. Tapez votre question dans le champ de saisie
2. Appuyez sur **Entrée** ou cliquez sur le bouton d'envoi
3. L'assistant analyse votre question et recherche dans la documentation
4. Une réponse contextuelle s'affiche en quelques secondes

### Utiliser les Suggestions

- Cliquez sur une suggestion pour l'insérer automatiquement dans le champ de saisie
- Modifiez-la si nécessaire avant de l'envoyer

### Copier un Prompt Amélioré

Si l'assistant propose un prompt amélioré :
1. Cliquez sur le bouton **Copier** sous le prompt amélioré
2. Collez-le dans le champ de saisie ou ailleurs selon vos besoins

### Réinitialiser la Conversation

Cliquez sur l'icône de rafraîchissement (↻) dans l'en-tête du chat pour effacer l'historique et recommencer une nouvelle conversation.

---

## 🔧 Configuration Backend

### Charger la Documentation dans le RAG

Pour que l'assistant ait accès à la documentation, vous devez d'abord charger les fichiers de documentation dans la base de données vectorielle :

```bash
cd backend
python3 load_documentation.py
```

Ce script :
1. Lit tous les fichiers de documentation (README, guides, etc.)
2. Les découpe en chunks de texte
3. Crée un fichier JSON prêt pour l'embedding
4. (Optionnel) Lance le processus d'embedding si configuré

### Fichiers de Documentation Indexés

- `README.md` : Documentation principale
- `EXPERT_EVALUATION.md` : Évaluation et recommandations
- `MIGRATION_PREEMBEDDED.md` : Guide de migration
- `MODIFICATIONS_SUMMARY.md` : Résumé des modifications
- `CHANGELOG.md` : Journal des changements
- `QUICKSTART.md` : Guide de démarrage rapide

---

## 🧠 Fonctionnement Technique

### Architecture

```
User Message
    ↓
Frontend (ChatAssistant.tsx)
    ↓
API Endpoint (/api/v1/assistant/chat)
    ↓
AssistantService
    ├─→ RAG Query (recherche dans la documentation)
    ├─→ Prompt Enhancement Detection
    ├─→ LLM Call (GPT-4o-mini)
    └─→ Suggestions Generation
    ↓
Response (message + enhanced_prompt + suggestions)
```

### Modèle LLM

L'assistant utilise **GPT-4o-mini** pour un équilibre optimal entre :
- **Performance** : Réponses rapides (< 2 secondes)
- **Qualité** : Réponses précises et contextuelles
- **Coût** : Modèle économique pour un usage intensif

### RAG (Retrieval-Augmented Generation)

1. **Requête utilisateur** → Vectorisation
2. **Recherche sémantique** dans la collection "documentation"
3. **Top 3 chunks** les plus pertinents récupérés
4. **Contexte enrichi** fourni au LLM
5. **Réponse générée** basée sur la documentation réelle

---

## 💡 Bonnes Pratiques

### Pour les Utilisateurs

1. **Soyez spécifique** : Plus votre question est précise, meilleure sera la réponse
2. **Utilisez les suggestions** : Elles sont conçues pour le contexte actuel
3. **Reformulez si nécessaire** : Si la réponse n'est pas satisfaisante, essayez de reformuler
4. **Explorez les prompts améliorés** : Ils peuvent vous apprendre à mieux formuler vos questions

### Pour les Développeurs

1. **Maintenez la documentation à jour** : L'assistant est aussi bon que la documentation qu'il indexe
2. **Relancez `load_documentation.py`** après chaque mise à jour majeure de la doc
3. **Surveillez les logs** : Les erreurs de l'assistant sont loguées pour faciliter le débogage
4. **Personnalisez le `system_prompt`** dans `assistant_service.py` selon vos besoins

---

## 🔐 Sécurité et Confidentialité

- **Pas de stockage permanent** : Les conversations ne sont pas sauvegardées en base de données
- **Contexte limité** : Seuls les 6 derniers messages sont gardés en mémoire
- **Accès public** : L'endpoint `/assistant/chat` est accessible sans authentification (peut être modifié)
- **Données sensibles** : Ne partagez pas d'informations confidentielles dans le chat

---

## 🛠️ Personnalisation

### Modifier le Comportement de l'Assistant

Éditez le fichier `backend/services/assistant_service.py` et modifiez la variable `self.system_prompt` pour changer :
- Le ton de l'assistant (formel, décontracté, etc.)
- Les domaines d'expertise
- Le format des réponses

### Ajouter de Nouveaux Documents

1. Placez vos fichiers Markdown dans le dossier racine du projet
2. Ajoutez-les à la liste `doc_files` dans `load_documentation.py`
3. Relancez le script de chargement

### Changer le Modèle LLM

Dans `assistant_service.py`, modifiez :
```python
self.model = "gpt-4o-mini"  # Changez pour un autre modèle
```

Modèles recommandés :
- `gpt-4o-mini` : Rapide et économique (par défaut)
- `gpt-4o` : Plus puissant mais plus lent
- `gpt-3.5-turbo` : Très rapide, moins précis

---

## 📊 Métriques et Monitoring

(À implémenter)

Suggestions de métriques à suivre :
- Nombre de conversations par jour
- Temps de réponse moyen
- Taux de satisfaction (avec boutons 👍/👎)
- Questions les plus fréquentes
- Taux d'utilisation des prompts améliorés

---

## 🐛 Dépannage

### L'assistant ne répond pas

1. Vérifiez que le backend est en cours d'exécution
2. Vérifiez la clé API OpenAI dans `.env`
3. Consultez les logs du backend : `docker-compose logs backend`

### Les réponses sont hors contexte

1. Vérifiez que la documentation a été chargée : `python3 load_documentation.py`
2. Vérifiez que la collection "documentation" existe dans Qdrant

### Erreur "Failed to fetch"

1. Vérifiez que `VITE_API_BASE_URL` est correctement configuré dans le frontend
2. Vérifiez les CORS dans le backend

---

**Auteur :** Manus AI  
**Version :** 3.1.0

