#!/bin/bash
# Script de démarrage du backend AI CFO Suite Phoenix

set -e

echo "========================================="
echo "AI CFO Suite Phoenix - Backend Startup"
echo "========================================="
echo ""

# Vérifier si le fichier .env existe
if [ ! -f backend/.env ]; then
    echo "⚠️  Fichier .env non trouvé. Création à partir de .env.example..."
    cp backend/.env.example backend/.env
    echo "✅ Fichier .env créé. Veuillez le configurer avec vos clés API."
    echo ""
fi

# Vérifier le mode de démarrage
MODE=${1:-docker}

if [ "$MODE" = "docker" ]; then
    echo "🐳 Démarrage en mode Docker Compose..."
    echo ""
    
    # Vérifier si Docker est installé
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Démarrer les services
    docker-compose up --build
    
elif [ "$MODE" = "local" ]; then
    echo "💻 Démarrage en mode local..."
    echo ""
    
    # Vérifier si Python est installé
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Installer les dépendances
    echo "📦 Installation des dépendances..."
    cd backend
    pip3 install -q -r requirements.txt
    
    echo ""
    echo "🚀 Démarrage du serveur backend..."
    python3 main.py
    
else
    echo "❌ Mode inconnu: $MODE"
    echo "Usage: $0 [docker|local]"
    echo "  docker - Démarre avec Docker Compose (par défaut)"
    echo "  local  - Démarre en mode local avec Python"
    exit 1
fi
