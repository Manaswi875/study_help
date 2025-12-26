# Adaptive Study Planner - Product Specification

**Version**: 1.0  
**Date**: December 25, 2025  
**Status**: Planning Phase

---

## Executive Summary

The Adaptive Study Planner is an intelligent learning management system that automatically generates and continuously adjusts a student's daily study schedule and content difficulty based on their quiz/grade history, real-time calendar availability, and mastery progression. The system integrates deeply with Google Calendar for scheduling and optionally syncs with Notion for task management.

---

## Core Objectives

### 1. Personalized Learning Path
- Generate study blocks, topics, and difficulty levels tailored to individual student performance
- Address mastery gaps based on quiz/grade history and assessment weights
- Respect upcoming deadlines and assessment schedules
- Adapt difficulty curve based on student preferences (gentle/balanced/aggressive)

### 2. Real-Life Integration
- Read free/busy time from Google Calendar to avoid scheduling conflicts
- Respect student's availability windows and time constraints
- Sync study tasks to Google Calendar as time-blocked events
- Optionally mirror tasks to Notion workspace for unified task management

### 3. Continuous Adaptation
- No static timetables - plans adjust as new data arrives
- Real-time rescheduling when calendar changes or tasks are missed
- Performance-driven replanning after each quiz or assessment
- Weekly recalibration based on mastery trends and upcoming priorities

---

## User Types & Roles

### Primary User: Student
- Create account and manage profile
- Add courses, topics, and assessment schemas
- Take diagnostic assessments and ongoing quizzes
- View and interact with personalized study schedule
- Provide feedback on difficulty and time allocation
- Connect Google Calendar and Notion integrations

### Future Role: Tutor/Coach (Stretch)
- View student progress and mastery dashboards
- Adjust course content and difficulty levels
- Override or suggest schedule modifications
- Monitor multiple students

---

## Onboarding Flow

### Step 1: Account & Identity (3-5 minutes)
**Goal**: Establish user identity and basic context

**Actions**:
- Sign up via email or SSO (Google, Microsoft)
- Complete profile:
  - Full name
  - School/university name
  - Academic level (high school, undergraduate, graduate)
  - Major/track (optional)
  - Timezone (auto-detected, confirm)
  - Preferred language

**Output**: User account created with basic profile

---

### Step 2: Courses & Assessments Setup (10-15 minutes)
**Goal**: Map the student's academic landscape

**Actions**:
- Add courses manually or via template:
  - Course name (e.g., "Calculus II")
  - Course code (e.g., "MATH 2413")
  - Instructor name (optional)
  - Credit hours (for workload estimation)
  - Semester/term dates
  
- Define assessment schema per course:
  - Assessment types: Quiz, Assignment, Midterm, Final, Project
  - Weight percentages (must sum to 100%)
  - Due dates and frequencies
  - Topics covered per assessment

**Features**:
- Pre-built templates for common courses (Calculus, Physics, etc.)
- CSV import option for bulk course setup
- Future: LMS integration for automatic import

**Output**: Course catalog with weighted assessment schemas

---

### Step 3: Time & Preferences (5-10 minutes)
**Goal**: Understand availability and study preferences

**Actions**:
- Weekly availability matrix:
  - Mark available days and time ranges (e.g., Mon-Fri 6pm-11pm, Sat-Sun 9am-9pm)
  - Set preferred max hours per day (default: 4 hours)
  - Define focus block length (25-90 minutes, default: 50 min)
  - Set break length between blocks (5-30 minutes, default: 10 min)

- Difficulty preferences:
  - Choose difficulty curve:
    - **Gentle**: Gradual progression, more review time
    - **Balanced**: Mix of challenge and reinforcement (default)
    - **Aggressive**: Fast progression, minimal review
  
- Study mode preferences per course:
  - Reading & note-taking
  - Problem sets & practice
  - Flashcards & memorization
  - Projects & labs
  - Video lectures
  - Group study

**Output**: Availability constraints and preference profile

---

### Step 4: Integrations Configuration (5-10 minutes)
**Goal**: Connect external tools for seamless workflow

**Google Calendar**:
- OAuth flow to grant read/write access
- Select calendars to monitor for conflicts (work, classes, personal)
- Choose or create dedicated study calendar (e.g., "Study Planner")
- Set scheduling window (e.g., only schedule between 8am-10pm)
- Configure event format preferences

**Notion (Optional)**:
- Provide Notion integration token
- Select workspace
- Choose or create "Study Tasks" database
- Map database properties:
  - Title, Course, Topics, Difficulty, Due Date, Status, Duration, Mastery Impact
- Enable two-way sync (status updates)

**Output**: Active integrations ready for sync

---

### Step 5: Initial Diagnostic (15-30 minutes)
**Goal**: Baseline mastery assessment for each course

**Actions**:
- For each course, take a short diagnostic quiz (10-20 questions)
- Questions span all major topics at varying difficulty levels
- Adaptive question selection (CAT-style):
  - Start at medium difficulty
  - Adjust based on correctness (harder if correct, easier if wrong)
  - Goal: Estimate mastery level in 10-20 questions per topic

**Alternative**:
- Import existing grade history if available
- System extrapolates mastery from past performance

**Output**: Initial mastery scores for all topics, confidence intervals

---

## User Journey: Daily Workflow

### Morning: Review Today's Plan
1. Open app dashboard or check Google Calendar
2. See today's time-blocked study sessions
3. View current task: "Calculus - Practice Limits (Medium, 50 min)"
4. Click to start session when ready

### During Study Block
1. System displays task details and resources
2. Complete assigned work (problems, reading, quiz)
3. Mark task as complete when done
4. System records time-on-task and performance

### After Quiz/Assessment
1. System ingests new performance data
2. Mastery scores update for relevant topics
3. Schedule automatically adjusts for tomorrow/next week
4. Notification: "Your plan has been updated based on your recent quiz"

### Evening: Quick Check-In (Optional)
1. Daily reflection: "How was today's plan?"
   - Too easy / Just right / Too hard
   - Too much time / Right amount / Not enough time
2. Feedback influences tomorrow's difficulty and duration

### Weekly: Review & Adjust
1. View weekly progress dashboard:
   - Hours studied per course
   - Mastery heatmap (topics color-coded by level)
   - Upcoming assessments and priorities
2. Adjust preferences if needed (e.g., reduce daily hours)
3. System regenerates upcoming week's plan

---

## Feature Specifications

### F1: Personalized Study Blocks
- **Description**: System generates optimal study blocks based on mastery, deadlines, and constraints
- **Inputs**: Mastery scores, assessment weights, due dates, availability
- **Logic**:
  - Priority score = (Assessment weight) × (Mastery gap) × (Urgency factor)
  - Urgency factor = 1 / (days until exam)
  - Allocate blocks to highest-priority topics first
- **Outputs**: Time-blocked study schedule in Google Calendar

### F2: Difficulty Adaptation
- **Description**: Content difficulty adjusts to current mastery level
- **Levels**: Easy, Medium, Hard, Exam-Level
- **Rules**:
  - Mastery < 40%: Easy → Medium content
  - Mastery 40-70%: Medium content with Hard mix
  - Mastery 70-85%: Hard content with Exam-Level mix
  - Mastery > 85%: Exam-Level + spaced review only
- **Override**: User can manually request harder/easier content

### F3: Real-Time Rescheduling
- **Triggers**:
  - New calendar event added → shift affected study blocks
  - Study block missed → reschedule to next available slot
  - Poor quiz performance → increase frequency of that topic
  - Exam date moved → recalculate all priorities
- **Behavior**: System reschedules within 5 minutes of trigger

### F4: Mastery Tracking
- **Calculation**: Bayesian update or Exponentially Weighted Moving Average (EWMA)
  - Initial: Diagnostic quiz score
  - Update: `new_mastery = α × quiz_score + (1-α) × old_mastery`
  - α (learning rate) = 0.3 for quizzes, 0.5 for exams
- **Visualization**: Heatmap per course showing topic mastery (red → yellow → green)

### F5: Spaced Repetition
- **Algorithm**: SM-2 variant
- **Intervals**: 1 day → 3 days → 1 week → 2 weeks → 1 month
- **Trigger**: Topics with mastery > 70% enter review cycle
- **Integration**: Review tasks auto-scheduled as short blocks (10-15 min)

### F6: Google Calendar Sync
- **Read**: All events in selected calendars to identify free/busy
- **Write**: Create study events in dedicated calendar
- **Event Format**:
  - Title: "[Course Code] Topic Name (Difficulty)"
  - Description: Task details, resources, Notion link
  - Duration: Estimated task time + buffer
- **Conflict Resolution**: Never overlap with existing events

### F7: Notion Integration
- **Database Schema**:
  | Property | Type | Description |
  |----------|------|-------------|
  | Title | Title | Task name |
  | Course | Select | Course name |
  | Topics | Multi-select | Topic tags |
  | Difficulty | Select | Easy/Medium/Hard/Exam |
  | Due Date | Date | Target completion |
  | Status | Select | Not Started/In Progress/Completed |
  | Duration | Number | Estimated minutes |
  | Mastery Impact | Number | Expected mastery gain |
  | Calendar Link | URL | Link to Google Calendar event |

- **Sync Behavior**:
  - Task created → Notion row created
  - Task updated → Notion row updated
  - Status changed in app → Notion status updated
  - (Optional) Status changed in Notion → App status updated

### F8: In-App Quiz System
- **Question Types**: MCQ, Multiple Select, Fill-in-blank, Short Answer, Code
- **Adaptive Logic**:
  - Start at user's estimated difficulty for topic
  - If correct: increase difficulty by 1 level
  - If incorrect: decrease difficulty by 1 level or repeat at same level
- **Metadata Capture**:
  - Time per question
  - Correctness
  - Topic mapping
  - Difficulty level
- **Output**: Updated mastery scores, performance analytics

### F9: Analytics Dashboard
- **Metrics**:
  - Total study time (daily/weekly/monthly)
  - Time per course (pie chart)
  - Mastery progression over time (line graph per course)
  - Assessment readiness score (0-100)
  - Consistency score (adherence to schedule)
- **Views**:
  - Today view: Current and upcoming blocks
  - Week view: Visual calendar with drag-drop
  - Course view: Topic mastery heatmap
  - Stats view: Performance trends

### F10: User Feedback Loop
- **Daily Check-In**:
  - Slider: Difficulty (1-5)
  - Slider: Time burden (1-5)
  - Optional text: "Anything to adjust?"
- **Weekly Review**:
  - Mark tasks that were mis-sized (too long/short)
  - Adjust preferences (hours/day, difficulty curve)
  - System recalibrates models based on feedback
- **Impact**: Feedback influences task duration estimates and difficulty selection

---

## Non-Functional Requirements

### Performance
- Schedule generation: < 3 seconds for 7-day plan
- Real-time rescheduling: < 5 seconds
- Calendar sync: < 2 seconds
- Mastery update: < 1 second per quiz

### Scalability
- Support 10,000+ concurrent users
- Handle 100+ courses per user
- Store 10+ years of performance history per user

### Security
- OAuth 2.0 for Google Calendar
- Encrypted storage of API tokens
- HTTPS for all communications
- GDPR-compliant data handling

### Reliability
- 99.5% uptime SLA
- Automated backup every 6 hours
- Graceful degradation if integrations fail
- Offline mode for viewing schedule (mobile)

### Usability
- Onboarding completion: < 30 minutes
- Mobile-responsive design
- WCAG 2.1 AA accessibility compliance
- Support for 5+ languages (initially English)

---

## Success Metrics (KPIs)

### User Engagement
- **Activation Rate**: % of users completing onboarding → Target: 80%
- **Daily Active Users (DAU)**: Target: 60% of registered users
- **Session Length**: Average time in app per day → Target: 10 minutes

### Learning Outcomes
- **Mastery Growth**: Average mastery increase per week → Target: 5-10%
- **Assessment Performance**: Correlation between app usage and grades → Target: +0.5 correlation
- **Completion Rate**: % of scheduled study blocks completed → Target: 75%

### Retention
- **Week 1 Retention**: Target: 70%
- **Month 1 Retention**: Target: 50%
- **Month 6 Retention**: Target: 30%

### Integration Adoption
- **Calendar Connection**: % of users connecting Google Calendar → Target: 90%
- **Notion Connection**: % of users connecting Notion → Target: 40%

---

## Technical Constraints

### Google Calendar API
- Rate limit: 1,000,000 queries/day
- Event limit: 25,000 events per calendar
- Sync latency: ~30 seconds

### Notion API
- Rate limit: 3 requests/second
- Database size: Unlimited (performance degrades > 100k rows)

### Database
- Performance target: < 100ms for 95% of queries
- Storage: Estimate 50 MB per user per year

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Google Calendar API changes | High | Medium | Use official SDK, monitor changelog |
| Poor mastery estimation | High | Medium | Collect user feedback, A/B test algorithms |
| User abandonment after onboarding | High | High | Simplify onboarding, demo mode |
| Scheduling conflicts | Medium | High | Robust conflict detection, user override |
| Data privacy concerns | High | Low | Clear privacy policy, minimal data collection |

---

## Future Enhancements (Roadmap)

### Phase 2 (3-6 months)
- LMS integration (Canvas, Blackboard, Moodle)
- Mobile app (iOS, Android)
- Group study mode (coordinate schedules with peers)
- Pomodoro timer with focus music

### Phase 3 (6-12 months)
- AI-powered question generation
- Video lecture integration (YouTube, Coursera)
- Tutor/coach dashboard for monitoring students
- Gamification (streaks, achievements)

### Phase 4 (12+ months)
- ML-based mastery prediction (LSTM/Transformer models)
- Voice-controlled study assistant
- AR/VR study environments
- Multi-language support (10+ languages)

---

## Appendix

### A. Sample Onboarding Screens (Wireframes)
*To be added: Figma mockups*

### B. Mastery Calculation Formulas
*Detailed mathematical models in separate document*

### C. API Rate Limit Strategies
*Google Calendar and Notion API optimization techniques*

### D. Competitive Analysis
*Comparison with existing tools: Anki, Notion, Google Tasks, etc.*

---

**Document Status**: Complete  
**Next Steps**: Begin module-level specifications and data modeling
