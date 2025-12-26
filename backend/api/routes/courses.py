"""
Course management routes: CRUD operations for courses
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from schemas.schemas import CourseCreate, CourseResponse
from models.models import User, Course
from utils.auth import get_current_user
from config.database import get_db

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new course
    """
    new_course = Course(
        user_id=current_user.id,
        **course_data.model_dump()
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return CourseResponse.model_validate(new_course)


@router.get("", response_model=List[CourseResponse])
async def get_courses(
    include_archived: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all courses for current user
    """
    query = db.query(Course).filter(Course.user_id == current_user.id)
    
    if not include_archived:
        query = query.filter(Course.is_archived == False)
    
    courses = query.order_by(Course.created_at.desc()).all()
    
    return [CourseResponse.model_validate(course) for course in courses]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific course by ID
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return CourseResponse.model_validate(course)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a course
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    for field, value in course_data.model_dump().items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    
    return CourseResponse.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a course (soft delete - archives it)
    """
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    course.is_archived = True
    db.commit()
    
    return None
