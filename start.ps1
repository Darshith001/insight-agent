# InsightAgent - One-click startup script
# Run from project root: .\start.ps1

$ROOT = $PSScriptRoot
$VENV = "$ROOT\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   InsightAgent - Starting up..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Qdrant
Write-Host "[1/4] Checking Qdrant..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "http://localhost:6333" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "      Qdrant already running OK" -ForegroundColor Green
} catch {
    Write-Host "      Starting Qdrant via Docker..." -ForegroundColor Yellow
    Start-Process "docker" -ArgumentList "compose -f infra/docker-compose.yml up -d qdrant" -WorkingDirectory $ROOT -NoNewWindow -Wait
    Start-Sleep -Seconds 3
}

# 2. Start Router
Write-Host "[2/4] Starting Router (port 8100)..." -ForegroundColor Yellow
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", `
    "cd '$ROOT'; & '$VENV'; uvicorn services.router.server:app --port 8100" `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# 3. Start API
Write-Host "[3/4] Starting API (port 8000)..." -ForegroundColor Yellow
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", `
    "cd '$ROOT'; & '$VENV'; uvicorn apps.api.app.main:app --port 8000" `
    -WindowStyle Normal

Start-Sleep -Seconds 4

# 4. Start Frontend
Write-Host "[4/4] Starting Frontend (port 3000)..." -ForegroundColor Yellow
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", `
    "cd '$ROOT\apps\web'; pnpm dev" `
    -WindowStyle Normal

Start-Sleep -Seconds 5

# 5. Verify
Write-Host ""
Write-Host "Verifying services..." -ForegroundColor Yellow
$all_ok = $true

@(
    @{name="Qdrant";   url="http://localhost:6333"},
    @{name="Router";   url="http://localhost:8100/health"},
    @{name="API";      url="http://localhost:8000/health"},
    @{name="Frontend"; url="http://localhost:3000"}
) | ForEach-Object {
    try {
        Invoke-WebRequest -Uri $_.url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop | Out-Null
        Write-Host "  [OK] $($_.name)" -ForegroundColor Green
    } catch {
        Write-Host "  [!!] $($_.name) not ready yet - may need a few more seconds" -ForegroundColor Red
        $all_ok = $false
    }
}

Write-Host ""
if ($all_ok) {
    Write-Host "All services running!" -ForegroundColor Green
} else {
    Write-Host "Some services still starting - wait 10s and check manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Open: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Open browser automatically
Start-Process "http://localhost:3000"
