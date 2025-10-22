# 🔗 Guide Complet SSH - AI CFO Suite Phoenix v3.0

## 🎯 Vue d'Ensemble

AI CFO Suite Phoenix permet de connecter des **agents distants via SSH**, offrant une architecture hybride puissante combinant :

- **Agents locaux** : Exécutés dans le conteneur Docker principal
- **Agents distants** : Connectés via SSH pour traitement délocalisé
- **Orchestrateur intelligent** : Route automatiquement les requêtes

## 🏗️ Architecture SSH

```
┌─────────────────────────────────────────────────────────────┐
│                AI CFO Suite (Docker)                        │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────┐   │
│  │ MetaOrchestrator│    │    SSH Client Manager      │   │
│  │                 │────│  - Connexions chiffrées    │   │
│  │ Route les       │    │  - Pool de connexions      │   │
│  │ requêtes        │    │  - Retry automatique        │   │
│  └─────────────────┘    └─────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │ SSH (Port 22)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Serveur Distant (Linux/Windows)                │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Agent Python │  │ API HTTP     │  │ CLI Personnalisé │ │
│  │ (Script)     │  │ (REST)       │  │ (Bash/PS1)      │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Configuration Rapide pour Tests Locaux

### Option 1 : Test avec WSL (Recommandé pour Windows)

#### 1. Installer WSL

```powershell
# Dans PowerShell en tant qu'Administrateur
wsl --install
# Redémarrer votre machine
```

#### 2. Configurer SSH dans WSL

```bash
# Dans WSL Ubuntu
sudo apt update
sudo apt install openssh-server python3 python3-pip

# Configurer SSH
sudo nano /etc/ssh/sshd_config
# Décommenter ou ajouter :
# Port 22
# PermitRootLogin no
# PasswordAuthentication yes

# Démarrer SSH
sudo service ssh start

# Créer un utilisateur test (optionnel)
sudo useradd -m -s /bin/bash aiagent
sudo passwd aiagent
```

#### 3. Obtenir l'IP de WSL

```bash
ip addr show eth0 | grep inet
# Note: Généralement 172.x.x.x
```

### Option 2 : Test avec Machine Virtuelle

#### Avec VirtualBox/VMware

1. **Créer une VM Ubuntu** (2 GB RAM minimum)
2. **Configurer le réseau** en mode Bridge
3. **Installer SSH** :

```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Option 3 : Test avec Docker SSH

#### Créer un conteneur SSH de test

```dockerfile
# ssh-test-container/Dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    openssh-server \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurer SSH
RUN mkdir /var/run/sshd
RUN echo 'root:testpassword123' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Créer utilisateur test
RUN useradd -m -s /bin/bash aiagent
RUN echo 'aiagent:agent123' | chpasswd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
```

```bash
# Construire et lancer
cd ssh-test-container
docker build -t ssh-test .
docker run -d -p 2222:22 --name ssh-test ssh-test

# Tester la connexion
ssh -p 2222 aiagent@localhost
```

## 🧪 Créer un Agent de Test

### Agent Python Simple

Créez ce script sur votre serveur distant :

```python
#!/usr/bin/env python3
# /home/aiagent/test_agent.py

import sys
import json
import datetime

def process_financial_query(query, context={}):
    """Traite une requête financière simple"""
    
    response_data = {
        "agent": "TestRemoteAgent",
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "response": "",
        "sources": [],
        "tool_calls": [],
        "success": True
    }
    
    # Logique simple basée sur des mots-clés
    query_lower = query.lower()
    
    if "tps" in query_lower or "gst" in query_lower:
        response_data["response"] = """
**TPS/GST au Canada** :
- Taux : 5% 
- Période de déclaration : Trimestrielle ou annuelle selon le chiffre d'affaires
- Date limite : Le 15 du mois suivant la fin de la période
- Remboursement possible pour les entreprises
        """.strip()
        
    elif "tvq" in query_lower:
        response_data["response"] = """
**TVQ au Québec** :
- Taux : 9,975%
- Combiné avec TPS : 14,975% total
- Déclaration harmonisée avec Revenu Québec
- Remboursement pour les entreprises exportatrices
        """.strip()
        
    elif "obligation" in query_lower and "pme" in query_lower:
        response_data["response"] = """
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
        """.strip()
        
    else:
        response_data["response"] = f"""
Je suis un agent de test distant connecté via SSH. 

Votre requête : "{query}"

Types de questions que je peux traiter :
- Questions sur TPS/GST
- Questions sur TVQ
- Obligations fiscales des PME au Québec

Pour des analyses plus poussées, utilisez les agents locaux spécialisés.
        """.strip()
    
    return response_data

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 test_agent.py process '<json_payload>'"}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "process" and len(sys.argv) >= 3:
        try:
            payload = json.loads(sys.argv[2])
            query = payload.get("query", "")
            context = payload.get("context", {})
            
            result = process_financial_query(query, context)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"JSON invalide: {str(e)}"}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": f"Erreur de traitement: {str(e)}"}))
            sys.exit(1)
    
    elif command == "health":
        print(json.dumps({
            "status": "healthy",
            "agent": "TestRemoteAgent",
            "timestamp": datetime.datetime.now().isoformat()
        }))
    
    else:
        print(json.dumps({"error": "Commande non supportée"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Rendez le script exécutable :

```bash
chmod +x /home/aiagent/test_agent.py
```

### Agent API HTTP Simple

```python
#!/usr/bin/env python3
# /home/aiagent/api_agent.py

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import datetime

class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/process':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                query = payload.get('query', '')
                
                response = {
                    "agent": "RemoteAPIAgent",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "response": f"API Agent a traité : {query}",
                    "success": True
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": str(e), "success": False}
                self.wfile.write(json.dumps(error_response).encode())
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health = {"status": "healthy", "agent": "RemoteAPIAgent"}
            self.wfile.write(json.dumps(health).encode())

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), AgentHandler)
    print("API Agent démarré sur port 8080")
    server.serve_forever()
```

```bash
# Lancer l'API en arrière-plan
python3 /home/aiagent/api_agent.py &
```

## 🔧 Configuration dans l'Interface Web

### 1. Accéder à l'Interface Agents

1. Ouvrez http://localhost:3000
2. Cliquez sur "🧠 Agents" dans la sidebar
3. Cliquez sur "➕ Nouvel Agent"

### 2. Configuration Agent SSH - Script Python

```
📋 Informations de Base :
- ID: TestRemoteAgent
- Nom: Agent Test Distant
- Rôle: Agent de test via SSH
- Objectif: Tester les connexions SSH et traitement distant
- Backstory: Agent de démonstration pour valider l'architecture hybride

🔗 Configuration SSH :
☑️ Agent Distant (SSH)
- Hôte SSH: 172.x.x.x (IP de votre WSL/VM)
- Port SSH: 22
- Nom d'utilisateur: aiagent
- Mot de passe SSH: agent123
- Endpoint: /home/aiagent/test_agent.py

🎨 Personnalisation :
- Namespace: test_remote
- Icon: 🌐
- Couleur: #ff6b6b
```

### 3. Configuration Agent SSH - API HTTP

```
📋 Informations de Base :
- ID: TestAPIAgent
- Nom: Agent API Distant
- Rôle: Agent API via SSH
- Objectif: Tester les API distantes via SSH tunneling

🔗 Configuration SSH :
☑️ Agent Distant (SSH)
- Hôte SSH: 172.x.x.x
- Port SSH: 22
- Nom d'utilisateur: aiagent
- Mot de passe SSH: agent123
- Endpoint: http://localhost:8080/process

🎨 Personnalisation :
- Namespace: api_remote
- Icon: 🔌
- Couleur: #4ecdc4
```

## 🧪 Tests Automatisés

### Script PowerShell de Test SSH

```powershell
# test-ssh-agents.ps1

function Test-SSHAgent {
    param(
        [string]$AgentId,
        [string]$TestQuery = "Quelles sont les obligations TPS d'une PME?"
    )
    
    Write-Host "🧪 Test de l'agent SSH: $AgentId" -ForegroundColor Cyan
    
    $body = @{
        query = $TestQuery
        agent_id = $AgentId
        language = "fr"
        jurisdiction = "CA-QC"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/$AgentId/query" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        Write-Host "✅ Succès!" -ForegroundColor Green
        Write-Host "Réponse: $($response.response.Substring(0, [Math]::Min(200, $response.response.Length)))..." -ForegroundColor White
        return $true
        
    } catch {
        Write-Host "❌ Échec: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Tester les agents SSH
Write-Host "🔗 Tests des Agents SSH" -ForegroundColor Yellow
Write-Host "=" * 40

$sshAgents = @("TestRemoteAgent", "TestAPIAgent")

foreach ($agent in $sshAgents) {
    Test-SSHAgent -AgentId $agent
    Write-Host ""
}
```

## 🔐 Sécurité SSH

### Authentification par Clés (Recommandé)

```bash
# Sur votre machine Windows
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ai_cfo_agent

# Copier la clé publique (adaptez l'IP)
scp ~/.ssh/ai_cfo_agent.pub aiagent@172.x.x.x:~/.ssh/authorized_keys

# Dans l'interface, utilisez le chemin de la clé privée
# au lieu du mot de passe
```

### Variables d'Environnement Sécurisées

```env
# backend/.env
SSH_ENCRYPTION_KEY=your-32-byte-encryption-key-here
SSH_TIMEOUT=30
SSH_MAX_CONNECTIONS=10
SSH_RETRY_COUNT=3
```

## 📊 Monitoring SSH

### Vérifier les Connexions

```bash
# Voir les connexions SSH actives
curl "http://localhost:8000/api/v1/agents/ssh/status" | python -m json.tool
```

Réponse attendue :
```json
{
  "ssh_connections": [
    {
      "agent_id": "TestRemoteAgent",
      "host": "172.x.x.x",
      "status": "connected",
      "last_used": "2025-01-14T10:30:00Z",
      "latency_ms": 15,
      "success_rate": 95.5
    }
  ],
  "total_connections": 1,
  "healthy_connections": 1
}
```

### Dashboard Monitoring

Accédez à http://localhost:8000/api/v1/monitoring/health pour voir :

- Latence des connexions SSH
- Taux de succès par agent
- Erreurs de connexion
- Statistiques d'utilisation

## 🛠️ Dépannage

### Problèmes Courants

#### 1. Connexion SSH Refuse

```bash
# Vérifier le service SSH
sudo systemctl status ssh

# Vérifier le port
netstat -tlnp | grep :22

# Tester manuellement
ssh -v aiagent@172.x.x.x
```

#### 2. Agent ne Répond Pas

```bash
# Tester l'agent directement
python3 /home/aiagent/test_agent.py process '{"query":"test"}'

# Vérifier les permissions
ls -la /home/aiagent/test_agent.py
```

#### 3. Timeout de Connexion

```env
# Augmenter les timeouts dans .env
SSH_TIMEOUT=60
AGENT_TIMEOUT=120
```

### Logs de Débogage

```bash
# Logs spécifiques aux agents SSH
docker-compose logs backend | grep -i ssh

# Logs d'un agent spécifique
docker-compose logs backend | grep TestRemoteAgent
```

## 🎓 Cas d'Usage Avancés

### 1. Agent de Calcul Intensif

```python
# Agent pour calculs complexes (ex: ML, optimisation)
# Déployé sur serveur haute performance
```

### 2. Agent Spécialisé par Juridiction

```python
# Agent français sur serveur en France
# Agent américain sur serveur aux USA
# Routing automatique basé sur la juridiction
```

### 3. Load Balancing SSH

```python
# Plusieurs instances du même agent
# Distribution de charge automatique
# Failover en cas de panne
```

## 🚀 Prochaines Étapes

1. **Tester la configuration de base**
2. **Créer vos agents personnalisés**
3. **Implémenter l'authentification par clés**
4. **Configurer le monitoring**
5. **Déployer en production avec HTTPS/VPN**

---

**Votre architecture hybride SSH est maintenant opérationnelle ! 🎉**

## 📞 Support

- **Documentation complète** : Consultez le README.md principal
- **API Reference** : http://localhost:8000/docs
- **Troubleshooting** : Vérifiez les logs avec `docker-compose logs -f`