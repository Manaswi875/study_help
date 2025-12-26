"""
Scheduling engine: Adaptive task scheduling with constraint satisfaction
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date, time, timedelta
from typing import List, Tuple, Optional
from uuid import UUID
import heapq

from models.models import (
    User, StudyTask, MasteryRecord, CalendarBlock, 
    TaskType, TaskStatus, Difficulty
)
from services.mastery_engine import MasteryEngine


def get_available_time_blocks(
    user_id: UUID,
    start_date: date,
    end_date: date,
    db: Session
) -> List[Tuple[datetime, datetime]]:
    """
    Get available time blocks based on user preferences and calendar blocks
    """
    from models.models import User, UserPreferences
    
    user = db.query(User).filter(User.id == user_id).first()
    prefs = user.preferences
    
    # Get calendar blocks (busy times)
    calendar_blocks = db.query(CalendarBlock).filter(
        CalendarBlock.user_id == user_id,
        CalendarBlock.start_time >= datetime.combine(start_date, time.min),
        CalendarBlock.end_time <= datetime.combine(end_date, time.max)
    ).all()
    
    # Generate potential time blocks
    available_blocks = []
    current_date = start_date
    
    while current_date <= end_date:
        day_of_week = current_date.strftime("%A").lower()
        
        # Check if day is available in weekly_availability
        if not prefs.weekly_availability.get(day_of_week, True):
            current_date += timedelta(days=1)
            continue
        
        # Create time block for this day
        start_time = datetime.combine(current_date, prefs.earliest_start_time)
        end_time = datetime.combine(current_date, prefs.latest_end_time)
        
        # Split into blocks and exclude busy times
        block_length = timedelta(minutes=prefs.preferred_block_length_min)
        break_length = timedelta(minutes=prefs.break_length_min)
        
        current_block_start = start_time
        while current_block_start + block_length <= end_time:
            current_block_end = current_block_start + block_length
            
            # Check if block overlaps with calendar blocks
            is_busy = any(
                block.start_time < current_block_end and block.end_time > current_block_start
                for block in calendar_blocks
            )
            
            if not is_busy:
                available_blocks.append((current_block_start, current_block_end))
            
            current_block_start = current_block_end + break_length
        
        current_date += timedelta(days=1)
    
    return available_blocks


def create_study_tasks_from_topics(
    user_id: UUID,
    course_id: UUID,
    db: Session
) -> List[StudyTask]:
    """
    Create study tasks for topics that need practice
    """
    from models.models import Topic, Course
    
    # Get prioritized topics using mastery engine
    engine = MasteryEngine(db)
    prioritized_topics = engine.get_prioritized_topics(str(user_id), horizon_days=7)
    
    # Filter for this specific course
    course_topics = [t for t in prioritized_topics if str(t.get('course_id')) == str(course_id)]
    
    tasks = []
    for topic_data in course_topics:
        topic = db.query(Topic).filter(Topic.id == topic_data['topic_id']).first()
        if not topic:
            continue
        
        # Determine task difficulty based on mastery
        mastery_score = topic_data['mastery_score']
        if mastery_score < 40:
            difficulty = Difficulty.EASY
            duration = 30
        elif mastery_score < 70:
            difficulty = Difficulty.MEDIUM
            duration = 45
        else:
            difficulty = Difficulty.HARD
            duration = 60
        
        # Create practice task
        task = StudyTask(
            user_id=user_id,
            course_id=course_id,
            topic_id=topic.id,
            title=f"Practice: {topic.name}",
            task_type=TaskType.PRACTICE,
            difficulty=difficulty,
            estimated_duration_min=duration,
            priority_score=topic_data['priority_score'],
            status=TaskStatus.PENDING
        )
        tasks.append(task)
    
    return tasks


def schedule_tasks_greedy(
    tasks: List[StudyTask],
    available_blocks: List[Tuple[datetime, datetime]],
    max_hours_per_day: float
) -> Tuple[List[StudyTask], List[StudyTask]]:
    """
    Schedule tasks using greedy algorithm with constraint satisfaction
    """
    # Sort tasks by priority (descending)
    sorted_tasks = sorted(tasks, key=lambda t: t.priority_score or 0, reverse=True)
    
    scheduled = []
    unscheduled = []
    
    # Track daily usage
    daily_usage = {}  # date -> minutes used
    
    for task in sorted_tasks:
        task_duration = timedelta(minutes=task.estimated_duration_min)
        scheduled_this_task = False
        
        for block_start, block_end in available_blocks:
            block_date = block_start.date()
            block_duration = block_end - block_start
            
            # Check if task fits in this block
            if task_duration > block_duration:
                continue
            
            # Check daily limit
            daily_minutes = daily_usage.get(block_date, 0)
            max_daily_minutes = max_hours_per_day * 60
            
            if daily_minutes + task.estimated_duration_min > max_daily_minutes:
                continue
            
            # Schedule task
            task.scheduled_start = block_start
            task.scheduled_end = block_start + task_duration
            task.status = TaskStatus.SCHEDULED
            
            # Update daily usage
            daily_usage[block_date] = daily_minutes + task.estimated_duration_min
            
            # Remove used portion of block
            available_blocks.remove((block_start, block_end))
            
            # Add remaining time if any
            remaining_start = block_start + task_duration
            if remaining_start < block_end:
                available_blocks.append((remaining_start, block_end))
            
            scheduled.append(task)
            scheduled_this_task = True
            break
        
        if not scheduled_this_task:
            unscheduled.append(task)
    
    return scheduled, unscheduled


def generate_schedule(
    user_id: UUID,
    start_date: date,
    end_date: date,
    db: Session
) -> dict:
    """
    Generate adaptive study schedule for user
    """
    from models.models import User, Course
    
    user = db.query(User).filter(User.id == user_id).first()
    prefs = user.preferences
    
    # Get available time blocks
    available_blocks = get_available_time_blocks(user_id, start_date, end_date, db)
    
    # Get all active courses
    courses = db.query(Course).filter(
        Course.user_id == user_id,
        Course.is_archived == False
    ).all()
    
    # Generate tasks for all courses
    all_tasks = []
    for course in courses:
        tasks = create_study_tasks_from_topics(user_id, course.id, db)
        all_tasks.extend(tasks)
    
    # Check for upcoming assessments and create review tasks
    from models.models import Assessment
    upcoming_assessments = db.query(Assessment).join(Course).filter(
        Course.user_id == user_id,
        Assessment.due_date >= datetime.utcnow(),
        Assessment.due_date <= datetime.combine(end_date, time.max),
        Assessment.is_completed == False
    ).all()
    
    for assessment in upcoming_assessments:
        # Create review task
        days_until = (assessment.due_date.date() - start_date).days
        priority = 10.0 - (days_until / 7.0)  # Higher priority as due date approaches
        
        review_task = StudyTask(
            user_id=user_id,
            course_id=assessment.course_id,
            assessment_id=assessment.id,
            title=f"Review for {assessment.name}",
            task_type=TaskType.REVIEW,
            difficulty=Difficulty.MEDIUM,
            estimated_duration_min=assessment.estimated_duration_min or 60,
            priority_score=priority,
            status=TaskStatus.PENDING
        )
        all_tasks.append(review_task)
    
    # Schedule tasks
    scheduled, unscheduled = schedule_tasks_greedy(
        all_tasks,
        available_blocks,
        prefs.max_hours_per_day
    )
    
    # Save scheduled tasks to database
    for task in scheduled:
        db.add(task)
    
    db.commit()
    
    # Calculate statistics
    total_hours = sum(t.estimated_duration_min for t in scheduled) / 60.0
    
    # Daily breakdown
    daily_breakdown = {}
    for task in scheduled:
        task_date = task.scheduled_start.date()
        if task_date not in daily_breakdown:
            daily_breakdown[task_date] = {'hours': 0, 'blocks': 0}
        
        daily_breakdown[task_date]['hours'] += task.estimated_duration_min / 60.0
        daily_breakdown[task_date]['blocks'] += 1
    
    return {
        'scheduled': scheduled,
        'unscheduled': unscheduled,
        'total_hours': total_hours,
        'daily_breakdown': daily_breakdown
    }


def replan_schedule(
    user_id: UUID,
    trigger_event: str,
    db: Session
) -> dict:
    """
    Automatically replan schedule when changes occur
    """
    # Get today's date
    today = date.today()
    horizon_days = 7
    end_date = today + timedelta(days=horizon_days)
    
    # Delete pending/scheduled tasks in the planning horizon
    db.query(StudyTask).filter(
        StudyTask.user_id == user_id,
        StudyTask.scheduled_start >= datetime.combine(today, time.min),
        StudyTask.scheduled_start <= datetime.combine(end_date, time.max),
        StudyTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED])
    ).delete()
    
    db.commit()
    
    # Generate new schedule
    result = generate_schedule(user_id, today, end_date, db)
    
    return {
        'trigger': trigger_event,
        'replanned_at': datetime.utcnow(),
        **result
    }
