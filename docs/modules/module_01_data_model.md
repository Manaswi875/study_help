# Module 1: Data Model & Ingestion Layer

**Owner**: Backend Team  
**Priority**: Critical (Foundation)  
**Dependencies**: None  
**Estimated Effort**: 2-3 weeks

---

## Overview

The Data Model & Ingestion Layer is the foundation of the Adaptive Study Planner. It defines all entities, relationships, and data ingestion mechanisms needed to capture user profiles, course content, assessments, performance records, and study tasks.

---

## Objectives

1. Design a normalized, scalable database schema for all system entities
2. Provide APIs for manual and programmatic data ingestion
3. Maintain topic-level mastery scores with confidence intervals
4. Store all constraints (time, deadlines, preferences)
5. Support versioning and historical data tracking

---

## Core Entities

### 1. User
**Purpose**: Represents a student using the platform

**Fields**:
```python
class User:
    id: UUID (PK)
    email: str (unique, indexed)
    password_hash: str
    full_name: str
    school_name: str
    academic_level: Enum['high_school', 'undergraduate', 'graduate', 'other']
    major: str (optional)
    timezone: str (IANA timezone)
    language: str (ISO 639-1 code)
    created_at: datetime
    updated_at: datetime
    last_login: datetime
    is_active: bool
    is_verified: bool
```

**Relationships**:
- 1:N with UserPreferences
- 1:N with Course
- 1:N with PerformanceRecord
- 1:N with StudyTask
- 1:1 with IntegrationSettings

---

### 2. UserPreferences
**Purpose**: Stores user's study preferences and constraints

**Fields**:
```python
class UserPreferences:
    id: UUID (PK)
    user_id: UUID (FK → User)
    
    # Time constraints
    max_hours_per_day: float (default: 4.0)
    preferred_block_length_min: int (default: 50)
    break_length_min: int (default: 10)
    earliest_start_time: time (default: 08:00)
    latest_end_time: time (default: 22:00)
    
    # Weekly availability (stored as JSON)
    # Format: {"monday": [{"start": "18:00", "end": "22:00"}], ...}
    weekly_availability: JSON
    
    # Difficulty preferences
    difficulty_curve: Enum['gentle', 'balanced', 'aggressive']
    
    # Study mode preferences per course (stored as JSON)
    # Format: {"course_id": ["reading", "problem_sets", "flashcards"], ...}
    study_mode_preferences: JSON
    
    # Spaced repetition settings
    enable_spaced_repetition: bool (default: True)
    min_review_interval_days: int (default: 1)
    
    created_at: datetime
    updated_at: datetime
```

---

### 3. Course
**Purpose**: Represents an academic course

**Fields**:
```python
class Course:
    id: UUID (PK)
    user_id: UUID (FK → User)
    name: str
    code: str (e.g., "MATH 2413")
    instructor_name: str (optional)
    credit_hours: float
    semester: str (e.g., "Fall 2025")
    start_date: date
    end_date: date
    description: text (optional)
    color: str (hex color for UI)
    is_archived: bool (default: False)
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- N:1 with User
- 1:N with Topic
- 1:N with Assessment
- 1:N with PerformanceRecord

---

### 4. Topic (Concept)
**Purpose**: Granular learning concept within a course

**Fields**:
```python
class Topic:
    id: UUID (PK)
    course_id: UUID (FK → Course)
    name: str (e.g., "Limits and Continuity")
    description: text (optional)
    estimated_difficulty: Enum['easy', 'medium', 'hard', 'exam_level']
    
    # Dependency graph (stored as JSON array of topic IDs)
    prerequisite_topic_ids: JSON (default: [])
    
    # Resources
    resource_links: JSON (array of {"type": "video|reading|exercise", "url": "..."})
    
    # Ordering
    order_index: int (for display ordering)
    
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- N:1 with Course
- N:N with Assessment (through AssessmentTopic join table)
- 1:N with MasteryRecord
- 1:N with StudyTask

---

### 5. Assessment
**Purpose**: Quiz, exam, assignment, or project

**Fields**:
```python
class Assessment:
    id: UUID (PK)
    course_id: UUID (FK → Course)
    name: str
    type: Enum['quiz', 'assignment', 'midterm', 'final', 'project']
    weight_percent: float (0-100)
    due_date: datetime
    estimated_duration_min: int
    max_score: float (default: 100)
    description: text (optional)
    is_completed: bool (default: False)
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- N:1 with Course
- N:N with Topic (through AssessmentTopic)
- 1:N with PerformanceRecord

---

### 6. AssessmentTopic (Join Table)
**Purpose**: Maps which topics are covered in each assessment

**Fields**:
```python
class AssessmentTopic:
    id: UUID (PK)
    assessment_id: UUID (FK → Assessment)
    topic_id: UUID (FK → Topic)
    question_count: int (optional, for analytics)
    weight_in_assessment: float (optional, 0-100)
```

---

### 7. PerformanceRecord
**Purpose**: Captures quiz/assignment attempts and scores

**Fields**:
```python
class PerformanceRecord:
    id: UUID (PK)
    user_id: UUID (FK → User)
    course_id: UUID (FK → Course)
    assessment_id: UUID (FK → Assessment, nullable for practice sessions)
    attempt_number: int (for retakes)
    
    # Performance data
    score: float (0-100 or raw score)
    max_score: float
    percentage: float (computed: score/max_score * 100)
    time_spent_min: int
    completed_at: datetime
    
    # Per-topic breakdown (stored as JSON)
    # Format: {"topic_id": {"correct": 5, "total": 8, "time_min": 12}, ...}
    topic_breakdown: JSON
    
    # Question-level data (stored as JSON for later analysis)
    # Format: [{"question_id": "q1", "correct": true, "time_sec": 45, "difficulty": "medium"}, ...]
    question_data: JSON (optional)
    
    created_at: datetime
```

**Relationships**:
- N:1 with User
- N:1 with Course
- N:1 with Assessment (nullable)

---

### 8. MasteryRecord
**Purpose**: Tracks mastery level for each topic over time

**Fields**:
```python
class MasteryRecord:
    id: UUID (PK)
    user_id: UUID (FK → User)
    topic_id: UUID (FK → Topic)
    
    # Mastery metrics
    mastery_score: float (0-100)
    confidence_interval: float (standard deviation or confidence range)
    trend: Enum['improving', 'stable', 'declining', 'new']
    
    # Spaced repetition data
    last_practiced_at: datetime (nullable)
    next_review_date: date (nullable)
    review_interval_days: int (default: 1)
    
    # Historical tracking
    practice_count: int (number of practice sessions)
    quiz_count: int (number of quizzes taken)
    
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- N:1 with User
- N:1 with Topic

**Unique Constraint**: (user_id, topic_id)

---

### 9. StudyTask
**Purpose**: Atomic unit of work to be scheduled

**Fields**:
```python
class StudyTask:
    id: UUID (PK)
    user_id: UUID (FK → User)
    course_id: UUID (FK → Course)
    
    # Task details
    title: str
    description: text
    task_type: Enum['reading', 'problem_set', 'quiz', 'review', 'project', 'flashcards']
    difficulty: Enum['easy', 'medium', 'hard', 'exam_level']
    
    # Topics covered (JSON array of topic IDs)
    topic_ids: JSON
    
    # Scheduling
    estimated_duration_min: int
    scheduled_start: datetime (nullable, set by scheduler)
    scheduled_end: datetime (nullable)
    actual_start: datetime (nullable)
    actual_end: datetime (nullable)
    
    # Status
    status: Enum['pending', 'scheduled', 'in_progress', 'completed', 'skipped']
    completion_percentage: float (0-100)
    
    # Priority (computed by scheduler)
    priority_score: float
    
    # Integration IDs
    calendar_event_id: str (nullable, Google Calendar event ID)
    notion_page_id: str (nullable, Notion database row ID)
    
    # Metadata
    expected_mastery_gain: float (0-100, estimated)
    actual_mastery_gain: float (0-100, measured after completion)
    
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- N:1 with User
- N:1 with Course

---

### 10. CalendarBlock
**Purpose**: Represents a scheduled time block in Google Calendar

**Fields**:
```python
class CalendarBlock:
    id: UUID (PK)
    user_id: UUID (FK → User)
    study_task_id: UUID (FK → StudyTask, nullable)
    
    # Calendar sync
    google_calendar_id: str (the calendar ID)
    google_event_id: str (the specific event ID)
    
    # Time block
    start_time: datetime
    end_time: datetime
    
    # Status
    is_synced: bool (True if successfully synced to Google Calendar)
    last_sync_at: datetime
    sync_error: text (nullable, error message if sync failed)
    
    # User modifications
    manually_modified: bool (True if user edited directly in Google Calendar)
    
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- N:1 with User
- 1:1 with StudyTask (nullable)

---

### 11. NotionTask
**Purpose**: Mirrors StudyTask in Notion database

**Fields**:
```python
class NotionTask:
    id: UUID (PK)
    user_id: UUID (FK → User)
    study_task_id: UUID (FK → StudyTask)
    
    # Notion sync
    notion_database_id: str
    notion_page_id: str (the specific page/row ID)
    
    # Sync status
    is_synced: bool
    last_sync_at: datetime
    sync_error: text (nullable)
    
    # Notion properties (stored as JSON for flexibility)
    # Format: {"Status": "In Progress", "Due Date": "2025-12-30", ...}
    notion_properties: JSON
    
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- N:1 with User
- 1:1 with StudyTask

---

### 12. IntegrationSettings
**Purpose**: Stores API tokens and integration configurations

**Fields**:
```python
class IntegrationSettings:
    id: UUID (PK)
    user_id: UUID (FK → User)
    
    # Google Calendar
    google_calendar_enabled: bool (default: False)
    google_access_token: str (encrypted)
    google_refresh_token: str (encrypted)
    google_token_expiry: datetime
    google_calendar_id: str (the dedicated study calendar ID)
    google_monitored_calendars: JSON (array of calendar IDs to check for conflicts)
    
    # Notion
    notion_enabled: bool (default: False)
    notion_access_token: str (encrypted)
    notion_database_id: str
    notion_two_way_sync: bool (default: False)
    
    # Sync settings
    auto_sync_interval_min: int (default: 15)
    last_sync_at: datetime
    
    created_at: datetime
    updated_at: datetime
```

**Relationships**:
- 1:1 with User

---

## Data Ingestion APIs

### Manual Data Entry
```python
# POST /api/courses
def create_course(user_id, name, code, semester, start_date, end_date, ...):
    """Manually add a course"""
    pass

# POST /api/courses/{course_id}/topics
def create_topic(course_id, name, description, difficulty, prerequisite_ids, ...):
    """Add a topic to a course"""
    pass

# POST /api/courses/{course_id}/assessments
def create_assessment(course_id, name, type, weight, due_date, topic_ids, ...):
    """Add an assessment with topic mapping"""
    pass

# POST /api/performance
def record_performance(user_id, assessment_id, score, time_spent, topic_breakdown, ...):
    """Record quiz/assignment results"""
    pass
```

### Programmatic Import
```python
# POST /api/import/csv
def import_courses_csv(user_id, csv_file):
    """
    Bulk import courses from CSV
    Format: name, code, semester, start_date, end_date, instructor
    """
    pass

# POST /api/import/lms
def import_from_lms(user_id, lms_type, credentials):
    """
    Future: Import from Canvas, Blackboard, Moodle
    """
    pass

# POST /api/import/grades
def import_grade_history(user_id, course_id, grade_data):
    """
    Import existing grade history
    Format: [{assessment_name, score, max_score, date, topics}, ...]
    """
    pass
```

---

## Mastery Score Calculation

### Initial Mastery (from Diagnostic)
```python
def initialize_mastery(user_id, topic_id, diagnostic_score):
    """
    Create initial MasteryRecord from diagnostic quiz
    
    Args:
        diagnostic_score: Percentage (0-100) from diagnostic quiz
    
    Returns:
        MasteryRecord with:
            mastery_score = diagnostic_score
            confidence_interval = high (e.g., 15) if few questions, low (e.g., 5) if many
            trend = 'new'
    """
    confidence = calculate_confidence(question_count)
    return MasteryRecord(
        user_id=user_id,
        topic_id=topic_id,
        mastery_score=diagnostic_score,
        confidence_interval=confidence,
        trend='new',
        last_practiced_at=datetime.now(),
        practice_count=1
    )
```

### Mastery Update (after Quiz)
```python
def update_mastery(user_id, topic_id, new_quiz_data):
    """
    Update mastery using Exponentially Weighted Moving Average (EWMA)
    
    Args:
        new_quiz_data: {
            'score_percent': float (0-100),
            'question_count': int,
            'time_spent_min': int,
            'difficulty_level': str
        }
    
    Returns:
        Updated MasteryRecord
    """
    record = get_mastery_record(user_id, topic_id)
    
    # EWMA calculation
    alpha = 0.3  # Learning rate for quizzes (0.5 for exams)
    new_score = new_quiz_data['score_percent']
    
    updated_mastery = alpha * new_score + (1 - alpha) * record.mastery_score
    
    # Update confidence (decreases with more data points)
    updated_confidence = max(5, record.confidence_interval * 0.9)
    
    # Determine trend
    if updated_mastery > record.mastery_score + 5:
        trend = 'improving'
    elif updated_mastery < record.mastery_score - 5:
        trend = 'declining'
    else:
        trend = 'stable'
    
    # Spaced repetition scheduling
    if updated_mastery >= 70:
        next_review = calculate_next_review_date(record.review_interval_days)
    else:
        next_review = datetime.now().date() + timedelta(days=1)
    
    record.mastery_score = updated_mastery
    record.confidence_interval = updated_confidence
    record.trend = trend
    record.last_practiced_at = datetime.now()
    record.next_review_date = next_review
    record.quiz_count += 1
    
    return record
```

---

## Constraints Storage

### Time Constraints
Stored in `UserPreferences.weekly_availability` as JSON:
```json
{
  "monday": [{"start": "18:00", "end": "22:00"}],
  "tuesday": [{"start": "18:00", "end": "22:00"}],
  "wednesday": [{"start": "18:00", "end": "22:00"}],
  "thursday": [{"start": "18:00", "end": "22:00"}],
  "friday": [{"start": "19:00", "end": "23:00"}],
  "saturday": [{"start": "09:00", "end": "21:00"}],
  "sunday": [{"start": "09:00", "end": "21:00"}]
}
```

### Deadline Constraints
Stored in `Assessment.due_date`  
Scheduler queries: `SELECT * FROM assessments WHERE due_date >= NOW() ORDER BY due_date`

### Calendar Constraints
Read from Google Calendar API in real-time  
Cached in memory for 15-minute intervals to reduce API calls

---

## Database Indexes

### Performance-Critical Indexes
```sql
-- User lookups
CREATE INDEX idx_user_email ON users(email);

-- Course queries
CREATE INDEX idx_course_user_id ON courses(user_id);
CREATE INDEX idx_course_active ON courses(user_id, is_archived);

-- Topic queries
CREATE INDEX idx_topic_course_id ON topics(course_id);

-- Assessment deadlines
CREATE INDEX idx_assessment_due_date ON assessments(course_id, due_date);

-- Performance records
CREATE INDEX idx_perf_user_course ON performance_records(user_id, course_id);
CREATE INDEX idx_perf_assessment ON performance_records(assessment_id);
CREATE INDEX idx_perf_completed ON performance_records(user_id, completed_at);

-- Mastery records
CREATE UNIQUE INDEX idx_mastery_user_topic ON mastery_records(user_id, topic_id);
CREATE INDEX idx_mastery_review ON mastery_records(user_id, next_review_date);

-- Study tasks
CREATE INDEX idx_task_user_status ON study_tasks(user_id, status);
CREATE INDEX idx_task_scheduled ON study_tasks(user_id, scheduled_start);
CREATE INDEX idx_task_priority ON study_tasks(user_id, priority_score DESC);

-- Calendar blocks
CREATE INDEX idx_calendar_user_time ON calendar_blocks(user_id, start_time);
CREATE INDEX idx_calendar_event ON calendar_blocks(google_event_id);
```

---

## Data Validation Rules

### User Input Validation
- Email: RFC 5322 compliant
- Timezone: Must be valid IANA timezone
- Max hours per day: 1-16 hours
- Block length: 15-180 minutes
- Break length: 5-60 minutes

### Course Validation
- Semester dates: end_date > start_date
- Assessment weights: Sum of all assessment weights per course must equal 100%

### Performance Validation
- Score: 0 ≤ score ≤ max_score
- Percentage: 0 ≤ percentage ≤ 100
- Time spent: > 0 minutes

### Mastery Validation
- Mastery score: 0-100
- Confidence interval: 0-50
- Review interval: 1-365 days

---

## Migration Strategy

### Phase 1: Core Tables
1. Users, UserPreferences
2. Courses, Topics
3. Assessments, AssessmentTopic

### Phase 2: Performance Tracking
4. PerformanceRecords
5. MasteryRecords

### Phase 3: Scheduling
6. StudyTasks
7. CalendarBlocks

### Phase 4: Integrations
8. IntegrationSettings
9. NotionTasks

---

## Testing Requirements

### Unit Tests
- Entity creation and validation
- Mastery calculation algorithms
- Constraint checking logic

### Integration Tests
- CSV import flow
- Multi-course setup
- Performance record → mastery update pipeline

### Performance Tests
- Query performance with 10k+ performance records
- Mastery calculation with 100+ topics
- Concurrent user writes

---

## Dependencies
- **Database**: PostgreSQL 13+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Validation**: Pydantic

---

## Success Criteria
✅ All entities defined with proper relationships  
✅ Manual data entry APIs functional  
✅ CSV import working for courses  
✅ Mastery calculation tested with sample data  
✅ Database queries performant (< 100ms)  
✅ Unit test coverage > 80%

---

**Status**: Ready for Implementation  
**Next Module**: Module 2 - Mastery & Difficulty Engine
