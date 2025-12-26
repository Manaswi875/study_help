# Module 2: Mastery & Difficulty Engine

**Owner**: ML/Algorithm Team  
**Priority**: Critical (Core Intelligence)  
**Dependencies**: Module 1 (Data Model)  
**Estimated Effort**: 3-4 weeks

---

## Overview

The Mastery & Difficulty Engine is the intelligence core that converts quiz/grade history into actionable mastery scores and content difficulty recommendations. It determines what the student should study, at what difficulty level, and how frequently.

---

## Objectives

1. Accurately estimate topic mastery from quiz performance
2. Track mastery trends (improving, stagnating, declining)
3. Select optimal difficulty level for each study session
4. Prioritize topics based on mastery gaps, assessment weights, and deadlines
5. Support spaced repetition for retention

---

## Mastery Calculation Algorithms

### Algorithm 1: Exponentially Weighted Moving Average (EWMA)
**Use Case**: Primary algorithm for continuous mastery updates

**Formula**:
```
M_new = α * S_quiz + (1 - α) * M_old

Where:
- M_new: Updated mastery score (0-100)
- M_old: Previous mastery score
- S_quiz: Recent quiz performance (%)
- α: Learning rate (0-1)
```

**Learning Rate (α) Selection**:
- **Diagnostic quiz**: α = 1.0 (full replacement, no prior data)
- **Practice quiz**: α = 0.3 (moderate weight to new data)
- **Major exam**: α = 0.5 (high confidence in exam results)
- **Single question**: α = 0.1 (low weight to avoid volatility)

**Implementation**:
```python
def ewma_update(old_mastery: float, new_score: float, alpha: float) -> float:
    """
    Update mastery using EWMA
    
    Args:
        old_mastery: Previous mastery score (0-100)
        new_score: New quiz performance (0-100)
        alpha: Learning rate (0-1)
    
    Returns:
        Updated mastery score (0-100)
    """
    return alpha * new_score + (1 - alpha) * old_mastery

# Example usage
old_mastery = 65.0  # Student had 65% mastery
new_quiz_score = 80.0  # Scored 80% on recent quiz
alpha = 0.3  # Standard quiz learning rate

new_mastery = ewma_update(old_mastery, new_quiz_score, alpha)
# Result: 0.3 * 80 + 0.7 * 65 = 24 + 45.5 = 69.5%
```

**Advantages**:
- Simple, fast computation
- Smooth progression (avoids wild swings)
- Gives more weight to recent performance

**Disadvantages**:
- Doesn't model uncertainty explicitly
- May be slow to react to sudden changes

---

### Algorithm 2: Bayesian Knowledge Tracing (BKT) - Advanced
**Use Case**: Future upgrade for more sophisticated modeling

**Parameters**:
- P(L₀): Prior probability of mastery (from diagnostic)
- P(T): Probability of learning (transition from not-mastered to mastered)
- P(S): Probability of slip (getting question wrong despite mastery)
- P(G): Probability of guess (getting question right despite not mastering)

**Formula**:
```
P(L_n | correct) = P(L_{n-1} | evidence) + (1 - P(L_{n-1})) * P(T)
                   / [P(L_{n-1}) * (1 - P(S)) + (1 - P(L_{n-1})) * P(G)]
```

**Implementation** (pseudocode):
```python
class BayesianKnowledgeTracing:
    def __init__(self, p_l0=0.5, p_t=0.1, p_s=0.1, p_g=0.2):
        self.p_l0 = p_l0  # Prior mastery
        self.p_t = p_t    # Learning probability
        self.p_s = p_s    # Slip probability
        self.p_g = p_g    # Guess probability
        self.p_l = p_l0   # Current mastery probability
    
    def update(self, is_correct: bool):
        if is_correct:
            numerator = self.p_l * (1 - self.p_s)
            denominator = numerator + (1 - self.p_l) * self.p_g
        else:
            numerator = self.p_l * self.p_s
            denominator = numerator + (1 - self.p_l) * (1 - self.p_g)
        
        self.p_l = numerator / denominator + (1 - self.p_l) * self.p_t
        return self.p_l * 100  # Convert to 0-100 scale
```

**Advantages**:
- Models uncertainty explicitly
- Accounts for guessing and slips
- More accurate for adaptive testing

**Disadvantages**:
- More complex to tune
- Requires more historical data
- Higher computational cost

---

## Confidence Interval Calculation

**Purpose**: Measure how confident we are in the mastery estimate

**Formula**:
```
CI = max(5, 20 / sqrt(N))

Where:
- CI: Confidence interval (standard deviation equivalent)
- N: Number of quiz attempts for this topic
- 5: Minimum confidence (even with many attempts)
- 20: Maximum confidence (with very few attempts)
```

**Implementation**:
```python
import math

def calculate_confidence_interval(attempt_count: int) -> float:
    """
    Calculate confidence interval for mastery estimate
    
    Args:
        attempt_count: Number of quizzes/attempts for this topic
    
    Returns:
        Confidence interval (lower is more confident)
    """
    return max(5.0, 20.0 / math.sqrt(attempt_count))

# Examples
calculate_confidence_interval(1)   # 20.0 (very uncertain)
calculate_confidence_interval(4)   # 10.0 (moderate)
calculate_confidence_interval(16)  # 5.0 (confident)
calculate_confidence_interval(100) # 5.0 (capped at minimum)
```

**Usage**:
- Display mastery as: "65% ± 10%" (mastery ± CI)
- Higher CI → prioritize more practice to improve confidence
- Lower CI → can move to harder content

---

## Trend Detection

**Purpose**: Identify if mastery is improving, stable, or declining

**Algorithm**:
```python
def detect_trend(old_mastery: float, new_mastery: float, threshold: float = 5.0) -> str:
    """
    Detect mastery trend
    
    Args:
        old_mastery: Previous mastery score
        new_mastery: Current mastery score
        threshold: Minimum change to consider a trend (default 5%)
    
    Returns:
        'improving', 'stable', or 'declining'
    """
    delta = new_mastery - old_mastery
    
    if delta > threshold:
        return 'improving'
    elif delta < -threshold:
        return 'declining'
    else:
        return 'stable'

# Example
detect_trend(65, 72)  # 'improving' (delta = +7)
detect_trend(65, 67)  # 'stable' (delta = +2, below threshold)
detect_trend(65, 58)  # 'declining' (delta = -7)
```

**Enhanced Trend Detection** (using last N attempts):
```python
def detect_trend_advanced(mastery_history: list[float], window: int = 5) -> str:
    """
    Detect trend using linear regression over recent history
    
    Args:
        mastery_history: List of recent mastery scores (newest last)
        window: Number of recent attempts to consider
    
    Returns:
        'improving', 'stable', or 'declining'
    """
    if len(mastery_history) < 2:
        return 'stable'
    
    recent = mastery_history[-window:]
    n = len(recent)
    
    # Simple linear regression slope
    x = list(range(n))
    y = recent
    
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    slope = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n)) / \
            sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if slope > 1.0:
        return 'improving'
    elif slope < -1.0:
        return 'declining'
    else:
        return 'stable'
```

---

## Difficulty Selection Logic

### Difficulty Levels
1. **Easy**: 50-60% of questions expected to be correct
2. **Medium**: 65-75% correct
3. **Hard**: 75-85% correct
4. **Exam-Level**: 85-95% correct (mimics real exam difficulty)

### Selection Rules

**Rule 1: Based on Mastery Score**
```python
def select_difficulty_by_mastery(mastery: float) -> str:
    """
    Select difficulty based on current mastery
    
    Args:
        mastery: Current mastery score (0-100)
    
    Returns:
        'easy', 'medium', 'hard', or 'exam_level'
    """
    if mastery < 40:
        return 'easy'
    elif mastery < 60:
        return 'medium'
    elif mastery < 80:
        return 'hard'
    else:
        return 'exam_level'
```

**Rule 2: Based on Trend and Exam Proximity**
```python
def select_difficulty_adaptive(
    mastery: float, 
    trend: str, 
    days_until_exam: int,
    difficulty_curve: str
) -> str:
    """
    Adaptive difficulty selection considering multiple factors
    
    Args:
        mastery: Current mastery score (0-100)
        trend: 'improving', 'stable', or 'declining'
        days_until_exam: Days remaining until exam
        difficulty_curve: User preference ('gentle', 'balanced', 'aggressive')
    
    Returns:
        Recommended difficulty level
    """
    # Base difficulty from mastery
    base_diff = select_difficulty_by_mastery(mastery)
    
    # Adjust based on trend
    if trend == 'declining':
        # Step down to rebuild confidence
        diff_order = ['easy', 'medium', 'hard', 'exam_level']
        idx = diff_order.index(base_diff)
        base_diff = diff_order[max(0, idx - 1)]
    elif trend == 'improving' and difficulty_curve == 'aggressive':
        # Push harder if improving and user wants aggressive curve
        diff_order = ['easy', 'medium', 'hard', 'exam_level']
        idx = diff_order.index(base_diff)
        base_diff = diff_order[min(3, idx + 1)]
    
    # Adjust based on exam proximity
    if days_until_exam <= 7 and mastery >= 60:
        # Focus on exam-level difficulty when exam is near
        return 'exam_level'
    elif days_until_exam <= 3 and mastery < 60:
        # Close gap with medium difficulty when exam is very near
        return 'medium'
    
    return base_diff
```

---

## Task Prioritization Algorithm

**Objective**: Rank topics to determine what to study next

### Priority Score Formula
```
Priority = (Weight * Gap * Urgency) / (Confidence * Recency)

Where:
- Weight: Assessment weight (0-1, normalized)
- Gap: Mastery gap (1 - mastery/100)
- Urgency: 1 / max(1, days_until_exam)
- Confidence: 1 / (1 + confidence_interval/100)
- Recency: 1 / (1 + days_since_last_practice)
```

**Implementation**:
```python
from datetime import datetime, date

def calculate_priority(
    assessment_weight: float,
    mastery_score: float,
    confidence_interval: float,
    exam_date: date,
    last_practiced: date
) -> float:
    """
    Calculate priority score for a topic
    
    Args:
        assessment_weight: Weight of assessment covering this topic (0-100)
        mastery_score: Current mastery (0-100)
        confidence_interval: Confidence in mastery estimate
        exam_date: Date of upcoming exam
        last_practiced: Last practice date for this topic
    
    Returns:
        Priority score (higher = more urgent)
    """
    # Normalize weight to 0-1
    weight = assessment_weight / 100.0
    
    # Calculate mastery gap (how much improvement needed)
    gap = 1.0 - (mastery_score / 100.0)
    
    # Calculate urgency (higher as exam approaches)
    days_until_exam = max(1, (exam_date - date.today()).days)
    urgency = 1.0 / days_until_exam
    
    # Calculate confidence factor (lower confidence = higher priority)
    confidence_factor = 1.0 / (1.0 + confidence_interval / 100.0)
    
    # Calculate recency factor (longer since last practice = higher priority)
    days_since_practice = (date.today() - last_practiced).days if last_practiced else 30
    recency_factor = 1.0 / (1.0 + days_since_practice)
    
    # Combine factors
    priority = (weight * gap * urgency * confidence_factor) / recency_factor
    
    return priority

# Example
priority = calculate_priority(
    assessment_weight=30.0,  # 30% of final grade
    mastery_score=55.0,      # 55% mastered
    confidence_interval=12.0,
    exam_date=date(2025, 12, 31),  # 6 days away
    last_practiced=date(2025, 12, 20)  # 5 days ago
)
# Result: (0.3 * 0.45 * 0.167 * 0.893) / 0.167 = ~0.127
```

### Priority-Based Task Selection
```python
def select_next_tasks(user_id: str, horizon_days: int = 7) -> list:
    """
    Select and prioritize tasks for upcoming days
    
    Args:
        user_id: User identifier
        horizon_days: How many days ahead to plan
    
    Returns:
        List of prioritized study tasks
    """
    # Fetch all topics with their data
    topics = get_user_topics_with_mastery(user_id)
    
    # Calculate priority for each topic
    prioritized_topics = []
    for topic in topics:
        priority = calculate_priority(
            topic.assessment_weight,
            topic.mastery_score,
            topic.confidence_interval,
            topic.exam_date,
            topic.last_practiced
        )
        
        prioritized_topics.append({
            'topic_id': topic.id,
            'course_id': topic.course_id,
            'priority': priority,
            'recommended_difficulty': select_difficulty_adaptive(
                topic.mastery_score,
                topic.trend,
                (topic.exam_date - date.today()).days,
                topic.user_difficulty_curve
            )
        })
    
    # Sort by priority (descending)
    prioritized_topics.sort(key=lambda x: x['priority'], reverse=True)
    
    # Select top topics and create study tasks
    return prioritized_topics[:horizon_days * 2]  # ~2 tasks per day
```

---

## Spaced Repetition Integration

### SM-2 Algorithm (Simplified)
**Purpose**: Schedule reviews for topics with high mastery

**Parameters**:
- EF (Easiness Factor): Multiplier for interval growth (default: 2.5)
- Interval: Days until next review

**Algorithm**:
```python
def calculate_next_review(
    easiness_factor: float,
    current_interval: int,
    quiz_quality: int
) -> tuple[int, float]:
    """
    Calculate next review interval using SM-2 algorithm
    
    Args:
        easiness_factor: Current EF (1.3-2.5, default 2.5)
        current_interval: Current interval in days
        quiz_quality: Quality of recall (0-5, where 5=perfect, 3=threshold)
    
    Returns:
        (next_interval_days, updated_easiness_factor)
    """
    # Update easiness factor based on quality
    new_ef = easiness_factor + (0.1 - (5 - quiz_quality) * (0.08 + (5 - quiz_quality) * 0.02))
    new_ef = max(1.3, new_ef)  # EF minimum is 1.3
    
    # Calculate next interval
    if quiz_quality < 3:
        # Failed recall, reset to 1 day
        next_interval = 1
    else:
        if current_interval == 0:
            next_interval = 1
        elif current_interval == 1:
            next_interval = 6
        else:
            next_interval = int(current_interval * new_ef)
    
    return next_interval, new_ef

# Example
interval, ef = calculate_next_review(
    easiness_factor=2.5,
    current_interval=6,
    quiz_quality=4  # Good recall
)
# Result: (15 days, 2.5)
```

### Integration with Mastery System
```python
def update_mastery_with_spaced_repetition(
    user_id: str,
    topic_id: str,
    quiz_score: float,
    mastery_record
):
    """
    Update mastery and schedule next review
    
    Args:
        user_id, topic_id: Identifiers
        quiz_score: Score on recent quiz (0-100)
        mastery_record: Current MasteryRecord object
    """
    # Update mastery using EWMA
    new_mastery = ewma_update(
        mastery_record.mastery_score,
        quiz_score,
        alpha=0.3
    )
    
    # Convert quiz score to quality (0-5 scale for SM-2)
    quality = int((quiz_score / 100.0) * 5)
    
    # Calculate next review if mastery is sufficient
    if new_mastery >= 70:
        next_interval, new_ef = calculate_next_review(
            mastery_record.easiness_factor or 2.5,
            mastery_record.review_interval_days or 1,
            quality
        )
        
        mastery_record.review_interval_days = next_interval
        mastery_record.next_review_date = date.today() + timedelta(days=next_interval)
        mastery_record.easiness_factor = new_ef
    else:
        # Low mastery, practice more frequently
        mastery_record.review_interval_days = 1
        mastery_record.next_review_date = date.today() + timedelta(days=1)
    
    mastery_record.mastery_score = new_mastery
    mastery_record.last_practiced_at = datetime.now()
    
    return mastery_record
```

---

## API Endpoints

### GET /api/mastery/{user_id}/topics
**Description**: Retrieve mastery scores for all topics

**Response**:
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

### GET /api/mastery/{user_id}/topic/{topic_id}
**Description**: Get detailed mastery history for a specific topic

**Response**:
```json
{
  "topic_id": "uuid",
  "current_mastery": 68.5,
  "confidence_interval": 8.2,
  "trend": "improving",
  "history": [
    {"date": "2025-12-01", "mastery": 45.0, "quiz_score": 45.0},
    {"date": "2025-12-08", "mastery": 52.5, "quiz_score": 60.0},
    {"date": "2025-12-15", "mastery": 61.5, "quiz_score": 70.0},
    {"date": "2025-12-20", "mastery": 68.5, "quiz_score": 75.0}
  ]
}
```

### POST /api/mastery/{user_id}/update
**Description**: Update mastery after a quiz

**Request**:
```json
{
  "topic_id": "uuid",
  "quiz_score": 80.0,
  "question_count": 10,
  "time_spent_min": 25,
  "difficulty_level": "medium"
}
```

**Response**:
```json
{
  "old_mastery": 68.5,
  "new_mastery": 72.0,
  "confidence_interval": 7.5,
  "trend": "improving",
  "next_review_date": "2025-12-30"
}
```

### GET /api/tasks/next/{user_id}
**Description**: Get prioritized next tasks

**Query Parameters**:
- `horizon_days`: Planning horizon (default: 7)
- `max_tasks`: Maximum tasks to return (default: 14)

**Response**:
```json
[
  {
    "topic_id": "uuid",
    "topic_name": "Integration by Parts",
    "course_name": "Calculus II",
    "priority_score": 0.127,
    "recommended_difficulty": "medium",
    "estimated_duration_min": 50,
    "reason": "30% of final exam, 45% mastery gap, 6 days until exam"
  }
]
```

---

## Testing Strategy

### Unit Tests
```python
def test_ewma_update():
    assert ewma_update(50, 80, 0.3) == 59.0
    assert ewma_update(100, 50, 0.5) == 75.0

def test_confidence_calculation():
    assert calculate_confidence_interval(1) == 20.0
    assert calculate_confidence_interval(16) == 5.0

def test_difficulty_selection():
    assert select_difficulty_by_mastery(35) == 'easy'
    assert select_difficulty_by_mastery(75) == 'hard'
```

### Integration Tests
- Multi-quiz mastery progression
- Priority calculation with real data
- Spaced repetition scheduling

### Performance Tests
- Mastery update for 1000 topics < 1 second
- Priority ranking for 100 topics < 500ms

---

## Success Criteria
✅ Mastery updates within 1 second  
✅ Accurate difficulty recommendations (validated by user feedback)  
✅ Priority scores correlate with exam performance  
✅ Spaced repetition intervals follow SM-2 algorithm  
✅ Unit test coverage > 85%

---

**Status**: Ready for Implementation  
**Next Module**: Module 3 - Scheduling & Adaptation Engine
