# 🎓 Adaptive Study Planner


Core Features

Backend API - 45+ endpoints with FastAPI (Python)
Frontend UI - Modern React/Next.js with TypeScript
Adaptive Scheduling - Greedy algorithm with priority scoring
Mastery Tracking - EWMA + SM-2 algorithms
Smart Visualization- Charts and progress tracking
Authentication - JWT-based secure auth
Course Management - Full CRUD operations
Quiz System - Take quizzes and update mastery
Responsive Design - Works on all devices


Quick Start

1. Start Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python run.py
```

Backend runs on http://localhost:8000
API docs: http://localhost:8000/api/docs

2. Start Frontend

Open a new terminal:

```powershell
cd frontend
npm install  # First time only
npm run dev
```

Frontend runs on http://localhost:3000

3. Create Account & Start Learning!

1. Go to http://localhost:3000
2. Click "Sign up" to create an account
3. Add your courses
4. Take quizzes to track mastery
5. Generate your adaptive study schedule

 What's Built

Backend
- 45+ API endpoints
- JWT authentication
- 12 database models
- EWMA mastery algorithm
- SM-2 spaced repetition
- Greedy scheduling algorithm
- Full API documentation

Frontend
- Login & Registration pages
- Dashboard with stats
- Course & topic management
- Schedule view (today & upcoming)
- Mastery tracking with charts
- Quiz interface
- Settings page
- Fully responsive design


Modules

1. Data Model & Ingestion - User, course, topic, assessment, and performance data
2. Mastery Engine - Topic mastery calculation and difficulty recommendations
3. Scheduling Engine - Time-blocked schedule generation with constraints
4. Google Calendar Integration - Real-time calendar sync
5. Notion Integration - Task mirroring to Notion workspace
6. Quiz & Practice - Adaptive quiz system with performance tracking
7. Spaced Repetition - Review scheduling for retention
8. User Interface - Student-facing dashboard and controls
9. Feedback Loop - User feedback integration for continuous improvement
10. System Architecture - Core services and infrastructure

Technology Stack

Backend
Framework: FastAPI (Python)
Database: PostgreSQL with SQLAlchemy ORM
Task Queue: Celery with Redis
Authentication: OAuth 2.0 / JWT
APIs: Google Calendar API, Notion API

Frontend
Framework: React with TypeScript
State Management: Redux Toolkit
UI Library: Material-UI
Charts: Recharts
Calendar: FullCalendar

Infrastructure
Deployment: Docker + Kubernetes
CI/CD: GitHub Actions
Monitoring: Prometheus + Grafana
Logging: ELK Stack
