# Module 3: Scheduling & Adaptation Engine

**Owner**: Algorithm Team  
**Priority**: Critical (Core Feature)  
**Dependencies**: Module 1 (Data Model), Module 2 (Mastery Engine)  
**Estimated Effort**: 3-4 weeks

---

## Overview

The Scheduling & Adaptation Engine transforms prioritized study tasks into time-blocked schedules that respect user availability, calendar constraints, and learning science principles. It continuously adapts the schedule based on real-time changes and performance feedback.

---

## Objectives

1. Generate optimal daily/weekly study schedules from prioritized tasks
2. Respect all constraints (time windows, max hours, calendar conflicts)
3. Automatically reschedule when events change or tasks are missed
4. Balance workload across days (avoid overload/underutilization)
5. Integrate breaks and transitions between study blocks

---

## Core Scheduling Algorithm

### Input Parameters
```python
@dataclass
class SchedulingInput:
    user_id: str
    start_date: date
    end_date: date
    prioritized_tasks: list[PrioritizedTask]  # From Mastery Engine
    availability_windows: list[TimeWindow]    # From UserPreferences
    calendar_events: list[CalendarEvent]      # From Google Calendar
    constraints: SchedulingConstraints
```

### Constraints
```python
@dataclass
class SchedulingConstraints:
    max_hours_per_day: float = 4.0
    min_block_length_min: int = 25
    max_block_length_min: int = 120
    preferred_block_length_min: int = 50
    break_length_min: int = 10
    min_break_between_courses_min: int = 15  # Extra break when switching courses
    earliest_start_time: time = time(8, 0)
    latest_end_time: time = time(22, 0)
    max_blocks_per_day: int = 6
    min_gap_before_event_min: int = 15  # Buffer before calendar events
```

---

## Algorithm: Greedy Scheduling with Constraint Satisfaction

### Step 1: Prepare Time Slots
```python
def generate_available_slots(
    date: date,
    availability_windows: list[TimeWindow],
    calendar_events: list[CalendarEvent],
    constraints: SchedulingConstraints
) -> list[TimeSlot]:
    """
    Generate all available time slots for a given day
    
    Args:
        date: Target date
        availability_windows: User's availability for that day
        calendar_events: Existing events (classes, meetings, etc.)
        constraints: Scheduling constraints
    
    Returns:
        List of available TimeSlots
    """
    available_slots = []
    
    for window in availability_windows:
        # Start with user's availability window
        current_start = datetime.combine(date, window.start_time)
        window_end = datetime.combine(date, window.end_time)
        
        # Subtract existing calendar events
        for event in sorted(calendar_events, key=lambda e: e.start_time):
            if event.start_time >= window_end:
                break
            
            if event.end_time <= current_start:
                continue  # Event is before current window
            
            # Create slot before event if sufficient time
            slot_before_event = event.start_time - timedelta(minutes=constraints.min_gap_before_event_min)
            if current_start < slot_before_event:
                duration_min = (slot_before_event - current_start).total_seconds() / 60
                if duration_min >= constraints.min_block_length_min:
                    available_slots.append(TimeSlot(
                        start=current_start,
                        end=slot_before_event,
                        duration_min=int(duration_min)
                    ))
            
            # Move current_start to after the event
            current_start = max(current_start, event.end_time)
        
        # Add remaining time after all events
        if current_start < window_end:
            duration_min = (window_end - current_start).total_seconds() / 60
            if duration_min >= constraints.min_block_length_min:
                available_slots.append(TimeSlot(
                    start=current_start,
                    end=window_end,
                    duration_min=int(duration_min)
                ))
    
    return available_slots
```

### Step 2: Score Task-Slot Combinations
```python
def calculate_placement_score(
    task: PrioritizedTask,
    slot: TimeSlot,
    existing_schedule: list[ScheduledTask],
    constraints: SchedulingConstraints
) -> float:
    """
    Calculate fitness score for placing a task in a slot
    
    Higher score = better placement
    
    Factors:
    - Task priority (higher is better)
    - Time of day fit (match task difficulty to alertness)
    - Workload balance (avoid overloading a single day)
    - Course variety (alternate courses for better context switching)
    """
    score = 0.0
    
    # Factor 1: Base priority (0-100)
    score += task.priority_score * 100
    
    # Factor 2: Time of day fit
    hour = slot.start.hour
    if task.recommended_difficulty in ['hard', 'exam_level']:
        # Hard tasks: prefer morning/early afternoon (peak alertness)
        if 9 <= hour <= 14:
            score += 50
        elif 15 <= hour <= 17:
            score += 20
    else:
        # Easy/medium tasks: flexible, slight preference for afternoon/evening
        if 15 <= hour <= 20:
            score += 30
    
    # Factor 3: Workload balance
    # Penalize if day already has many hours scheduled
    hours_today = sum(t.duration_min for t in existing_schedule if t.date == slot.start.date) / 60
    if hours_today < constraints.max_hours_per_day * 0.5:
        score += 20  # Bonus for underutilized days
    elif hours_today > constraints.max_hours_per_day * 0.8:
        score -= 50  # Penalty for near-max days
    
    # Factor 4: Course variety
    # Bonus if switching to different course from previous block
    if existing_schedule:
        last_task = existing_schedule[-1]
        if last_task.course_id != task.course_id:
            score += 15
    
    # Factor 5: Slot utilization efficiency
    # Prefer slots that match task duration (minimize wasted time)
    task_duration = task.estimated_duration_min + constraints.break_length_min
    utilization = min(task_duration, slot.duration_min) / slot.duration_min
    score += utilization * 20
    
    return score
```

### Step 3: Greedy Assignment
```python
def schedule_tasks_greedy(
    tasks: list[PrioritizedTask],
    available_slots: dict[date, list[TimeSlot]],
    constraints: SchedulingConstraints
) -> list[ScheduledTask]:
    """
    Assign tasks to slots using greedy algorithm
    
    Args:
        tasks: Prioritized list of tasks to schedule
        available_slots: Map of date to available time slots
        constraints: Scheduling constraints
    
    Returns:
        List of scheduled tasks
    """
    scheduled_tasks = []
    remaining_tasks = tasks.copy()
    
    while remaining_tasks:
        best_placement = None
        best_score = -float('inf')
        
        # For each remaining task, find best slot
        for task in remaining_tasks:
            for date, slots in available_slots.items():
                for slot in slots:
                    # Check if task fits in slot
                    task_duration = task.estimated_duration_min + constraints.break_length_min
                    if task_duration > slot.duration_min:
                        continue
                    
                    # Calculate placement score
                    score = calculate_placement_score(task, slot, scheduled_tasks, constraints)
                    
                    if score > best_score:
                        best_score = score
                        best_placement = (task, slot, date)
        
        if best_placement is None:
            # No more valid placements
            break
        
        # Schedule the best task-slot combination
        task, slot, date = best_placement
        scheduled_task = ScheduledTask(
            task_id=task.id,
            course_id=task.course_id,
            topic_ids=task.topic_ids,
            start_time=slot.start,
            end_time=slot.start + timedelta(minutes=task.estimated_duration_min),
            duration_min=task.estimated_duration_min,
            difficulty=task.recommended_difficulty,
            priority_score=task.priority_score
        )
        
        scheduled_tasks.append(scheduled_task)
        remaining_tasks.remove(task)
        
        # Update available slots (consume used time)
        update_slot_availability(available_slots[date], scheduled_task, constraints.break_length_min)
    
    return scheduled_tasks
```

---

## Adaptation Mechanisms

### Trigger 1: Calendar Event Added
```python
def handle_calendar_event_added(
    new_event: CalendarEvent,
    existing_schedule: list[ScheduledTask]
) -> list[ScheduledTask]:
    """
    Reschedule tasks affected by new calendar event
    
    Args:
        new_event: Newly added calendar event
        existing_schedule: Current schedule
    
    Returns:
        Updated schedule with affected tasks rescheduled
    """
    affected_tasks = []
    unaffected_tasks = []
    
    # Identify tasks that overlap with new event
    for task in existing_schedule:
        if tasks_overlap(task, new_event):
            affected_tasks.append(task)
            # Mark as unscheduled
            task.status = 'pending'
            task.scheduled_start = None
            task.scheduled_end = None
        else:
            unaffected_tasks.append(task)
    
    # Reschedule affected tasks
    if affected_tasks:
        # Re-prioritize affected tasks
        affected_tasks.sort(key=lambda t: t.priority_score, reverse=True)
        
        # Find next available slots
        available_slots = get_available_slots_after(datetime.now(), horizon_days=7)
        rescheduled = schedule_tasks_greedy(affected_tasks, available_slots, constraints)
        
        # Notify user
        notify_user(f"Rescheduled {len(affected_tasks)} tasks due to new event: {new_event.title}")
    
    return unaffected_tasks + rescheduled
```

### Trigger 2: Task Missed/Skipped
```python
def handle_task_missed(
    missed_task: ScheduledTask,
    existing_schedule: list[ScheduledTask]
) -> list[ScheduledTask]:
    """
    Reschedule a missed task
    
    Args:
        missed_task: Task that was skipped or not completed
        existing_schedule: Current schedule
    
    Returns:
        Updated schedule
    """
    # Mark task as pending
    missed_task.status = 'pending'
    missed_task.scheduled_start = None
    missed_task.scheduled_end = None
    
    # Increase priority (urgency increased)
    missed_task.priority_score *= 1.2
    
    # Find next available slot (prefer same day if possible)
    now = datetime.now()
    available_slots = get_available_slots_after(now, horizon_days=1)
    
    if not available_slots:
        # If no slots today, schedule for tomorrow
        available_slots = get_available_slots_after(now + timedelta(days=1), horizon_days=1)
    
    rescheduled = schedule_tasks_greedy([missed_task], available_slots, constraints)
    
    if rescheduled:
        notify_user(f"Rescheduled missed task: {missed_task.title} to {rescheduled[0].start_time}")
        return existing_schedule + rescheduled
    else:
        notify_user(f"Could not reschedule {missed_task.title}. Please free up time.")
        return existing_schedule
```

### Trigger 3: Poor Quiz Performance
```python
def handle_poor_performance(
    topic_id: str,
    quiz_score: float,
    existing_schedule: list[ScheduledTask],
    mastery_threshold: float = 60.0
) -> list[ScheduledTask]:
    """
    Increase frequency of topic practice after poor performance
    
    Args:
        topic_id: Topic that needs more practice
        quiz_score: Recent quiz score (0-100)
        existing_schedule: Current schedule
        mastery_threshold: Score below this triggers intervention
    
    Returns:
        Updated schedule with additional practice sessions
    """
    if quiz_score >= mastery_threshold:
        return existing_schedule  # No intervention needed
    
    # Calculate how many additional sessions needed
    gap = mastery_threshold - quiz_score
    additional_sessions = int(gap / 15) + 1  # ~1 session per 15% gap
    
    # Create additional practice tasks
    new_tasks = []
    for i in range(additional_sessions):
        task = create_practice_task(
            topic_id=topic_id,
            difficulty='medium',  # Start at medium to rebuild confidence
            duration_min=30,  # Shorter sessions for struggling topics
            priority_boost=1.5  # High priority
        )
        new_tasks.append(task)
    
    # Schedule new tasks over next 3-5 days (distributed practice)
    available_slots = get_available_slots_after(datetime.now(), horizon_days=5)
    rescheduled = schedule_tasks_greedy(new_tasks, available_slots, constraints)
    
    notify_user(f"Added {len(rescheduled)} practice sessions for {get_topic_name(topic_id)} based on recent performance")
    
    return existing_schedule + rescheduled
```

### Trigger 4: Exam Date Changed
```python
def handle_exam_date_changed(
    assessment_id: str,
    old_date: date,
    new_date: date,
    existing_schedule: list[ScheduledTask]
) -> list[ScheduledTask]:
    """
    Recalculate all priorities and regenerate schedule when exam date changes
    
    Args:
        assessment_id: Assessment with changed date
        old_date, new_date: Old and new exam dates
        existing_schedule: Current schedule
    
    Returns:
        Completely regenerated schedule
    """
    # Get all topics covered in this assessment
    affected_topics = get_assessment_topics(assessment_id)
    
    # Recalculate priorities for all tasks (urgency factor changed)
    all_tasks = get_all_pending_tasks(user_id)
    for task in all_tasks:
        if any(topic_id in task.topic_ids for topic_id in affected_topics):
            # Recalculate priority with new urgency
            days_until_exam = (new_date - date.today()).days
            task.priority_score = calculate_priority(
                task.assessment_weight,
                task.mastery_score,
                task.confidence_interval,
                new_date,
                task.last_practiced
            )
    
    # Cancel existing schedule for affected topics
    unaffected_tasks = [t for t in existing_schedule if not any(tid in affected_topics for tid in t.topic_ids)]
    affected_scheduled = [t for t in existing_schedule if any(tid in affected_topics for tid in t.topic_ids)]
    
    # Mark affected tasks as pending
    for task in affected_scheduled:
        task.status = 'pending'
    
    # Regenerate schedule for affected tasks
    available_slots = get_available_slots_after(datetime.now(), horizon_days=14)
    rescheduled = schedule_tasks_greedy(all_tasks, available_slots, constraints)
    
    notify_user(f"Regenerated schedule for {get_assessment_name(assessment_id)}. Exam moved from {old_date} to {new_date}")
    
    return unaffected_tasks + rescheduled
```

---

## Workload Balancing

### Daily Workload Metrics
```python
def calculate_daily_workload(scheduled_tasks: list[ScheduledTask], date: date) -> WorkloadMetrics:
    """
    Calculate workload metrics for a specific day
    
    Returns:
        WorkloadMetrics with total hours, number of blocks, course distribution
    """
    tasks_today = [t for t in scheduled_tasks if t.start_time.date() == date]
    
    total_minutes = sum(t.duration_min for t in tasks_today)
    total_hours = total_minutes / 60.0
    num_blocks = len(tasks_today)
    
    # Course distribution
    course_minutes = {}
    for task in tasks_today:
        course_minutes[task.course_id] = course_minutes.get(task.course_id, 0) + task.duration_min
    
    # Difficulty distribution
    difficulty_counts = {
        'easy': sum(1 for t in tasks_today if t.difficulty == 'easy'),
        'medium': sum(1 for t in tasks_today if t.difficulty == 'medium'),
        'hard': sum(1 for t in tasks_today if t.difficulty == 'hard'),
        'exam_level': sum(1 for t in tasks_today if t.difficulty == 'exam_level')
    }
    
    return WorkloadMetrics(
        total_hours=total_hours,
        num_blocks=num_blocks,
        course_distribution=course_minutes,
        difficulty_distribution=difficulty_counts
    )
```

### Workload Smoothing
```python
def smooth_weekly_workload(
    scheduled_tasks: list[ScheduledTask],
    week_start: date,
    constraints: SchedulingConstraints
) -> list[ScheduledTask]:
    """
    Redistribute tasks across week to balance workload
    
    Goal: Avoid days with 0 hours and days with max hours
    """
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    daily_workloads = {d: calculate_daily_workload(scheduled_tasks, d) for d in week_dates}
    
    # Find overloaded and underutilized days
    overloaded = [d for d, w in daily_workloads.items() if w.total_hours > constraints.max_hours_per_day * 0.9]
    underutilized = [d for d, w in daily_workloads.items() if w.total_hours < constraints.max_hours_per_day * 0.3]
    
    if not overloaded or not underutilized:
        return scheduled_tasks  # No balancing needed
    
    # Move low-priority tasks from overloaded to underutilized days
    for overload_date in overloaded:
        tasks_that_day = [t for t in scheduled_tasks if t.start_time.date() == overload_date]
        # Sort by priority (lowest first for moving)
        tasks_that_day.sort(key=lambda t: t.priority_score)
        
        for task in tasks_that_day:
            # Try to move to underutilized day
            for underutil_date in underutilized:
                available_slots = get_available_slots_for_date(underutil_date)
                if can_fit_task(task, available_slots):
                    # Move task
                    move_task_to_date(task, underutil_date)
                    notify_user(f"Balanced workload: moved {task.title} from {overload_date} to {underutil_date}")
                    break
            
            # Recheck workload
            if calculate_daily_workload(scheduled_tasks, overload_date).total_hours <= constraints.max_hours_per_day * 0.8:
                break
    
    return scheduled_tasks
```

---

## Rolling Horizon Planning

### Nightly Replanning
```python
def nightly_replan(user_id: str, horizon_days: int = 7):
    """
    Run nightly to regenerate upcoming week's schedule
    
    Called at 2am daily via scheduled job
    """
    # Fetch latest data
    user_prefs = get_user_preferences(user_id)
    prioritized_tasks = get_next_tasks(user_id, horizon_days=horizon_days)
    calendar_events = fetch_google_calendar_events(user_id, horizon_days=horizon_days)
    
    # Keep completed and in-progress tasks
    existing_schedule = get_user_schedule(user_id)
    locked_tasks = [t for t in existing_schedule if t.status in ['completed', 'in_progress']]
    
    # Regenerate schedule for pending tasks
    start_date = date.today()
    end_date = start_date + timedelta(days=horizon_days)
    
    available_slots = generate_available_slots_for_range(
        user_id,
        start_date,
        end_date,
        user_prefs,
        calendar_events
    )
    
    new_schedule = schedule_tasks_greedy(
        prioritized_tasks,
        available_slots,
        user_prefs.constraints
    )
    
    # Combine locked and new tasks
    full_schedule = locked_tasks + new_schedule
    
    # Balance workload
    full_schedule = smooth_weekly_workload(full_schedule, start_date, user_prefs.constraints)
    
    # Sync to Google Calendar
    sync_schedule_to_calendar(user_id, new_schedule)
    
    # Notify if significant changes
    if len(new_schedule) > 5:
        notify_user(f"Your schedule for the next {horizon_days} days has been updated")
```

---

## API Endpoints

### POST /api/schedule/generate
**Description**: Generate schedule for user

**Request**:
```json
{
  "user_id": "uuid",
  "start_date": "2025-12-26",
  "end_date": "2026-01-02",
  "horizon_days": 7
}
```

**Response**:
```json
{
  "schedule": [
    {
      "task_id": "uuid",
      "title": "Calculus - Integration by Parts",
      "course_name": "Calculus II",
      "start_time": "2025-12-26T18:00:00Z",
      "end_time": "2025-12-26T18:50:00Z",
      "duration_min": 50,
      "difficulty": "medium",
      "calendar_event_id": "google_event_id"
    }
  ],
  "unscheduled_tasks": 3,
  "total_hours": 18.5,
  "daily_breakdown": [
    {"date": "2025-12-26", "hours": 2.5, "blocks": 3},
    {"date": "2025-12-27", "hours": 3.0, "blocks": 3}
  ]
}
```

### POST /api/schedule/replan
**Description**: Trigger immediate replanning

**Request**:
```json
{
  "user_id": "uuid",
  "reason": "calendar_change"
}
```

### PUT /api/schedule/task/{task_id}/reschedule
**Description**: Reschedule a specific task

**Request**:
```json
{
  "new_start_time": "2025-12-27T19:00:00Z",
  "reason": "user_preference"
}
```

---

## Success Criteria
✅ Schedule generation < 3 seconds for 7-day horizon  
✅ Real-time rescheduling < 5 seconds  
✅ > 90% of tasks successfully scheduled within constraints  
✅ Daily workload within user's max hours limit  
✅ No scheduling conflicts with calendar events  
✅ User satisfaction score > 4/5 for schedule quality

---

**Status**: Ready for Implementation  
**Next Module**: Module 4 - Google Calendar Integration
