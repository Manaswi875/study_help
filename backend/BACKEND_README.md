# Adaptive Study Planner - Backend

FastAPI-based backend for the Adaptive Study Planner system.

## Quick Start

### 1. Install Dependencies

Make sure you're in the virtual environment:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

Install PostgreSQL 13+ and create a database:

```sql
CREATE DATABASE study_planner;
CREATE USER study_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE study_planner TO study_user;
```

Update the `.env` file with your database credentials:

```env
DATABASE_URL=postgresql://study_user:your_password@localhost:5432/study_planner
```

### 3. Initialize Database

Run Alembic migrations to create database tables:

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Run the Application

Start the development server:

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/api/docs
- Alternative docs: http://localhost:8000/api/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info

### Courses
- `POST /api/courses` - Create course
- `GET /api/courses` - List all courses
- `GET /api/courses/{id}` - Get course details
- `PUT /api/courses/{id}` - Update course
- `DELETE /api/courses/{id}` - Delete course

### Topics
- `POST /api/courses/{id}/topics` - Create topic
- `GET /api/courses/{id}/topics` - List course topics
- `GET /api/courses/{id}/topics/{topic_id}` - Get topic details
- `PUT /api/courses/{id}/topics/{topic_id}` - Update topic
- `DELETE /api/courses/{id}/topics/{topic_id}` - Delete topic

### Mastery Tracking
- `POST /api/mastery/update` - Update mastery after quiz
- `GET /api/mastery/course/{id}` - Get course mastery overview
- `GET /api/mastery/topic/{id}` - Get topic mastery details
- `GET /api/mastery/overview` - Get overall mastery statistics

### Scheduling
- `POST /api/schedule/generate` - Generate new schedule
- `POST /api/schedule/replan` - Trigger schedule replanning
- `GET /api/schedule/upcoming` - Get upcoming tasks
- `GET /api/schedule/today` - Get today's tasks
- `PUT /api/schedule/task/{id}/status` - Update task status
- `DELETE /api/schedule/task/{id}` - Delete task

## Architecture

### Core Components

1. **Mastery Engine** (`services/mastery_engine.py`)
   - EWMA (Exponentially Weighted Moving Average) algorithm
   - SM-2 spaced repetition algorithm
   - Adaptive difficulty selection
   - Priority scoring

2. **Scheduling Engine** (`services/scheduler.py`)
   - Greedy scheduling algorithm
   - Constraint satisfaction
   - Automatic replanning on changes
   - Daily time limit enforcement

3. **Authentication** (`utils/auth.py`)
   - JWT token-based authentication
   - Bcrypt password hashing
   - OAuth2 flow

### Database Models

- **User** - User accounts and profiles
- **UserPreferences** - Study preferences and settings
- **Course** - Academic courses
- **Topic** - Course topics/chapters
- **Assessment** - Exams, quizzes, assignments
- **MasteryRecord** - Topic mastery tracking
- **PerformanceRecord** - Quiz/test performance history
- **StudyTask** - Generated study tasks
- **CalendarBlock** - External calendar events
- **IntegrationSettings** - Google Calendar/Notion settings

## Configuration

Key environment variables in `.env`:

```env
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/study_planner
SECRET_KEY=your-secret-key-change-in-production

# Optional
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
NOTION_CLIENT_ID=your-notion-client-id
NOTION_CLIENT_SECRET=your-notion-client-secret
```

## Development

### Database Migrations

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Testing

Run tests:

```bash
pytest tests/
```

### Code Style

Format code:

```bash
black .
isort .
```

Lint:

```bash
flake8 .
mypy .
```

## Deployment

### Production Setup

1. Set `ENVIRONMENT=production` in `.env`
2. Use a strong `SECRET_KEY`
3. Set up PostgreSQL with proper security
4. Use a reverse proxy (nginx/caddy)
5. Set up SSL certificates
6. Configure proper CORS origins

### Docker Deployment

```bash
docker-compose up -d
```

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

### Import Errors

- Activate virtual environment
- Install all dependencies: `pip install -r requirements.txt`

### Port Already in Use

Change the port in `.env` or use a different port:

```bash
uvicorn app:app --port 8001
```

## API Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

Include the access token in requests:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:8000/api/courses
```

## Next Steps

1. Set up Google Calendar integration
2. Set up Notion integration
3. Implement background tasks with Celery
4. Add email notifications
5. Create frontend application
