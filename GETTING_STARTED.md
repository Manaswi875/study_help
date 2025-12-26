# 🚀 Getting Started with Adaptive Study Planner

## Quick Start Guide

This guide will get you up and running in **5 minutes**!

---

## Prerequisites Checklist

✅ Python 3.9+ installed  
✅ Node.js 16+ installed  
✅ PostgreSQL 13+ installed and running  
✅ Git installed (if cloning)

---

## Step-by-Step Setup

### 1️⃣ Database Setup

#### Create Database

Open PostgreSQL (pgAdmin or psql) and run:

```sql
CREATE DATABASE study_planner;
CREATE USER study_planner_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE study_planner TO study_planner_user;
```

#### Update Backend Configuration

Edit `backend\.env`:

```env
DATABASE_URL=postgresql://study_planner_user:your_password@localhost:5432/study_planner
SECRET_KEY=your-secret-key-here
```

Generate a secure SECRET_KEY:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2️⃣ Backend Setup

Open terminal in project root:

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (if not done)
pip install -r requirements.txt

# Initialize database
alembic upgrade head

# Start backend server
python run.py
```

✅ Backend should now be running on **http://localhost:8000**  
✅ Check API docs at **http://localhost:8000/api/docs**

### 3️⃣ Frontend Setup

Open a **NEW terminal** in project root:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend should now be running on **http://localhost:3000**

---

## 4️⃣ First Time Use

### Create Your Account

1. Open browser to **http://localhost:3000**
2. Click **"Sign up"**
3. Fill in:
   - Full Name
   - Email
   - Academic Level
   - Password
4. Click **"Create account"**
5. You'll be automatically logged in!

### Add Your First Course

1. Click **"Courses"** in sidebar
2. Click **"Add Course"**
3. Fill in:
   - Course Name (e.g., "Calculus I")
   - Course Code (e.g., "MATH 101")
   - Semester (e.g., "Spring 2026")
   - Color (choose your favorite)
4. Click **"Create"**

### Add Topics to Course

1. Click on your new course
2. Click **"Add Topic"**
3. Fill in:
   - Topic Name (e.g., "Limits")
   - Difficulty (Easy/Medium/Hard)
   - Notes (optional)
4. Click **"Create"**
5. Add more topics!

### Take Your First Quiz

1. Click **"Quiz"** in sidebar
2. Select your course
3. Select a topic
4. Set number of questions (e.g., 10)
5. Set difficulty
6. Click **"Start Quiz"**
7. Enter your score (0-100)
8. Click **"Submit Quiz"**

✅ Your mastery for that topic is now calculated!

### Generate Your Study Schedule

1. Click **"Schedule"** in sidebar
2. Click **"Generate Schedule"**
3. Select date range (e.g., next 7 days)
4. Click **"Generate"**

✅ Your personalized study schedule is ready!

### Track Your Progress

1. Click **"Mastery"** in sidebar
2. View overall mastery percentage
3. See course-by-course breakdown
4. Check topic-level progress with charts

---

## 🎯 Daily Workflow

```
Morning:
1. Login to app
2. Check "Today's Schedule"
3. See prioritized tasks

During Study:
4. Work on scheduled tasks
5. Mark tasks as "In Progress"
6. Complete tasks

After Study:
7. Take quizzes on studied topics
8. System updates your mastery
9. Schedule auto-adjusts for tomorrow!
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Issue**: ModuleNotFoundError  
**Fix**: Activate virtual environment
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

**Issue**: Database connection error  
**Fix**: Check PostgreSQL is running and DATABASE_URL is correct

**Issue**: Port 8000 already in use  
**Fix**: Kill process or change port in `backend\.env`

### Frontend Won't Start

**Issue**: Module not found  
**Fix**: Install dependencies
```powershell
cd frontend
rm -rf node_modules
npm install
```

**Issue**: Port 3000 already in use  
**Fix**: 
```powershell
npm run dev -- -p 3001
```

**Issue**: API connection error  
**Fix**: Ensure backend is running on port 8000

### Can't Login

**Issue**: Invalid credentials  
**Fix**: Double-check email and password, or register new account

**Issue**: Token expired  
**Fix**: Login again (tokens expire after 30 minutes)

---

## 📱 Features Overview

### Dashboard
- See all your courses at a glance
- Today's tasks summary
- Overall mastery percentage
- Quick access to all features

### Courses
- Create unlimited courses
- Color-code for organization
- Track semester and details
- Archive old courses

### Topics
- Add topics to each course
- Set difficulty levels
- Track mastery per topic
- View progress trends

### Schedule
- AI-generated study schedule
- Priority-based task ordering
- Today and upcoming views
- Mark tasks as complete
- Automatic replanning

### Mastery
- Visual progress charts
- Course and topic breakdowns
- Trend indicators
- Detailed statistics

### Quiz
- Take quizzes on any topic
- Configurable difficulty
- Instant mastery updates
- Performance tracking

---

## 🎨 Tips & Tricks

### Best Practices

1. **Start Small**: Add 2-3 courses first
2. **Take Regular Quizzes**: Update mastery at least weekly
3. **Complete Tasks**: Mark tasks done for accurate replanning
4. **Check Daily**: Review your schedule each morning
5. **Track Progress**: Visit Mastery page to see improvement

### Color Coding

Use consistent colors for better organization:
- 🟦 Blue: Math courses
- 🟩 Green: Science courses
- 🟨 Yellow: Humanities
- 🟥 Red: Priority/difficult courses
- 🟪 Purple: Electives

### Mastery Levels

- **80-100%**: Mastered - Schedule reviews
- **60-79%**: Good - Continue regular study
- **40-59%**: Learning - Increase study time
- **0-39%**: Needs work - Focus here!

---

## 🚀 Advanced Features

### Replanning

Click "Replan" on Schedule page to:
- Update schedule based on completed tasks
- Re-prioritize remaining tasks
- Adjust for new quiz results

### Batch Operations

Quickly add multiple:
- Topics to a course
- Quizzes for multiple topics
- Schedule for multiple weeks

---

## 📊 Understanding Algorithms

### Mastery Calculation (EWMA)
Your mastery score is calculated using Exponentially Weighted Moving Average:
- Recent quiz scores have more impact
- Adjusted for question difficulty
- Confidence increases over time

### Spaced Repetition (SM-2)
Topics are scheduled for review based on:
- Your performance history
- Time since last study
- Optimal retention intervals

### Priority Scoring
Tasks are prioritized by:
- Urgency (40%): Deadline proximity
- Mastery (30%): Lower = higher priority
- Trend (20%): Declining = higher priority
- Prerequisites (10%): Foundation topics first

---

## 💡 Next Steps

Now that you're set up:

1. ✅ Add all your current courses
2. ✅ Break down courses into topics
3. ✅ Take initial quizzes (baseline mastery)
4. ✅ Generate your first schedule
5. ✅ Follow the schedule for a week
6. ✅ Take more quizzes to track progress
7. ✅ Watch your mastery improve!

---

## 🎓 Example Scenario

**Sarah - Undergraduate Student**

**Monday Morning:**
- Opens app, sees 3 tasks for today
- Task 1: Study "Limits" (60 min) - Priority 8.5
- Task 2: Review "Derivatives" (30 min) - Priority 6.2
- Task 3: Practice "Integrals" (45 min) - Priority 7.8

**During Day:**
- Completes Task 1, marks as done
- Takes quiz on Limits - scores 85%
- System updates mastery to 78% (was 65%)
- Schedule automatically adjusts

**End of Day:**
- Checks Mastery page
- Sees progress chart improving
- Tomorrow's schedule updated with easier review task

**After 2 Weeks:**
- Overall mastery increased from 55% to 72%
- Difficult topics now feel manageable
- Schedule perfectly matches her learning pace

---

## 🎉 You're Ready!

You now have a **complete, intelligent study planning system** at your fingertips!

**Remember:**
- 📚 Consistent quiz-taking = accurate mastery
- 📅 Follow your schedule = optimal learning
- 📈 Track progress = stay motivated

**Happy Learning!** 🚀✨

---

## 📞 Quick Reference

| What | Where | How |
|------|-------|-----|
| Backend API | http://localhost:8000 | `cd backend && python run.py` |
| Frontend UI | http://localhost:3000 | `cd frontend && npm run dev` |
| API Docs | http://localhost:8000/api/docs | Open in browser |
| Add Course | Courses page | Click "Add Course" |
| Take Quiz | Quiz page | Select course/topic |
| View Schedule | Schedule page | Click "Today" or "Upcoming" |
| Track Progress | Mastery page | See charts and stats |

---

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Last Updated**: December 2025
