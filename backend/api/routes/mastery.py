"""
Mastery tracking routes: update mastery scores and get mastery status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from schemas.schemas import MasteryUpdate, MasteryResponse
from models.models import User, Course, Topic, MasteryRecord, PerformanceRecord
from utils.auth import get_current_user
from config.database import get_db
from services.mastery_engine import MasteryEngine

router = APIRouter(prefix="/mastery", tags=["Mastery"])


@router.post("/update", response_model=MasteryResponse)
async def update_mastery(
    mastery_data: MasteryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update mastery score for a topic based on quiz performance
    """
    # Verify topic exists and belongs to user
    topic = db.query(Topic).join(Course).filter(
        Topic.id == mastery_data.topic_id,
        Course.user_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Get or create mastery record
    mastery_record = db.query(MasteryRecord).filter(
        MasteryRecord.user_id == current_user.id,
        MasteryRecord.topic_id == mastery_data.topic_id
    ).first()
    
    # Initialize mastery engine
    engine = MasteryEngine(db)
    
    if not mastery_record:
        # Initialize new mastery record
        mastery_record = engine.initialize_mastery(
            user_id=str(current_user.id),
            topic_id=str(mastery_data.topic_id),
            diagnostic_score=mastery_data.quiz_score,
            question_count=mastery_data.question_count
        )
        db.add(mastery_record)
        db.flush()
    else:
        # Update mastery using EWMA algorithm
        mastery_record = engine.update_mastery_ewma(
            mastery_record=mastery_record,
            quiz_score=mastery_data.quiz_score,
            difficulty_level=mastery_data.difficulty_level,
            time_spent_min=mastery_data.time_spent_min
        )
    
    updated_record = mastery_record
    
    # Create performance record
    performance_record = PerformanceRecord(
        user_id=current_user.id,
        course_id=topic.course_id,
        score=mastery_data.quiz_score,
        max_score=100.0,
        time_spent_min=mastery_data.time_spent_min,
        question_data=mastery_data.question_data,
        topic_breakdown={str(mastery_data.topic_id): mastery_data.quiz_score}
    )
    db.add(performance_record)
    db.commit()
    db.refresh(updated_record)
    
    return MasteryResponse(
        topic_id=updated_record.topic_id,
        topic_name=topic.name,
        course_id=topic.course_id,
        course_name=topic.course.name,
        mastery_score=updated_record.mastery_score,
        confidence_interval=updated_record.confidence_interval,
        trend=updated_record.trend.value,
        last_practiced=updated_record.last_practiced,
        next_review_date=updated_record.next_review_date,
        practice_count=updated_record.practice_count,
        quiz_count=updated_record.quiz_count
    )


@router.get("/course/{course_id}", response_model=List[MasteryResponse])
async def get_course_mastery(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mastery status for all topics in a course
    """
    # Verify course belongs to user
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get all topics with their mastery records
    topics = db.query(Topic).filter(Topic.course_id == course_id).all()
    
    results = []
    for topic in topics:
        mastery_record = db.query(MasteryRecord).filter(
            MasteryRecord.user_id == current_user.id,
            MasteryRecord.topic_id == topic.id
        ).first()
        
        if mastery_record:
            results.append(MasteryResponse(
                topic_id=topic.id,
                topic_name=topic.name,
                course_id=course_id,
                course_name=course.name,
                mastery_score=mastery_record.mastery_score,
                confidence_interval=mastery_record.confidence_interval,
                trend=mastery_record.trend.value,
                last_practiced=mastery_record.last_practiced,
                next_review_date=mastery_record.next_review_date,
                practice_count=mastery_record.practice_count,
                quiz_count=mastery_record.quiz_count
            ))
        else:
            # Topic not yet practiced
            results.append(MasteryResponse(
                topic_id=topic.id,
                topic_name=topic.name,
                course_id=course_id,
                course_name=course.name,
                mastery_score=0.0,
                confidence_interval=0.0,
                trend="stable",
                last_practiced=None,
                next_review_date=None,
                practice_count=0,
                quiz_count=0
            ))
    
    return results


@router.get("/topic/{topic_id}", response_model=MasteryResponse)
async def get_topic_mastery(
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mastery status for a specific topic
    """
    # Verify topic exists and belongs to user
    topic = db.query(Topic).join(Course).filter(
        Topic.id == topic_id,
        Course.user_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    mastery_record = db.query(MasteryRecord).filter(
        MasteryRecord.user_id == current_user.id,
        MasteryRecord.topic_id == topic_id
    ).first()
    
    if not mastery_record:
        return MasteryResponse(
            topic_id=topic_id,
            topic_name=topic.name,
            course_id=topic.course_id,
            course_name=topic.course.name,
            mastery_score=0.0,
            confidence_interval=0.0,
            trend="stable",
            last_practiced=None,
            next_review_date=None,
            practice_count=0,
            quiz_count=0
        )
    
    return MasteryResponse(
        topic_id=mastery_record.topic_id,
        topic_name=topic.name,
        course_id=topic.course_id,
        course_name=topic.course.name,
        mastery_score=mastery_record.mastery_score,
        confidence_interval=mastery_record.confidence_interval,
        trend=mastery_record.trend.value,
        last_practiced=mastery_record.last_practiced,
        next_review_date=mastery_record.next_review_date,
        practice_count=mastery_record.practice_count,
        quiz_count=mastery_record.quiz_count
    )


@router.get("/overview", response_model=dict)
async def get_mastery_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overall mastery statistics for the user
    """
    # Get all mastery records
    records = db.query(MasteryRecord).filter(
        MasteryRecord.user_id == current_user.id
    ).all()
    
    if not records:
        return {
            "total_topics": 0,
            "average_mastery": 0.0,
            "mastered_count": 0,
            "proficient_count": 0,
            "learning_count": 0,
            "needs_review": 0,
            "total_practice_sessions": 0
        }
    
    mastered = sum(1 for r in records if r.mastery_score >= 90)
    proficient = sum(1 for r in records if 70 <= r.mastery_score < 90)
    learning = sum(1 for r in records if 50 <= r.mastery_score < 70)
    needs_review = sum(1 for r in records if r.mastery_score < 50)
    
    return {
        "total_topics": len(records),
        "average_mastery": sum(r.mastery_score for r in records) / len(records),
        "mastered_count": mastered,
        "proficient_count": proficient,
        "learning_count": learning,
        "needs_review": needs_review,
        "total_practice_sessions": sum(r.practice_count for r in records)
    }
