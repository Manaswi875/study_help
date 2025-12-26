"""
Schedule management routes: generate and manage study schedules
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date, timedelta

from schemas.schemas import (
    ScheduleGenerateRequest,
    ScheduleResponse,
    StudyTaskResponse,
    DailyBreakdown
)
from models.models import User, StudyTask, TaskStatus
from utils.auth import get_current_user
from config.database import get_db
from services.scheduler import generate_schedule, replan_schedule

router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.post("/generate", response_model=ScheduleResponse)
async def generate_new_schedule(
    request: ScheduleGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new adaptive study schedule
    """
    # Validate date range
    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Generate schedule
    result = generate_schedule(
        user_id=current_user.id,
        start_date=request.start_date,
        end_date=request.end_date,
        db=db
    )
    
    # Format response
    daily_breakdown = [
        DailyBreakdown(
            date=task_date,
            hours=stats['hours'],
            blocks=stats['blocks']
        )
        for task_date, stats in result['daily_breakdown'].items()
    ]
    
    return ScheduleResponse(
        schedule=[StudyTaskResponse.model_validate(t) for t in result['scheduled']],
        unscheduled_tasks=len(result['unscheduled']),
        total_hours=result['total_hours'],
        daily_breakdown=daily_breakdown
    )


@router.post("/replan")
async def replan_current_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger automatic schedule replanning
    """
    result = replan_schedule(
        user_id=current_user.id,
        trigger_event="manual_replan",
        db=db
    )
    
    # Format response
    daily_breakdown = [
        DailyBreakdown(
            date=task_date,
            hours=stats['hours'],
            blocks=stats['blocks']
        )
        for task_date, stats in result['daily_breakdown'].items()
    ]
    
    return ScheduleResponse(
        schedule=[StudyTaskResponse.model_validate(t) for t in result['scheduled']],
        unscheduled_tasks=len(result['unscheduled']),
        total_hours=result['total_hours'],
        daily_breakdown=daily_breakdown
    )


@router.get("/upcoming", response_model=List[StudyTaskResponse])
async def get_upcoming_tasks(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming scheduled tasks
    """
    from datetime import datetime, time
    
    today = date.today()
    end_date = today + timedelta(days=days)
    
    tasks = db.query(StudyTask).filter(
        StudyTask.user_id == current_user.id,
        StudyTask.scheduled_start >= datetime.combine(today, time.min),
        StudyTask.scheduled_start <= datetime.combine(end_date, time.max),
        StudyTask.status.in_([TaskStatus.SCHEDULED, TaskStatus.IN_PROGRESS])
    ).order_by(StudyTask.scheduled_start).all()
    
    return [StudyTaskResponse.model_validate(task) for task in tasks]


@router.get("/today", response_model=List[StudyTaskResponse])
async def get_todays_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's scheduled tasks
    """
    from datetime import datetime, time
    
    today = date.today()
    
    tasks = db.query(StudyTask).filter(
        StudyTask.user_id == current_user.id,
        StudyTask.scheduled_start >= datetime.combine(today, time.min),
        StudyTask.scheduled_start <= datetime.combine(today, time.max),
        StudyTask.status.in_([TaskStatus.SCHEDULED, TaskStatus.IN_PROGRESS])
    ).order_by(StudyTask.scheduled_start).all()
    
    return [StudyTaskResponse.model_validate(task) for task in tasks]


@router.put("/task/{task_id}/status")
async def update_task_status(
    task_id: UUID,
    status: TaskStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the status of a study task
    """
    task = db.query(StudyTask).filter(
        StudyTask.id == task_id,
        StudyTask.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = status
    
    if status == TaskStatus.COMPLETED:
        task.actual_duration_min = task.estimated_duration_min  # Can be updated with actual time
    
    db.commit()
    db.refresh(task)
    
    return StudyTaskResponse.model_validate(task)


@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a study task
    """
    task = db.query(StudyTask).filter(
        StudyTask.id == task_id,
        StudyTask.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return None
