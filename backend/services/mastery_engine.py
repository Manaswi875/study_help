"""
Mastery Engine Service
Implements mastery calculation and difficulty selection algorithms
"""

from typing import List, Dict, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from models.models import MasteryRecord, Topic, Assessment, PerformanceRecord, Trend, Difficulty
import math


class MasteryEngine:
    """Core mastery calculation and recommendation engine"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_mastery(
        self,
        user_id: str,
        topic_id: str,
        diagnostic_score: float,
        question_count: int = 10
    ) -> MasteryRecord:
        """
        Create initial mastery record from diagnostic quiz
        
        Args:
            user_id: User identifier
            topic_id: Topic identifier
            diagnostic_score: Percentage score (0-100)
            question_count: Number of questions in diagnostic
        
        Returns:
            New MasteryRecord
        """
        confidence = self.calculate_confidence_interval(question_count)
        
        mastery = MasteryRecord(
            user_id=user_id,
            topic_id=topic_id,
            mastery_score=diagnostic_score,
            confidence_interval=confidence,
            trend=Trend.NEW,
            last_practiced_at=datetime.now(),
            next_review_date=date.today() + timedelta(days=1),
            practice_count=1,
            quiz_count=0
        )
        
        self.db.add(mastery)
        self.db.commit()
        self.db.refresh(mastery)
        
        return mastery
    
    def update_mastery_ewma(
        self,
        user_id: str,
        topic_id: str,
        quiz_score: float,
        question_count: int,
        alpha: float = 0.3
    ) -> MasteryRecord:
        """
        Update mastery using Exponentially Weighted Moving Average
        
        Args:
            user_id, topic_id: Identifiers
            quiz_score: Recent quiz score (0-100)
            question_count: Number of questions
            alpha: Learning rate (0-1)
        
        Returns:
            Updated MasteryRecord
        """
        # Get existing record or create new one
        mastery = self.db.query(MasteryRecord).filter(
            MasteryRecord.user_id == user_id,
            MasteryRecord.topic_id == topic_id
        ).first()
        
        if not mastery:
            return self.initialize_mastery(user_id, topic_id, quiz_score, question_count)
        
        # EWMA update
        old_mastery = mastery.mastery_score
        new_mastery = alpha * quiz_score + (1 - alpha) * old_mastery
        
        # Update confidence (decreases with more data)
        mastery.confidence_interval = max(5.0, mastery.confidence_interval * 0.9)
        
        # Detect trend
        mastery.trend = self.detect_trend(old_mastery, new_mastery)
        
        # Update spaced repetition schedule
        if new_mastery >= 70:
            quality = int((quiz_score / 100.0) * 5)
            interval, ef = self.calculate_next_review(
                mastery.easiness_factor,
                mastery.review_interval_days,
                quality
            )
            mastery.review_interval_days = interval
            mastery.next_review_date = date.today() + timedelta(days=interval)
            mastery.easiness_factor = ef
        else:
            mastery.review_interval_days = 1
            mastery.next_review_date = date.today() + timedelta(days=1)
        
        # Update metrics
        mastery.mastery_score = new_mastery
        mastery.last_practiced_at = datetime.now()
        mastery.quiz_count += 1
        
        self.db.commit()
        self.db.refresh(mastery)
        
        return mastery
    
    def calculate_confidence_interval(self, attempt_count: int) -> float:
        """
        Calculate confidence interval for mastery estimate
        
        Args:
            attempt_count: Number of quiz attempts
        
        Returns:
            Confidence interval (lower is more confident)
        """
        return max(5.0, 20.0 / math.sqrt(attempt_count))
    
    def detect_trend(self, old_mastery: float, new_mastery: float, threshold: float = 5.0) -> Trend:
        """
        Detect mastery trend
        
        Args:
            old_mastery: Previous mastery score
            new_mastery: Current mastery score
            threshold: Minimum change to consider a trend
        
        Returns:
            Trend enum value
        """
        delta = new_mastery - old_mastery
        
        if delta > threshold:
            return Trend.IMPROVING
        elif delta < -threshold:
            return Trend.DECLINING
        else:
            return Trend.STABLE
    
    def calculate_next_review(
        self,
        easiness_factor: float,
        current_interval: int,
        quality: int
    ) -> Tuple[int, float]:
        """
        Calculate next review interval using SM-2 algorithm
        
        Args:
            easiness_factor: Current EF (1.3-2.5)
            current_interval: Current interval in days
            quality: Quality of recall (0-5)
        
        Returns:
            (next_interval_days, updated_easiness_factor)
        """
        # Update easiness factor
        new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(1.3, new_ef)
        
        # Calculate next interval
        if quality < 3:
            next_interval = 1
        else:
            if current_interval == 0:
                next_interval = 1
            elif current_interval == 1:
                next_interval = 6
            else:
                next_interval = int(current_interval * new_ef)
        
        return next_interval, new_ef
    
    def select_difficulty_by_mastery(self, mastery: float) -> Difficulty:
        """
        Select difficulty based on mastery score
        
        Args:
            mastery: Current mastery score (0-100)
        
        Returns:
            Recommended difficulty level
        """
        if mastery < 40:
            return Difficulty.EASY
        elif mastery < 60:
            return Difficulty.MEDIUM
        elif mastery < 80:
            return Difficulty.HARD
        else:
            return Difficulty.EXAM_LEVEL
    
    def select_difficulty_adaptive(
        self,
        mastery: float,
        trend: Trend,
        days_until_exam: int,
        difficulty_curve: str
    ) -> Difficulty:
        """
        Adaptive difficulty selection considering multiple factors
        
        Args:
            mastery: Current mastery score
            trend: Trend enum
            days_until_exam: Days until exam
            difficulty_curve: User preference
        
        Returns:
            Recommended difficulty
        """
        base_diff = self.select_difficulty_by_mastery(mastery)
        diff_order = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD, Difficulty.EXAM_LEVEL]
        
        # Adjust based on trend
        if trend == Trend.DECLINING:
            idx = diff_order.index(base_diff)
            base_diff = diff_order[max(0, idx - 1)]
        elif trend == Trend.IMPROVING and difficulty_curve == 'aggressive':
            idx = diff_order.index(base_diff)
            base_diff = diff_order[min(3, idx + 1)]
        
        # Adjust based on exam proximity
        if days_until_exam <= 7 and mastery >= 60:
            return Difficulty.EXAM_LEVEL
        elif days_until_exam <= 3 and mastery < 60:
            return Difficulty.MEDIUM
        
        return base_diff
    
    def calculate_priority(
        self,
        assessment_weight: float,
        mastery_score: float,
        confidence_interval: float,
        exam_date: date,
        last_practiced: date
    ) -> float:
        """
        Calculate priority score for a topic
        
        Returns:
            Priority score (higher = more urgent)
        """
        weight = assessment_weight / 100.0
        gap = 1.0 - (mastery_score / 100.0)
        
        days_until_exam = max(1, (exam_date - date.today()).days)
        urgency = 1.0 / days_until_exam
        
        confidence_factor = 1.0 / (1.0 + confidence_interval / 100.0)
        
        days_since_practice = (date.today() - last_practiced).days if last_practiced else 30
        recency_factor = 1.0 / (1.0 + days_since_practice)
        
        priority = (weight * gap * urgency * confidence_factor) / recency_factor
        
        return priority
    
    def get_prioritized_topics(self, user_id: str, horizon_days: int = 7) -> List[Dict]:
        """
        Get prioritized list of topics to study
        
        Args:
            user_id: User identifier
            horizon_days: Planning horizon
        
        Returns:
            List of prioritized topics with recommendations
        """
        # Fetch all mastery records for user
        mastery_records = self.db.query(MasteryRecord).filter(
            MasteryRecord.user_id == user_id
        ).all()
        
        prioritized = []
        
        for record in mastery_records:
            # Get topic and associated assessments
            topic = self.db.query(Topic).filter(Topic.id == record.topic_id).first()
            if not topic:
                continue
            
            # Find next upcoming assessment covering this topic
            upcoming_assessments = self.db.query(Assessment).join(
                Assessment.topics
            ).filter(
                Topic.id == record.topic_id,
                Assessment.due_date >= datetime.now()
            ).order_by(Assessment.due_date).all()
            
            if not upcoming_assessments:
                continue
            
            next_assessment = upcoming_assessments[0]
            
            # Calculate priority
            priority = self.calculate_priority(
                next_assessment.weight_percent,
                record.mastery_score,
                record.confidence_interval,
                next_assessment.due_date.date(),
                record.last_practiced_at.date() if record.last_practiced_at else None
            )
            
            # Recommend difficulty
            days_until = (next_assessment.due_date.date() - date.today()).days
            difficulty = self.select_difficulty_adaptive(
                record.mastery_score,
                record.trend,
                days_until,
                'balanced'  # TODO: Get from user preferences
            )
            
            prioritized.append({
                'topic_id': str(record.topic_id),
                'topic_name': topic.name,
                'course_id': str(topic.course_id),
                'priority': priority,
                'mastery': record.mastery_score,
                'trend': record.trend.value,
                'recommended_difficulty': difficulty.value,
                'assessment_name': next_assessment.name,
                'days_until_exam': days_until
            })
        
        # Sort by priority (descending)
        prioritized.sort(key=lambda x: x['priority'], reverse=True)
        
        return prioritized[:horizon_days * 2]
