# AI CFO Suite Phoenix - Script de Démarrage
# Version 3.0 - PowerShell

param(
    [switch]$Clean = $false,
    [switch]$Logs = $false,
    [string]$OpenRouterKey = ""
)

Write-Host "🚀 AI CFO Suite Phoenix v3.0 - Démarrage" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Vérifier si Docker est installé
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ Erreur: Docker ou Docker Compose n'est pas installé!" -ForegroundColor Red
    Write-Host "📥 Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Configurer la clé OpenRouter si fournie
if ($OpenRouterKey -ne "") {
    Write-Host "🔑 Configuration de la clé OpenRouter..." -ForegroundColor Yellow
    $envPath = ".\backend\.env"
    if (Test-Path $envPath) {
        (Get-Content $envPath) -replace "OPENROUTER_API_KEY=.*", "OPENROUTER_API_KEY=$OpenRouterKey" | Set-Content $envPath
        Write-Host "✅ Clé OpenRouter configurée!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Fichier .env non trouvé dans backend/" -ForegroundColor Yellow
    }
}

# Nettoyer les volumes si demandé
if ($Clean) {
    Write-Host "🧹 Nettoyage des volumes existants..." -ForegroundColor Yellow
    docker-compose down -v
    docker system prune -f
}

# Arrêter les conteneurs existants
Write-Host "🛑 Arrêt des conteneurs existants..." -ForegroundColor Yellow
docker-compose down

# Construire et démarrer les services
Write-Host "🔨 Construction et démarrage des services..." -ForegroundColor Yellow
docker-compose up -d --build

# Attendre que les services démarrent
Write-Host "⏳ Attente du démarrage des services (60s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Vérifier l'état des services
Write-Host "📊 État des services:" -ForegroundColor Cyan
docker-compose ps

# Initialiser les agents par défaut
Write-Host "🤖 Initialisation des agents par défaut..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/init-defaults" -Method POST
    Write-Host "✅ Agents initialisés avec succès!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Échec d'initialisation des agents (normal au premier démarrage)" -ForegroundColor Yellow
}

# Vérifier les services
$services = @(
    @{Name="Frontend"; URL="http://localhost:3000"; Port=3000}
    @{Name="Backend API"; URL="http://localhost:8000/docs"; Port=8000}
    @{Name="Backend Health"; URL="http://localhost:8000/api/v1/monitoring/health"; Port=8000}
    @{Name="Qdrant Dashboard"; URL="http://localhost:6333/dashboard"; Port=6333}
    @{Name="MinIO Console"; URL="http://localhost:9001"; Port=9001}
)

Write-Host ""
Write-Host "🔍 Vérification des services..." -ForegroundColor Cyan

foreach ($service in $services) {
    try {
        $null = Test-NetConnection -ComputerName "localhost" -Port $service.Port -WarningAction SilentlyContinue -ErrorAction Stop
        Write-Host "✅ $($service.Name): $($service.URL)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($service.Name): Indisponible sur le port $($service.Port)" -ForegroundColor Red
    }
}

# Afficher les informations de connexion
Write-Host ""
Write-Host "🎉 AI CFO Suite Phoenix est prêt!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""
Write-Host "📱 URLs d'accès:" -ForegroundColor Cyan
Write-Host "   • Application Web:    http://localhost:3000" -ForegroundColor White
Write-Host "   • API Documentation:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Monitoring:         http://localhost:8000/api/v1/monitoring/health" -ForegroundColor White
Write-Host "   • Qdrant Dashboard:   http://localhost:6333/dashboard" -ForegroundColor White
Write-Host "   • MinIO Console:      http://localhost:9001 (admin/minioadmin123)" -ForegroundColor White
Write-Host ""
Write-Host "🗄️  Bases de données:" -ForegroundColor Cyan
Write-Host "   • PostgreSQL:         localhost:5432 (aicfo/aicfo_secure_pass_2025)" -ForegroundColor White
Write-Host "   • Redis:              localhost:6379" -ForegroundColor White
Write-Host "   • Qdrant Vector DB:   localhost:6333" -ForegroundColor White
Write-Host ""

if ($OpenRouterKey -eq "") {
    Write-Host "⚠️  IMPORTANT: Configurez votre clé OpenRouter dans backend/.env" -ForegroundColor Yellow
    Write-Host "   OPENROUTER_API_KEY=sk-or-v1-your-key-here" -ForegroundColor Yellow
    Write-Host "   Obtenez votre clé: https://openrouter.ai/" -ForegroundColor Yellow
    Write-Host ""
}

# Proposer d'afficher les logs
if ($Logs) {
    Write-Host "📋 Affichage des logs en temps réel..." -ForegroundColor Yellow
    Write-Host "   (Ctrl+C pour arrêter)" -ForegroundColor Gray
    docker-compose logs -f
} else {
    Write-Host "💡 Commandes utiles:" -ForegroundColor Cyan
    Write-Host "   • Voir les logs:      docker-compose logs -f" -ForegroundColor White
    Write-Host "   • Arrêter les services: docker-compose down" -ForegroundColor White
    Write-Host "   • Redémarrer:         .\start-ai-cfo.ps1" -ForegroundColor White
    Write-Host "   • Nettoyer:           .\start-ai-cfo.ps1 -Clean" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Ouvrez http://localhost:3000 pour commencer!" -ForegroundColor Green
}