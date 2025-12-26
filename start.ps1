# Adaptive Study Planner - Startup Script
# This script starts both backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Adaptive Study Planner - Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($command)
    $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command python)) {
    Write-Host "❌ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command node)) {
    Write-Host "❌ Node.js not found! Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Python found: $(python --version)" -ForegroundColor Green
Write-Host "✅ Node.js found: $(node --version)" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Backend Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$backendPath = Join-Path $PSScriptRoot "backend"
$venvPath = Join-Path $backendPath "venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first: cd backend && python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Start backend in new window
$backendScript = @"
cd '$backendPath'
& '$venvPath'
Write-Host 'Backend starting on http://localhost:8000' -ForegroundColor Green
Write-Host 'API Docs: http://localhost:8000/api/docs' -ForegroundColor Green
Write-Host ''
python run.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Write-Host "✅ Backend server starting in new window..." -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$frontendPath = Join-Path $PSScriptRoot "frontend"

if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "❌ Frontend dependencies not installed!" -ForegroundColor Red
    Write-Host "Please run: cd frontend && npm install" -ForegroundColor Yellow
    exit 1
}

# Start frontend in new window
$frontendScript = @"
cd '$frontendPath'
Write-Host 'Frontend starting on http://localhost:3000' -ForegroundColor Green
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host "✅ Frontend server starting in new window..." -ForegroundColor Green
Write-Host "   URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Summary
Start-Sleep -Seconds 2
Write-Host "========================================" -ForegroundColor Green
Write-Host "  🎉 Servers Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to open the application in your browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Application opened in browser!" -ForegroundColor Green
Write-Host "Close the backend and frontend windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
