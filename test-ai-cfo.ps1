# AI CFO Suite Phoenix - Script de Test
# Version 3.0 - PowerShell

param(
    [switch]$Quick = $false,
    [switch]$Full = $false,
    [string]$TestQuery = "Quelles sont les principales obligations fiscales d'une PME au Québec?"
)

Write-Host "🧪 AI CFO Suite Phoenix v3.0 - Tests Automatisés" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

function Test-Service {
    param(
        [string]$Name,
        [string]$URL,
        [int]$Port,
        [string]$ExpectedText = ""
    )
    
    try {
        $response = Invoke-RestMethod -Uri $URL -TimeoutSec 5 -ErrorAction Stop
        if ($ExpectedText -ne "" -and $response -notlike "*$ExpectedText*") {
            throw "Réponse inattendue"
        }
        Write-Host "✅ $Name : OK" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ $Name : ÉCHEC ($($_.Exception.Message))" -ForegroundColor Red
        return $false
    }
}

function Test-Database {
    param(
        [string]$Name,
        [string]$Host,
        [int]$Port
    )
    
    try {
        $connection = Test-NetConnection -ComputerName $Host -Port $Port -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "✅ $Name : Accessible sur port $Port" -ForegroundColor Green
            return $true
        } else {
            throw "Port inaccessible"
        }
    } catch {
        Write-Host "❌ $Name : ÉCHEC (Port $Port inaccessible)" -ForegroundColor Red
        return $false
    }
}

function Test-Agent {
    param(
        [string]$Query,
        [string]$AgentId = "",
        [string]$Model = "mistralai/mistral-7b-instruct"
    )
    
    $endpoint = if ($AgentId -ne "") {
        "http://localhost:8000/api/v1/agents/$AgentId/query"
    } else {
        "http://localhost:8000/api/v1/meta/query"
    }
    
    $body = @{
        query = $Query
        language = "fr"
        jurisdiction = "CA-QC"
        model = $Model
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $endpoint -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        Write-Host "✅ Agent Response: $($response.response.Substring(0, [Math]::Min(100, $response.response.Length)))..." -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Agent Test ÉCHEC: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# ===============================
# TESTS INFRASTRUCTURE
# ===============================

Write-Host "🏗️  Tests Infrastructure" -ForegroundColor Yellow
Write-Host "-" * 30

$infrastructureTests = @(
    @{Name="PostgreSQL"; Host="localhost"; Port=5432}
    @{Name="Qdrant"; Host="localhost"; Port=6333}
    @{Name="Redis"; Host="localhost"; Port=6379}
    @{Name="MinIO"; Host="localhost"; Port=9000}
)

$infrastructureResults = @()
foreach ($test in $infrastructureTests) {
    $result = Test-Database -Name $test.Name -Host $test.Host -Port $test.Port
    $infrastructureResults += $result
}

# ===============================
# TESTS API
# ===============================

Write-Host ""
Write-Host "🌐 Tests API Services" -ForegroundColor Yellow
Write-Host "-" * 30

$apiTests = @(
    @{Name="Backend Health"; URL="http://localhost:8000/api/v1/monitoring/health"}
    @{Name="Frontend"; URL="http://localhost:3000"}
    @{Name="API Documentation"; URL="http://localhost:8000/docs"}
    @{Name="Qdrant Dashboard"; URL="http://localhost:6333/dashboard"}
    @{Name="MinIO Console"; URL="http://localhost:9001"}
)

$apiResults = @()
foreach ($test in $apiTests) {
    $result = Test-Service -Name $test.Name -URL $test.URL
    $apiResults += $result
}

# ===============================
# TESTS AGENTS
# ===============================

if (-not $Quick) {
    Write-Host ""
    Write-Host "🤖 Tests Agents" -ForegroundColor Yellow
    Write-Host "-" * 30
    
    # Vérifier les agents disponibles
    try {
        $agents = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents" -TimeoutSec 10
        Write-Host "✅ Agents disponibles: $($agents.agents.Count)" -ForegroundColor Green
        
        # Lister les agents
        foreach ($agent in $agents.agents) {
            Write-Host "   • $($agent.name) ($($agent.id))" -ForegroundColor Gray
        }
    } catch {
        Write-Host "❌ Impossible de récupérer la liste des agents" -ForegroundColor Red
    }
    
    # Test du MetaOrchestrator
    Write-Host ""
    Write-Host "🎯 Test MetaOrchestrator avec requête: '$TestQuery'" -ForegroundColor Cyan
    $agentTest = Test-Agent -Query $TestQuery
}

# ===============================
# TESTS OPTIONNELS (Mode Full)
# ===============================

if ($Full) {
    Write-Host ""
    Write-Host "🔬 Tests Approfondis (Mode Full)" -ForegroundColor Yellow
    Write-Host "-" * 40
    
    # Test upload de document
    Write-Host "📄 Test Upload Document..." -ForegroundColor Cyan
    
    # Créer un fichier test
    $testFile = "test-document.txt"
    $testContent = @"
RAPPORT FINANCIER TEST
=====================

Revenus: 250,000 CAD
Charges: 180,000 CAD
Bénéfice net: 70,000 CAD

Taxes à payer:
- TPS (5%): 12,500 CAD
- TVQ (9.975%): 24,937.50 CAD
"@
    
    $testContent | Out-File -FilePath $testFile -Encoding UTF8
    
    try {
        $fileBytes = [System.IO.File]::ReadAllBytes($testFile)
        $fileContent = [System.Convert]::ToBase64String($fileBytes)
        
        $uploadBody = @{
            filename = $testFile
            content = $fileContent
            document_type = "financial_report"
            country = "CA"
            province = "QC"
        } | ConvertTo-Json
        
        $uploadResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/upload" -Method POST -Body $uploadBody -ContentType "application/json" -TimeoutSec 30
        Write-Host "✅ Upload Document: OK (ID: $($uploadResponse.document_id))" -ForegroundColor Green
        
        # Test recherche dans le document
        Start-Sleep -Seconds 5
        $searchBody = @{
            query = "Combien de taxes dois-je payer?"
            use_context = $true
        } | ConvertTo-Json
        
        $searchResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/meta/query" -Method POST -Body $searchBody -ContentType "application/json" -TimeoutSec 30
        Write-Host "✅ Recherche dans Document: OK" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Test Upload/Recherche: ÉCHEC ($($_.Exception.Message))" -ForegroundColor Red
    } finally {
        # Nettoyer le fichier test
        if (Test-Path $testFile) {
            Remove-Item $testFile -Force
        }
    }
    
    # Test fonctionnalités i18n
    Write-Host ""
    Write-Host "🌍 Test Multilingue (i18n)..." -ForegroundColor Cyan
    
    # Test en français
    $frenchTest = Test-Agent -Query "Quelle est la date limite pour déclarer la TPS au Canada?" -Model "mistralai/mistral-7b-instruct"
    
    # Test en anglais
    $englishBody = @{
        query = "What is the deadline for GST filing in Canada?"
        language = "en"
        jurisdiction = "CA"
        model = "mistralai/mistral-7b-instruct"
    } | ConvertTo-Json
    
    try {
        $englishResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/meta/query" -Method POST -Body $englishBody -ContentType "application/json" -TimeoutSec 30
        Write-Host "✅ Test Anglais: OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ Test Anglais: ÉCHEC" -ForegroundColor Red
    }
}

# ===============================
# RÉSUMÉ DES TESTS
# ===============================

Write-Host ""
Write-Host "📊 Résumé des Tests" -ForegroundColor Cyan
Write-Host "=" * 40

$totalTests = $infrastructureResults.Count + $apiResults.Count
$passedTests = ($infrastructureResults + $apiResults | Where-Object { $_ -eq $true }).Count

if (-not $Quick) {
    $totalTests += 1
    if ($agentTest) { $passedTests += 1 }
}

Write-Host "Total: $totalTests tests" -ForegroundColor White
Write-Host "Réussis: $passedTests" -ForegroundColor Green
Write-Host "Échoués: $($totalTests - $passedTests)" -ForegroundColor Red
Write-Host "Taux de réussite: $([Math]::Round($passedTests / $totalTests * 100, 1))%" -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } else { "Yellow" })

# ===============================
# RECOMMANDATIONS
# ===============================

Write-Host ""
Write-Host "💡 Recommandations" -ForegroundColor Yellow
Write-Host "-" * 20

if ($passedTests -eq $totalTests) {
    Write-Host "🎉 Tous les tests sont passés ! AI CFO Suite est prêt." -ForegroundColor Green
    Write-Host "🚀 Vous pouvez utiliser l'application: http://localhost:3000" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Certains services ne fonctionnent pas correctement." -ForegroundColor Yellow
    Write-Host "📋 Actions recommandées:" -ForegroundColor Cyan
    Write-Host "   • Vérifiez les logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "   • Redémarrez les services: docker-compose restart" -ForegroundColor White
    Write-Host "   • Vérifiez la configuration .env" -ForegroundColor White
}

Write-Host ""
Write-Host "🔧 Autres commandes utiles:" -ForegroundColor Cyan
Write-Host "   • Tests rapides:     .\test-ai-cfo.ps1 -Quick" -ForegroundColor White
Write-Host "   • Tests complets:    .\test-ai-cfo.ps1 -Full" -ForegroundColor White
Write-Host "   • Logs en temps réel: docker-compose logs -f" -ForegroundColor White
Write-Host "   • Arrêter services:   docker-compose down" -ForegroundColor White