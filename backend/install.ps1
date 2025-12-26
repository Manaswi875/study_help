# Installation script for Adaptive Study Planner Backend

Write-Host "🚀 Installing Adaptive Study Planner Backend..." -ForegroundColor Cyan
Write-Host ""

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install core dependencies first (most important)
Write-Host ""
Write-Host "📦 Installing core dependencies..." -ForegroundColor Cyan
python -m pip install fastapi uvicorn sqlalchemy pydantic python-dotenv

# Install additional dependencies
Write-Host ""
Write-Host "📦 Installing additional dependencies..." -ForegroundColor Cyan
python -m pip install alembic psycopg2-binary python-jose passlib pydantic-settings email-validator pytz loguru python-multipart

# Install integration dependencies
Write-Host ""
Write-Host "📦 Installing integration dependencies..." -ForegroundColor Cyan
python -m pip install celery redis google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client notion-client httpx

# Verify installation
Write-Host ""
Write-Host "✅ Verifying installation..." -ForegroundColor Green
python -c "import fastapi, sqlalchemy, pydantic; print('✓ Core packages installed successfully')"

Write-Host ""
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Set up PostgreSQL database (see QUICKSTART.md)"
Write-Host "2. Update .env file with your database credentials"
Write-Host "3. Run: python run.py"
Write-Host "4. Visit: http://localhost:8000/api/docs"
Write-Host ""
