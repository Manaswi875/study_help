# API Specification - Adaptive Study Planner

**Version**: 1.0  
**Base URL**: `https://api.studyplanner.com/api` (development: `http://localhost:8000/api`)  
**Authentication**: JWT Bearer Token

---

## Authentication Endpoints

### POST /auth/register
**Description**: Register a new user

**Request Body**:
```json
{
  "email": "student@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "school_name": "University of Example",
  "academic_level": "undergraduate",
  "major": "Computer Science",
  "timezone": "America/New_York"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "email": "student@example.com",
  "full_name": "John Doe",
  "created_at": "2025-12-25T10:00:00Z"
}
```

---

### POST /auth/login
**Description**: Authenticate user and get access token

**Request Body**:
```json
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "full_name": "John Doe"
  }
}
```

---

## User Endpoints

### GET /users/me
**Description**: Get current user profile  
**Auth**: Required

**Response** (200):
```json
{
  "id": "uuid",
  "email": "student@example.com",
  "full_name": "John Doe",
  "school_name": "University of Example",
  "academic_level": "undergraduate",
  "major": "Computer Science",
  "timezone": "America/New_York",
  "created_at": "2025-12-25T10:00:00Z"
}
```

---

### GET /users/me/preferences
**Description**: Get user preferences  
**Auth**: Required

**Response** (200):
```json
{
  "max_hours_per_day": 4.0,
  "preferred_block_length_min": 50,
  "break_length_min": 10,
  "earliest_start_time": "08:00:00",
  "latest_end_time": "22:00:00",
  "weekly_availability": {
    "monday": [{"start": "18:00", "end": "22:00"}],
    "tuesday": [{"start": "18:00", "end": "22:00"}]
  },
  "difficulty_curve": "balanced",
  "enable_spaced_repetition": true
}
```

---

### PUT /users/me/preferences
**Description**: Update user preferences  
**Auth**: Required

**Request Body**: Same as GET response

**Response** (200): Updated preferences

---

## Course Endpoints

### GET /courses
**Description**: List all user's courses  
**Auth**: Required

**Query Parameters**:
- `include_archived` (bool): Include archived courses (default: false)

**Response** (200):
```json
[
  {
    "id": "uuid",
    "name": "Calculus II",
    "code": "MATH 2413",
    "instructor_name": "Dr. Smith",
    "credit_hours": 3.0,
    "semester": "Fall 2025",
    "start_date": "2025-08-25",
    "end_date": "2025-12-15",
    "color": "#3B82F6",
    "is_archived": false
  }
]
```

---

### POST /courses
**Description**: Create a new course  
**Auth**: Required

**Request Body**:
```json
{
  "name": "Calculus II",
  "code": "MATH 2413",
  "instructor_name": "Dr. Smith",
  "credit_hours": 3.0,
  "semester": "Fall 2025",
  "start_date": "2025-08-25",
  "end_date": "2025-12-15",
  "description": "Advanced calculus topics",
  "color": "#3B82F6"
}
```

**Response** (201): Created course object

---

### GET /courses/{course_id}
**Description**: Get course details  
**Auth**: Required

**Response** (200):
```json
{
  "id": "uuid",
  "name": "Calculus II",
  "code": "MATH 2413",
  "topics": [
    {
      "id": "uuid",
      "name": "Limits and Continuity",
      "estimated_difficulty": "medium"
    }
  ],
  "assessments": [
    {
      "id": "uuid",
      "name": "Midterm Exam",
      "type": "midterm",
      "weight_percent": 30.0,
      "due_date": "2025-10-15T10:00:00Z"
    }
  ]
}
```

---

### POST /courses/{course_id}/topics
**Description**: Add topic to course  
**Auth**: Required

**Request Body**:
```json
{
  "name": "Integration by Parts",
  "description": "Technique for integrating products of functions",
  "estimated_difficulty": "hard",
  "prerequisite_topic_ids": ["uuid1", "uuid2"],
  "resource_links": [
    {"type": "video", "url": "https://youtube.com/..."},
    {"type": "reading", "url": "https://textbook.com/..."}
  ]
}
```

**Response** (201): Created topic object

---

### POST /courses/{course_id}/assessments
**Description**: Add assessment to course  
**Auth**: Required

**Request Body**:
```json
{
  "name": "Final Exam",
  "type": "final",
  "weight_percent": 40.0,
  "due_date": "2025-12-15T14:00:00Z",
  "estimated_duration_min": 180,
  "max_score": 100.0,
  "topic_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response** (201): Created assessment object

---

## Mastery Endpoints

### GET /mastery/topics
**Description**: Get mastery scores for all topics  
**Auth**: Required

**Query Parameters**:
- `course_id` (uuid): Filter by course

**Response** (200):
```json
[
  {
    "topic_id": "uuid",
    "topic_name": "Limits and Continuity",
    "course_id": "uuid",
    "course_name": "Calculus II",
    "mastery_score": 68.5,
    "confidence_interval": 8.2,
    "trend": "improving",
    "last_practiced": "2025-12-20T14:30:00Z",
    "next_review_date": "2025-12-27",
    "practice_count": 12,
    "quiz_count": 4
  }
]
```

---

### GET /mastery/topics/{topic_id}/history
**Description**: Get mastery history for a topic  
**Auth**: Required

**Response** (200):
```json
{
  "topic_id": "uuid",
  "current_mastery": 68.5,
  "confidence_interval": 8.2,
  "trend": "improving",
  "history": [
    {
      "date": "2025-12-01",
      "mastery": 45.0,
      "quiz_score": 45.0,
      "event": "diagnostic"
    },
    {
      "date": "2025-12-20",
      "mastery": 68.5,
      "quiz_score": 75.0,
      "event": "practice_quiz"
    }
  ]
}
```

---

### POST /mastery/update
**Description**: Update mastery after completing quiz/practice  
**Auth**: Required

**Request Body**:
```json
{
  "topic_id": "uuid",
  "quiz_score": 80.0,
  "question_count": 10,
  "time_spent_min": 25,
  "difficulty_level": "medium",
  "question_data": [
    {"question_id": "q1", "correct": true, "time_sec": 45}
  ]
}
```

**Response** (200):
```json
{
  "old_mastery": 68.5,
  "new_mastery": 72.0,
  "confidence_interval": 7.5,
  "trend": "improving",
  "next_review_date": "2025-12-30",
  "message": "Mastery increased by 3.5 points!"
}
```

---

### GET /mastery/priority
**Description**: Get prioritized topics to study  
**Auth**: Required

**Query Parameters**:
- `horizon_days` (int): Planning horizon (default: 7)
- `max_tasks` (int): Max tasks to return (default: 14)

**Response** (200):
```json
[
  {
    "topic_id": "uuid",
    "topic_name": "Integration by Parts",
    "course_name": "Calculus II",
    "priority_score": 0.127,
    "mastery": 55.0,
    "trend": "stable",
    "recommended_difficulty": "medium",
    "estimated_duration_min": 50,
    "reason": "30% of final exam, 45% mastery gap, 6 days until exam"
  }
]
```

---

## Scheduling Endpoints

### POST /schedule/generate
**Description**: Generate study schedule  
**Auth**: Required

**Request Body**:
```json
{
  "start_date": "2025-12-26",
  "end_date": "2026-01-02",
  "horizon_days": 7
}
```

**Response** (200):
```json
{
  "schedule": [
    {
      "task_id": "uuid",
      "title": "Calculus - Integration by Parts",
      "course_name": "Calculus II",
      "start_time": "2025-12-26T18:00:00Z",
      "end_time": "2025-12-26T18:50:00Z",
      "duration_min": 50,
      "difficulty": "medium",
      "status": "scheduled",
      "calendar_event_id": "google_event_id"
    }
  ],
  "unscheduled_tasks": 3,
  "total_hours": 18.5,
  "daily_breakdown": [
    {"date": "2025-12-26", "hours": 2.5, "blocks": 3},
    {"date": "2025-12-27", "hours": 3.0, "blocks": 3}
  ]
}
```

---

### POST /schedule/replan
**Description**: Trigger immediate replanning  
**Auth**: Required

**Request Body**:
```json
{
  "reason": "calendar_change"
}
```

**Response** (200): New schedule

---

### GET /schedule/today
**Description**: Get today's schedule  
**Auth**: Required

**Response** (200):
```json
{
  "date": "2025-12-26",
  "tasks": [
    {
      "task_id": "uuid",
      "title": "Calculus - Limits Practice",
      "start_time": "2025-12-26T18:00:00Z",
      "end_time": "2025-12-26T18:50:00Z",
      "status": "scheduled",
      "course_color": "#3B82F6"
    }
  ],
  "total_hours": 2.5,
  "completed_hours": 0.0
}
```

---

### PUT /schedule/tasks/{task_id}
**Description**: Update a scheduled task  
**Auth**: Required

**Request Body**:
```json
{
  "status": "completed",
  "actual_start": "2025-12-26T18:05:00Z",
  "actual_end": "2025-12-26T18:55:00Z",
  "completion_percentage": 100.0
}
```

**Response** (200): Updated task

---

### DELETE /schedule/tasks/{task_id}
**Description**: Delete/skip a scheduled task  
**Auth**: Required

**Response** (204): No content

---

## Integration Endpoints

### GET /integrations/google/auth-url
**Description**: Get Google Calendar OAuth URL  
**Auth**: Required

**Response** (200):
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

---

### POST /integrations/google/callback
**Description**: Handle Google OAuth callback  
**Auth**: Required

**Request Body**:
```json
{
  "code": "authorization_code_from_google"
}
```

**Response** (200):
```json
{
  "success": true,
  "calendar_id": "primary",
  "message": "Google Calendar connected successfully"
}
```

---

### POST /integrations/google/sync
**Description**: Manually trigger Google Calendar sync  
**Auth**: Required

**Response** (200):
```json
{
  "synced_events": 15,
  "conflicts_resolved": 2,
  "last_sync": "2025-12-26T10:30:00Z"
}
```

---

### GET /integrations/notion/databases
**Description**: List Notion databases  
**Auth**: Required

**Response** (200):
```json
[
  {
    "id": "notion_db_id",
    "title": "Study Tasks",
    "url": "https://notion.so/..."
  }
]
```

---

### POST /integrations/notion/setup
**Description**: Set up Notion integration  
**Auth**: Required

**Request Body**:
```json
{
  "access_token": "notion_access_token",
  "database_id": "notion_db_id",
  "two_way_sync": true
}
```

**Response** (200):
```json
{
  "success": true,
  "database_id": "notion_db_id",
  "message": "Notion integration configured"
}
```

---

### POST /integrations/notion/sync
**Description**: Manually trigger Notion sync  
**Auth**: Required

**Response** (200):
```json
{
  "synced_tasks": 20,
  "created": 5,
  "updated": 15,
  "last_sync": "2025-12-26T10:30:00Z"
}
```

---

## Performance & Analytics Endpoints

### POST /performance/record
**Description**: Record quiz or assessment performance  
**Auth**: Required

**Request Body**:
```json
{
  "course_id": "uuid",
  "assessment_id": "uuid",
  "score": 85.0,
  "max_score": 100.0,
  "time_spent_min": 60,
  "topic_breakdown": {
    "topic_uuid_1": {"correct": 8, "total": 10, "time_min": 30},
    "topic_uuid_2": {"correct": 9, "total": 10, "time_min": 30}
  }
}
```

**Response** (201): Created performance record

---

### GET /analytics/dashboard
**Description**: Get analytics dashboard data  
**Auth**: Required

**Response** (200):
```json
{
  "total_study_hours": 45.5,
  "weekly_hours": 12.5,
  "consistency_score": 85.0,
  "course_breakdown": [
    {"course": "Calculus II", "hours": 20.5, "percentage": 45.0}
  ],
  "mastery_progression": [
    {"date": "2025-12-01", "avg_mastery": 55.0},
    {"date": "2025-12-26", "avg_mastery": 68.5}
  ],
  "upcoming_assessments": [
    {
      "name": "Final Exam",
      "course": "Calculus II",
      "date": "2025-12-30",
      "readiness_score": 75.0
    }
  ]
}
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request**:
```json
{
  "error": "validation_error",
  "message": "Invalid email format",
  "details": {"field": "email", "issue": "format"}
}
```

**401 Unauthorized**:
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

**404 Not Found**:
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

- Standard endpoints: 100 requests/minute
- Heavy endpoints (schedule generation): 10 requests/minute
- Integration endpoints: 30 requests/minute

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## Pagination

List endpoints support pagination:

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)

**Response**:
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```

---

## Webhooks (Future)

Future support for webhooks to notify external systems:

- `schedule.updated`: When schedule is regenerated
- `task.completed`: When a task is marked complete
- `mastery.changed`: When mastery increases significantly
