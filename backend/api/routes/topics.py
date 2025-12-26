"""
Topic management routes: CRUD operations for topics within courses
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from schemas.schemas import TopicCreate, TopicResponse
from models.models import User, Course, Topic
from utils.auth import get_current_user
from config.database import get_db

router = APIRouter(prefix="/courses/{course_id}/topics", tags=["Topics"])


@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    course_id: UUID,
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new topic for a course
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
    
    # Create the topic
    topic_dict = topic_data.model_dump()
    prerequisite_ids = topic_dict.pop('prerequisite_topic_ids', [])
    
    new_topic = Topic(
        course_id=course_id,
        **topic_dict
    )
    
    db.add(new_topic)
    db.flush()
    
    # Add prerequisites
    if prerequisite_ids:
        prerequisites = db.query(Topic).filter(
            Topic.id.in_(prerequisite_ids),
            Topic.course_id == course_id
        ).all()
        new_topic.prerequisite_topics = prerequisites
    
    db.commit()
    db.refresh(new_topic)
    
    return TopicResponse.model_validate(new_topic)


@router.get("", response_model=List[TopicResponse])
async def get_topics(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all topics for a course
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
    
    topics = db.query(Topic).filter(
        Topic.course_id == course_id
    ).order_by(Topic.order_index).all()
    
    return [TopicResponse.model_validate(topic) for topic in topics]


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    course_id: UUID,
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific topic
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
    
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.course_id == course_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    return TopicResponse.model_validate(topic)


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    course_id: UUID,
    topic_id: UUID,
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a topic
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
    
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.course_id == course_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Update fields
    topic_dict = topic_data.model_dump()
    prerequisite_ids = topic_dict.pop('prerequisite_topic_ids', [])
    
    for field, value in topic_dict.items():
        setattr(topic, field, value)
    
    # Update prerequisites
    if prerequisite_ids is not None:
        prerequisites = db.query(Topic).filter(
            Topic.id.in_(prerequisite_ids),
            Topic.course_id == course_id
        ).all()
        topic.prerequisite_topics = prerequisites
    
    db.commit()
    db.refresh(topic)
    
    return TopicResponse.model_validate(topic)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    course_id: UUID,
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a topic
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
    
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.course_id == course_id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    db.delete(topic)
    db.commit()
    
    return None
