"""
Pydantic schemas for request and response validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID
from models.models import AcademicLevel, DifficultyCurve, AssessmentType, Difficulty, TaskType, TaskStatus, Trend


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    school_name: Optional[str] = None
    academic_level: AcademicLevel
    major: Optional[str] = None
    timezone: str = "America/New_York"
    language: str = "en"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    full_name: str
    school_name: Optional[str]
    academic_level: str
    major: Optional[str]
    timezone: str
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# User Preferences schemas
class UserPreferencesUpdate(BaseModel):
    max_hours_per_day: Optional[float] = None
    preferred_block_length_min: Optional[int] = None
    break_length_min: Optional[int] = None
    earliest_start_time: Optional[time] = None
    latest_end_time: Optional[time] = None
    weekly_availability: Optional[dict] = None
    difficulty_curve: Optional[DifficultyCurve] = None
    study_mode_preferences: Optional[dict] = None
    enable_spaced_repetition: Optional[bool] = None


class UserPreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    max_hours_per_day: float
    preferred_block_length_min: int
    break_length_min: int
    earliest_start_time: time
    latest_end_time: time
    weekly_availability: dict
    difficulty_curve: str
    enable_spaced_repetition: bool


# Course schemas
class CourseCreate(BaseModel):
    name: str
    code: Optional[str] = None
    instructor_name: Optional[str] = None
    credit_hours: Optional[float] = None
    semester: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    color: str = "#3B82F6"


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    code: Optional[str]
    instructor_name: Optional[str]
    credit_hours: Optional[float]
    semester: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    color: str
    is_archived: bool


# Topic schemas
class TopicCreate(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_difficulty: Difficulty = Difficulty.MEDIUM
    prerequisite_topic_ids: List[UUID] = []
    resource_links: List[dict] = []
    order_index: int = 0


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    course_id: UUID
    name: str
    description: Optional[str]
    estimated_difficulty: str
    order_index: int


# Assessment schemas
class AssessmentCreate(BaseModel):
    name: str
    type: AssessmentType
    weight_percent: float = Field(ge=0, le=100)
    due_date: datetime
    estimated_duration_min: Optional[int] = None
    max_score: float = 100.0
    description: Optional[str] = None
    topic_ids: List[UUID] = []


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    course_id: UUID
    name: str
    type: str
    weight_percent: float
    due_date: datetime
    max_score: float
    is_completed: bool


# Mastery schemas
class MasteryUpdate(BaseModel):
    topic_id: UUID
    quiz_score: float = Field(ge=0, le=100)
    question_count: int = Field(ge=1)
    time_spent_min: Optional[int] = None
    difficulty_level: Difficulty = Difficulty.MEDIUM
    question_data: Optional[List[dict]] = None


class MasteryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    topic_id: UUID
    topic_name: str
    course_id: UUID
    course_name: str
    mastery_score: float
    confidence_interval: float
    trend: str
    last_practiced: Optional[datetime]
    next_review_date: Optional[date]
    practice_count: int
    quiz_count: int


# Performance Record schemas
class PerformanceRecordCreate(BaseModel):
    course_id: UUID
    assessment_id: Optional[UUID] = None
    score: float
    max_score: float
    time_spent_min: Optional[int] = None
    topic_breakdown: Optional[dict] = None
    question_data: Optional[List[dict]] = None


# Study Task schemas
class StudyTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    course_id: UUID
    title: str
    task_type: str
    difficulty: str
    estimated_duration_min: int
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    status: str
    priority_score: Optional[float]


# Schedule schemas
class ScheduleGenerateRequest(BaseModel):
    start_date: date
    end_date: date
    horizon_days: int = 7


class DailyBreakdown(BaseModel):
    date: date
    hours: float
    blocks: int


class ScheduleResponse(BaseModel):
    schedule: List[StudyTaskResponse]
    unscheduled_tasks: int
    total_hours: float
    daily_breakdown: List[DailyBreakdown]


# Integration schemas
class GoogleCalendarConnect(BaseModel):
    code: str


class NotionConnect(BaseModel):
    access_token: str
    database_id: Optional[str] = None
    two_way_sync: bool = False
