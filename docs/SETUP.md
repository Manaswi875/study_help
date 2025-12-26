# Setup Guide - Adaptive Study Planner

This guide will help you set up the Adaptive Study Planner development environment.

---

## Prerequisites

### Required Software
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 13+** - [Download](https://www.postgresql.org/download/)
- **Node.js 16+** - [Download](https://nodejs.org/) (for frontend)
- **Git** - [Download](https://git-scm.com/downloads)

### Optional (Recommended)
- **Redis** - For task queue (Celery)
- **Docker** - For containerized deployment
- **VS Code** - Recommended IDE

---

## Backend Setup

### 1. Clone Repository
```bash
cd c:\Users\seela\Desktop\study_help
```

### 2. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell)**:
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD)**:
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac**:
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Set Up PostgreSQL Database

**Create Database**:
```sql
-- Connect to PostgreSQL (psql or pgAdmin)
CREATE DATABASE study_planner;
CREATE USER study_planner_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE study_planner TO study_planner_user;
```

### 6. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Database
DATABASE_URL="postgresql://study_planner_user:your_secure_password@localhost:5432/study_planner"

# Security
SECRET_KEY="generate-a-secure-random-key-here"

# Google Calendar (get from Google Cloud Console)
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"

# Notion (get from Notion integrations)
NOTION_CLIENT_ID="your-notion-client-id"
NOTION_CLIENT_SECRET="your-notion-client-secret"
```

**Generate SECRET_KEY**:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 7. Initialize Database

```bash
# Create tables
python -c "from config.database import init_db; init_db()"
```

Or use Alembic for migrations:
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 8. Run Development Server

```bash
python app.py
```

Or with auto-reload:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

---

## Google Calendar API Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Study Planner"
3. Enable **Google Calendar API**

### 2. Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/google/callback`
   - `http://localhost:3000/auth/callback` (for frontend)
5. Copy **Client ID** and **Client Secret** to `.env`

### 3. Configure OAuth Consent Screen
1. Go to "OAuth consent screen"
2. User type: "External"
3. Add scopes:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/calendar.events`
4. Add test users (your email)

---

## Notion API Setup

### 1. Create Notion Integration
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name: "Study Planner"
4. Associated workspace: Select your workspace
5. Capabilities: Read, Update, Insert content
6. Copy **Internal Integration Token** to `.env` as `NOTION_ACCESS_TOKEN`

### 2. Share Database with Integration
1. Create a new database in Notion: "Study Tasks"
2. Click "Share" in top-right
3. Invite your integration: "Study Planner"
4. Copy database ID from URL:
   - URL: `https://notion.so/workspace/abc123?v=xyz`
   - Database ID: `abc123`

---

## Redis Setup (Optional - for Celery)

### Windows
Download and install Redis for Windows:
- [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

Or use Docker:
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Mac
brew install redis
```

Start Redis:
```bash
redis-server
```

### Run Celery Worker
```bash
celery -A services.tasks worker --loglevel=info
```

### Run Celery Beat (Scheduled Tasks)
```bash
celery -A services.tasks beat --loglevel=info
```

---

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

View coverage report: `open htmlcov/index.html`

### Run Specific Test File
```bash
pytest tests/test_mastery_engine.py
```

---

## Database Migrations

### Create New Migration
```bash
alembic revision --autogenerate -m "Add new field to User"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic history
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Connection refused" to PostgreSQL
**Solution**: Check PostgreSQL is running:
```bash
# Windows
pg_ctl status

# Linux/Mac
sudo systemctl status postgresql
```

### Issue: Google Calendar API quota exceeded
**Solution**: Implement request caching and increase quota in Google Cloud Console

### Issue: Alembic can't detect model changes
**Solution**: Ensure models are imported in `models/__init__.py`:
```python
from models.models import *
```

---

## Development Workflow

### Daily Development
1. Activate virtual environment
2. Start PostgreSQL and Redis
3. Run development server: `python app.py`
4. Make code changes (server auto-reloads)
5. Write tests
6. Run tests: `pytest`

### Before Committing
1. Run tests: `pytest`
2. Check code style: `flake8 .`
3. Format code: `black .`
4. Update requirements if needed: `pip freeze > requirements.txt`

### Deployment Checklist
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Monitoring set up

---

## Next Steps

1. **Frontend Setup**: See `frontend/README.md`
2. **API Documentation**: Visit `http://localhost:8000/api/docs`
3. **Module Documentation**: Read `docs/modules/`
4. **Contributing**: See `CONTRIBUTING.md` (to be created)

---

## Useful Commands

### Database
```bash
# Connect to database
psql -U study_planner_user -d study_planner

# Backup database
pg_dump study_planner > backup.sql

# Restore database
psql study_planner < backup.sql

# Drop all tables (WARNING: Destructive!)
python -c "from config.database import drop_db; drop_db()"
```

### Python
```bash
# Update all packages
pip list --outdated
pip install --upgrade package_name

# Generate requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt
```

### Docker (Optional)
```bash
# Build image
docker build -t study-planner-backend .

# Run container
docker run -p 8000:8000 study-planner-backend

# Docker Compose (all services)
docker-compose up -d
```

---

## Support & Resources

- **Documentation**: `docs/`
- **API Spec**: `docs/api/api_spec.md`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `SECRET_KEY` | JWT signing key | Yes | - |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes* | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | Yes* | - |
| `NOTION_CLIENT_ID` | Notion integration ID | No | - |
| `NOTION_CLIENT_SECRET` | Notion integration secret | No | - |
| `REDIS_URL` | Redis connection string | No | `redis://localhost:6379/0` |
| `FRONTEND_URL` | Frontend URL for CORS | No | `http://localhost:3000` |
| `DEBUG` | Enable debug mode | No | `False` |

*Required if enabling integrations

---

Happy Coding! 🚀
