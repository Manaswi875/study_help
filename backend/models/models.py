"""
Database models for Adaptive Study Planner
Using SQLAlchemy ORM with PostgreSQL/SQLite compatibility
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Time, Text, JSON, ForeignKey, Enum as SQLEnum, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

# Custom UUID type that works with both SQLite and PostgreSQL
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

# Enums
class AcademicLevel(enum.Enum):
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    OTHER = "other"

class DifficultyCurve(enum.Enum):
    GENTLE = "gentle"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

class AssessmentType(enum.Enum):
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    MIDTERM = "midterm"
    FINAL = "final"
    PROJECT = "project"

class Difficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXAM_LEVEL = "exam_level"

class TaskType(enum.Enum):
    READING = "reading"
    PROBLEM_SET = "problem_set"
    QUIZ = "quiz"
    REVIEW = "review"
    PROJECT = "project"
    FLASHCARDS = "flashcards"

class TaskStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class Trend(enum.Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    NEW = "new"


# Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    school_name = Column(String(255))
    academic_level = Column(SQLEnum(AcademicLevel), nullable=False)
    major = Column(String(255))
    timezone = Column(String(50), nullable=False, default='America/New_York')
    language = Column(String(10), nullable=False, default='en')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    performance_records = relationship("PerformanceRecord", back_populates="user", cascade="all, delete-orphan")
    study_tasks = relationship("StudyTask", back_populates="user", cascade="all, delete-orphan")
    mastery_records = relationship("MasteryRecord", back_populates="user", cascade="all, delete-orphan")
    integration_settings = relationship("IntegrationSettings", back_populates="user", uselist=False)


class UserPreferences(Base):
    __tablename__ = 'user_preferences'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, unique=True)
    
    # Time constraints
    max_hours_per_day = Column(Float, default=4.0)
    preferred_block_length_min = Column(Integer, default=50)
    break_length_min = Column(Integer, default=10)
    earliest_start_time = Column(Time, default='08:00:00')
    latest_end_time = Column(Time, default='22:00:00')
    
    # Weekly availability (JSON)
    # Format: {"monday": [{"start": "18:00", "end": "22:00"}], ...}
    weekly_availability = Column(JSON, nullable=False, default={})
    
    # Difficulty preferences
    difficulty_curve = Column(SQLEnum(DifficultyCurve), default=DifficultyCurve.BALANCED)
    
    # Study mode preferences (JSON)
    # Format: {"course_id": ["reading", "problem_sets"], ...}
    study_mode_preferences = Column(JSON, default={})
    
    # Spaced repetition
    enable_spaced_repetition = Column(Boolean, default=True)
    min_review_interval_days = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50))
    instructor_name = Column(String(255))
    credit_hours = Column(Float)
    semester = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    description = Column(Text)
    color = Column(String(7), default='#3B82F6')  # Hex color
    is_archived = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="courses")
    topics = relationship("Topic", back_populates="course", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="course", cascade="all, delete-orphan")
    performance_records = relationship("PerformanceRecord", back_populates="course")
    study_tasks = relationship("StudyTask", back_populates="course")


class Topic(Base):
    __tablename__ = 'topics'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey('courses.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    estimated_difficulty = Column(SQLEnum(Difficulty), default=Difficulty.MEDIUM)
    
    # Dependency graph (JSON array of topic IDs)
    prerequisite_topic_ids = Column(JSON, default=[])
    
    # Resources (JSON array)
    # Format: [{"type": "video", "url": "..."}, ...]
    resource_links = Column(JSON, default=[])
    
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="topics")
    assessments = relationship("Assessment", secondary="assessment_topics", back_populates="topics")
    mastery_records = relationship("MasteryRecord", back_populates="topic", cascade="all, delete-orphan")


class Assessment(Base):
    __tablename__ = 'assessments'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey('courses.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(AssessmentType), nullable=False)
    weight_percent = Column(Float, nullable=False)  # 0-100
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    estimated_duration_min = Column(Integer)
    max_score = Column(Float, default=100.0)
    description = Column(Text)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="assessments")
    topics = relationship("Topic", secondary="assessment_topics", back_populates="assessments")
    performance_records = relationship("PerformanceRecord", back_populates="assessment")


class AssessmentTopic(Base):
    __tablename__ = 'assessment_topics'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(GUID(), ForeignKey('assessments.id'), nullable=False)
    topic_id = Column(GUID(), ForeignKey('topics.id'), nullable=False)
    question_count = Column(Integer)
    weight_in_assessment = Column(Float)  # 0-100


class PerformanceRecord(Base):
    __tablename__ = 'performance_records'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    course_id = Column(GUID(), ForeignKey('courses.id'), nullable=False, index=True)
    assessment_id = Column(GUID(), ForeignKey('assessments.id'), nullable=True, index=True)
    attempt_number = Column(Integer, default=1)
    
    # Performance data
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)  # Computed: score/max_score * 100
    time_spent_min = Column(Integer)
    completed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Per-topic breakdown (JSON)
    # Format: {"topic_id": {"correct": 5, "total": 8, "time_min": 12}, ...}
    topic_breakdown = Column(JSON)
    
    # Question-level data (JSON)
    # Format: [{"question_id": "q1", "correct": true, "time_sec": 45, "difficulty": "medium"}, ...]
    question_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="performance_records")
    course = relationship("Course", back_populates="performance_records")
    assessment = relationship("Assessment", back_populates="performance_records")


class MasteryRecord(Base):
    __tablename__ = 'mastery_records'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    topic_id = Column(GUID(), ForeignKey('topics.id'), nullable=False, index=True)
    
    # Mastery metrics
    mastery_score = Column(Float, nullable=False, default=0.0)  # 0-100
    confidence_interval = Column(Float, default=20.0)
    trend = Column(SQLEnum(Trend), default=Trend.NEW)
    
    # Spaced repetition
    last_practiced_at = Column(DateTime(timezone=True))
    next_review_date = Column(Date, index=True)
    review_interval_days = Column(Integer, default=1)
    easiness_factor = Column(Float, default=2.5)  # For SM-2 algorithm
    
    # Historical tracking
    practice_count = Column(Integer, default=0)
    quiz_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mastery_records")
    topic = relationship("Topic", back_populates="mastery_records")
    
    # Unique constraint
    __table_args__ = (
        {'extend_existing': True}
    )


class StudyTask(Base):
    __tablename__ = 'study_tasks'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    course_id = Column(GUID(), ForeignKey('courses.id'), nullable=False, index=True)
    
    # Task details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    task_type = Column(SQLEnum(TaskType), nullable=False)
    difficulty = Column(SQLEnum(Difficulty), nullable=False)
    
    # Topics covered (JSON array of topic IDs)
    topic_ids = Column(JSON, nullable=False)
    
    # Scheduling
    estimated_duration_min = Column(Integer, nullable=False)
    scheduled_start = Column(DateTime(timezone=True), index=True)
    scheduled_end = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    
    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    completion_percentage = Column(Float, default=0.0)
    
    # Priority
    priority_score = Column(Float, index=True)
    
    # Integration IDs
    calendar_event_id = Column(String(500))
    notion_page_id = Column(String(500))
    
    # Metadata
    expected_mastery_gain = Column(Float)
    actual_mastery_gain = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_tasks")
    course = relationship("Course", back_populates="study_tasks")
    calendar_block = relationship("CalendarBlock", back_populates="study_task", uselist=False)
    notion_task = relationship("NotionTask", back_populates="study_task", uselist=False)


class CalendarBlock(Base):
    __tablename__ = 'calendar_blocks'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    study_task_id = Column(GUID(), ForeignKey('study_tasks.id'), nullable=True)
    
    # Calendar sync
    google_calendar_id = Column(String(500), nullable=False)
    google_event_id = Column(String(500), nullable=False, index=True)
    
    # Time block
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    is_synced = Column(Boolean, default=False)
    last_sync_at = Column(DateTime(timezone=True))
    sync_error = Column(Text)
    
    # User modifications
    manually_modified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    study_task = relationship("StudyTask", back_populates="calendar_block")


class NotionTask(Base):
    __tablename__ = 'notion_tasks'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    study_task_id = Column(GUID(), ForeignKey('study_tasks.id'), nullable=False)
    
    # Notion sync
    notion_database_id = Column(String(500), nullable=False)
    notion_page_id = Column(String(500), nullable=False, index=True)
    
    # Sync status
    is_synced = Column(Boolean, default=False)
    last_sync_at = Column(DateTime(timezone=True))
    sync_error = Column(Text)
    
    # Notion properties (JSON)
    # Format: {"Status": "In Progress", "Due Date": "2025-12-30", ...}
    notion_properties = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    study_task = relationship("StudyTask", back_populates="notion_task")


class IntegrationSettings(Base):
    __tablename__ = 'integration_settings'
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, unique=True)
    
    # Google Calendar
    google_calendar_enabled = Column(Boolean, default=False)
    google_access_token = Column(Text)  # Should be encrypted
    google_refresh_token = Column(Text)  # Should be encrypted
    google_token_expiry = Column(DateTime(timezone=True))
    google_calendar_id = Column(String(500))
    google_monitored_calendars = Column(JSON, default=[])  # Array of calendar IDs
    
    # Notion
    notion_enabled = Column(Boolean, default=False)
    notion_access_token = Column(Text)  # Should be encrypted
    notion_database_id = Column(String(500))
    notion_two_way_sync = Column(Boolean, default=False)
    
    # Sync settings
    auto_sync_interval_min = Column(Integer, default=15)
    last_sync_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integration_settings")


# Create indexes
from sqlalchemy import Index

Index('idx_course_user_active', Course.user_id, Course.is_archived)
Index('idx_perf_user_course', PerformanceRecord.user_id, PerformanceRecord.course_id)
Index('idx_mastery_user_topic', MasteryRecord.user_id, MasteryRecord.topic_id, unique=True)
Index('idx_mastery_review', MasteryRecord.user_id, MasteryRecord.next_review_date)
Index('idx_task_user_status', StudyTask.user_id, StudyTask.status)
Index('idx_task_scheduled', StudyTask.user_id, StudyTask.scheduled_start)
Index('idx_task_priority', StudyTask.user_id, StudyTask.priority_score)
Index('idx_calendar_user_time', CalendarBlock.user_id, CalendarBlock.start_time)

