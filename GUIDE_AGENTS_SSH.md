# 🧠 Guide de Gestion des Agents - AI CFO Suite Phoenix v2.0

## 🎯 Vue d'ensemble

Le système d'agents de l'AI CFO Suite vous permet de :

1. **Éditer les prompts système** de chaque agent via l'interface web
2. **Créer de nouveaux agents** locaux ou distants
3. **Connecter des agents distants via SSH** en fournissant simplement leur adresse
4. **Gérer dynamiquement** tous les agents sans redémarrer le système

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Web Admin                       │
│  Créer | Éditer | Supprimer | Tester SSH                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Base de Données PostgreSQL                      │
│  Configuration complète de chaque agent                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            Orchestrateur d'Agents Dynamique                  │
│  Charge | Route | Exécute les agents                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
┌───────────────────────┐    ┌───────────────────────┐
│   Agents Locaux       │    │   Agents Distants     │
│   (Python)            │    │   (via SSH)           │
│   - RAG intégré       │    │   - Serveurs externes │
│   - Qdrant local      │    │   - API REST/CLI      │
└───────────────────────┘    └───────────────────────┘
```

## 📝 Créer un Agent Local

### Via l'Interface Web

1. **Accédez à la page Agents** : Cliquez sur "🧠 Agents" dans la sidebar
2. **Cliquez sur "➕ Nouvel Agent"**
3. **Remplissez le formulaire** :

#### Informations de Base
- **ID** : Identifiant unique (ex: `SalesAgent`, `HRAgent`)
- **Nom** : Nom d'affichage (ex: "Agent Commercial")
- **Rôle** : Titre/fonction (ex: "Expert en Ventes B2B")
- **Objectif** : But principal de l'agent
- **Backstory** : Contexte et expertise

#### Prompt Système (Optionnel)
```
Tu es un expert en ventes B2B avec 10 ans d'expérience.

Ton rôle est d'analyser les opportunités commerciales et de recommander des stratégies de closing.

Instructions :
1. Analyse les données de vente fournies
2. Identifie les patterns et tendances
3. Recommande des actions concrètes
4. Cite toujours tes sources

Réponds en français de manière professionnelle.
```

#### Configuration
- **Namespace** : Collection Qdrant (ex: `sales`, `hr`, `legal`)
- **Icon** : Emoji (ex: 💼, 📈, ⚖️)
- **Couleur** : Code hex (ex: #64ffda)

4. **Cliquez sur "💾 Sauvegarder"**

L'agent est immédiatement disponible dans le Playground !

## 🌐 Connecter un Agent Distant via SSH

### Prérequis

Votre agent distant doit :
- Être accessible via SSH
- Exposer une API REST ou un CLI pour traiter les requêtes
- Retourner des réponses en JSON

### Exemple d'Agent Distant (Python)

```python
#!/usr/bin/env python3
# agent_remote.py

import sys
import json

def process_query(query, context):
    """Process a query and return response"""
    return {
        "agent": "RemoteAgent",
        "response": f"Traitement de : {query}",
        "sources": [],
        "tool_calls": []
    }

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "process":
        payload = json.loads(sys.argv[2])
        result = process_query(
            payload.get("query", ""),
            payload.get("context", {})
        )
        print(json.dumps(result))
```

### Configuration SSH dans l'Interface

1. **Accédez à la page Agents**
2. **Créez un nouvel agent**
3. **Cochez "Agent Distant (SSH)"**
4. **Remplissez la configuration SSH** :

#### Configuration SSH
- **Hôte SSH** : `192.168.1.100` ou `agent.example.com`
- **Port SSH** : `22` (par défaut)
- **Nom d'utilisateur** : `ubuntu` ou `root`
- **Mot de passe SSH** : Votre mot de passe (sera chiffré)
  - OU
- **Chemin de la clé privée** : `/home/user/.ssh/id_rsa`
- **Endpoint** : `/home/ubuntu/agent_remote.py` ou `http://localhost:8000/api/process`

5. **Cliquez sur "🔌 Tester la Connexion SSH"**
   - ✅ Si succès : "Connexion SSH réussie !"
   - ❌ Si échec : Vérifiez les credentials et la connectivité

6. **Sauvegardez l'agent**

### Types d'Endpoints Supportés

#### 1. CLI Python
```
Endpoint: /home/ubuntu/agent_remote.py
Commande exécutée: python3 /home/ubuntu/agent_remote.py process '{"query":"...", "context":{...}}'
```

#### 2. API HTTP
```
Endpoint: http://localhost:8000/api/process
Commande exécutée: curl -X POST http://localhost:8000/api/process -H "Content-Type: application/json" -d '{"query":"...", "context":{...}}'
```

## 🔧 Éditer un Agent Existant

1. **Sélectionnez l'agent** dans la liste
2. **Cliquez sur "✏️ Éditer"**
3. **Modifiez les champs** souhaités
4. **Sauvegardez**

Les modifications sont appliquées **immédiatement** sans redémarrage.

## 🎨 Personnaliser le Prompt Système

Le prompt système définit le comportement de l'agent. Vous pouvez :

### Exemple de Prompt Avancé

```
Tu es {nom}, un {rôle}.

CONTEXTE :
{backstory}

OBJECTIF :
{goal}

INSTRUCTIONS SPÉCIFIQUES :
1. Analyse approfondie des données fournies
2. Utilisation obligatoire de la base de connaissances RAG
3. Citations des sources avec numéros de page si disponibles
4. Recommandations actionnables et mesurables
5. Format de réponse structuré :
   - Résumé exécutif (3 lignes max)
   - Analyse détaillée
   - Recommandations numérotées
   - Sources consultées

CONTRAINTES :
- Réponds uniquement dans ton domaine d'expertise
- Si tu ne sais pas, dis "Je n'ai pas suffisamment d'informations"
- Évite les spéculations
- Reste factuel et professionnel

STYLE :
- Ton : Professionnel et accessible
- Langue : Français
- Format : Markdown avec sections claires

Commence chaque réponse par : "En tant que {nom}, voici mon analyse :"
```

## 🔄 Hot-Reload des Agents

Le système supporte le **hot-reload** :

1. Modifiez un agent dans l'interface
2. Cliquez sur "🔄 Recharger" (ou sauvegardez)
3. Les agents sont rechargés **sans redémarrer le backend**

## 📊 Monitoring des Agents

### Statistiques Disponibles

- **Nombre de requêtes** : Total de requêtes traitées
- **Dernière requête** : Timestamp de la dernière utilisation
- **Statut** : Actif / Inactif
- **Type** : Local / Distant (SSH)

### Voir les Statistiques

```bash
# Via API
curl http://localhost:8000/api/v1/agents

# Réponse
{
  "agents": [
    {
      "id": "AccountantAgent",
      "name": "Expert Comptable",
      "query_count": 42,
      "last_query": "2025-10-08T10:30:00",
      "is_active": true,
      "is_remote": false
    }
  ]
}
```

## 🔐 Sécurité SSH

### Bonnes Pratiques

1. **Utilisez des clés SSH** plutôt que des mots de passe
   ```bash
   # Générer une paire de clés
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/ai_cfo_agent
   
   # Copier la clé publique sur le serveur distant
   ssh-copy-id -i ~/.ssh/ai_cfo_agent.pub user@remote-host
   ```

2. **Limitez les permissions**
   ```bash
   # Sur le serveur distant
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

3. **Utilisez un utilisateur dédié**
   ```bash
   # Créer un utilisateur pour les agents
   sudo useradd -m -s /bin/bash ai-agent
   sudo su - ai-agent
   ```

4. **Configurez le firewall**
   ```bash
   # Autoriser uniquement l'IP du serveur AI CFO Suite
   sudo ufw allow from 192.168.1.50 to any port 22
   ```

### Chiffrement des Mots de Passe

⚠️ **Note** : Dans la version actuelle, les mots de passe SSH sont stockés en clair dans PostgreSQL.

**Pour la production**, implémentez le chiffrement :

```python
from cryptography.fernet import Fernet

# Générer une clé (à stocker dans .env)
key = Fernet.generate_key()
cipher = Fernet(key)

# Chiffrer
encrypted_password = cipher.encrypt(password.encode())

# Déchiffrer
decrypted_password = cipher.decrypt(encrypted_password).decode()
```

## 🧪 Tester un Agent

### Via l'Interface

1. Accédez au **Playground**
2. Posez une question
3. L'orchestrateur route automatiquement vers le bon agent

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quelles sont les déductions fiscales pour une PME ?",
    "agent": "TaxAgent"
  }'
```

## 📚 Exemples d'Agents Personnalisés

### Agent Juridique

```
ID: LegalAgent
Nom: Conseiller Juridique
Rôle: Expert en Droit des Affaires Canadien
Objectif: Fournir des conseils juridiques précis et conformes
Backstory: Avocat spécialisé en droit commercial avec 12 ans d'expérience
Namespace: legal
Keywords: contrat, juridique, légal, loi, réglementation
```

### Agent RH

```
ID: HRAgent
Nom: Spécialiste RH
Rôle: Expert en Ressources Humaines
Objectif: Optimiser la gestion des talents et la conformité RH
Backstory: Professionnel RH certifié CRHA avec expertise en droit du travail québécois
Namespace: hr
Keywords: employé, salaire, embauche, licenciement, congé
```

### Agent Commercial Distant (SSH)

```
ID: SalesAgentRemote
Nom: Agent Commercial IA
Rôle: Analyste des Ventes
is_remote: true
ssh_host: 192.168.1.200
ssh_username: sales-bot
ssh_key_path: /home/ubuntu/.ssh/sales_agent_key
ssh_endpoint: /opt/sales-agent/process.py
```

## 🚨 Dépannage

### Agent ne répond pas

1. **Vérifier le statut** :
   ```bash
   curl http://localhost:8000/api/v1/agents/{agent_id}
   ```

2. **Vérifier les logs** :
   ```bash
   docker-compose logs backend | grep "{agent_id}"
   ```

3. **Recharger les agents** :
   ```bash
   curl -X POST http://localhost:8000/api/v1/agents/reload
   ```

### Connexion SSH échoue

1. **Tester manuellement** :
   ```bash
   ssh -p 22 user@host
   ```

2. **Vérifier les credentials** dans l'interface Admin

3. **Vérifier le firewall** :
   ```bash
   telnet host 22
   ```

### Agent distant ne retourne pas de JSON

Assurez-vous que votre agent distant :
- Retourne du JSON valide
- Utilise `print()` pour stdout
- Ne mélange pas stdout et stderr

## 📖 API Complète

### Endpoints Agents

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/agents` | Liste tous les agents |
| GET | `/api/v1/agents/{id}` | Détails d'un agent |
| POST | `/api/v1/agents` | Créer un agent |
| PUT | `/api/v1/agents/{id}` | Modifier un agent |
| DELETE | `/api/v1/agents/{id}` | Supprimer un agent |
| POST | `/api/v1/agents/ssh/test` | Tester connexion SSH |
| GET | `/api/v1/agents/ssh/status` | Statut connexions SSH |
| POST | `/api/v1/agents/reload` | Recharger les agents |
| POST | `/api/v1/agents/init-defaults` | Initialiser agents par défaut |

Documentation complète : http://localhost:8000/docs

## 🎓 Bonnes Pratiques

1. **Nommage** : Utilisez des IDs clairs (ex: `TaxAgentQC` pour Québec)
2. **Namespaces** : Séparez par domaine (`finance_tax`, `finance_accounting`)
3. **Keywords** : Ajoutez des mots-clés pour le routing automatique
4. **Prompts** : Soyez spécifique et structuré
5. **Tests** : Testez toujours la connexion SSH avant de sauvegarder
6. **Documentation** : Documentez vos agents personnalisés
7. **Monitoring** : Surveillez les statistiques d'utilisation

---

**Vous avez maintenant le contrôle total sur vos agents ! 🚀**
