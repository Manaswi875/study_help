# System Architecture - Adaptive Study Planner

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Web App     │  │ Mobile App   │  │ Browser Ext  │         │
│  │  (React)     │  │ (Future)     │  │ (Future)     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│  ┌────────────────────────────────────────────────────────────┐│
│  │              FastAPI Application                           ││
│  │  • Authentication (JWT)                                    ││
│  │  • Rate Limiting                                           ││
│  │  • Request Validation                                      ││
│  │  • CORS Configuration                                      ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│    SERVICE LAYER          │  │   INTEGRATION LAYER       │
│                           │  │                           │
│  ┌──────────────────────┐│  │ ┌──────────────────────┐ │
│  │  Auth Service        ││  │ │ Google Calendar API  │ │
│  │  • User management   ││  │ │ • OAuth 2.0          │ │
│  │  • JWT tokens        ││  │ │ • Event CRUD         │ │
│  └──────────────────────┘│  │ │ • Sync engine        │ │
│                           │  │ └──────────────────────┘ │
│  ┌──────────────────────┐│  │                           │
│  │  Mastery Engine      ││  │ ┌──────────────────────┐ │
│  │  • EWMA algorithm    ││  │ │ Notion API           │ │
│  │  • Difficulty select ││  │ │ • Database ops       │ │
│  │  • Priority calc     ││  │ │ • Page CRUD          │ │
│  │  • SM-2 spaced rep   ││  │ │ • Two-way sync       │ │
│  └──────────────────────┘│  │ └──────────────────────┘ │
│                           │  └───────────────────────────┘
│  ┌──────────────────────┐│
│  │  Scheduling Engine   ││
│  │  • Time slot gen     ││
│  │  • Constraint solver ││
│  │  • Auto-reschedule   ││
│  │  • Workload balance  ││
│  └──────────────────────┘│
│                           │
│  ┌──────────────────────┐│
│  │  Quiz Engine         ││
│  │  • Adaptive testing  ││
│  │  • Performance track ││
│  │  • Question bank     ││
│  └──────────────────────┘│
│                           │
│  ┌──────────────────────┐│
│  │  Analytics Service   ││
│  │  • Progress tracking ││
│  │  • Insights gen      ││
│  │  • Reports           ││
│  └──────────────────────┘│
└───────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              PostgreSQL Database                         │ │
│  │                                                          │ │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │ │
│  │  │ Users  │  │Courses │  │ Topics │  │Mastery │       │ │
│  │  └────────┘  └────────┘  └────────┘  └────────┘       │ │
│  │                                                          │ │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │ │
│  │  │ Tasks  │  │Calendar│  │ Notion │  │ Perfs  │       │ │
│  │  └────────┘  └────────┘  └────────┘  └────────┘       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Redis Cache                            │ │
│  │  • Session storage                                       │ │
│  │  • Task queue (Celery)                                   │ │
│  │  • Temporary data                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKGROUND JOBS LAYER                         │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                  Celery Workers                            ││
│  │                                                            ││
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐││
│  │  │ Nightly Replan │  │ Calendar Sync  │  │ Notion Sync  │││
│  │  │ (2 AM daily)   │  │ (Every 15 min) │  │ (Every 15min)│││
│  │  └────────────────┘  └────────────────┘  └──────────────┘││
│  │                                                            ││
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐││
│  │  │ Email Notif    │  │ Analytics Agg  │  │ Data Cleanup │││
│  │  │ (On demand)    │  │ (Daily)        │  │ (Weekly)     │││
│  │  └────────────────┘  └────────────────┘  └──────────────┘││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Student Takes Quiz

```
┌─────────┐     1. Complete Quiz      ┌─────────┐
│ Student │ ──────────────────────────>│ Web App │
└─────────┘                            └─────────┘
                                             │
                                             │ 2. POST /mastery/update
                                             ▼
                                       ┌─────────┐
                                       │  API    │
                                       └─────────┘
                                             │
                                             │ 3. Process results
                                             ▼
                                    ┌─────────────────┐
                                    │ Mastery Engine  │
                                    │ • Update EWMA   │
                                    │ • Calculate CI  │
                                    │ • Detect trend  │
                                    └─────────────────┘
                                             │
                                             │ 4. Store
                                             ▼
                                       ┌─────────┐
                                       │Database │
                                       └─────────┘
                                             │
                                             │ 5. Trigger reschedule
                                             ▼
                                    ┌─────────────────┐
                                    │Scheduling Engine│
                                    │ • Reprioritize  │
                                    │ • Adjust plan   │
                                    └─────────────────┘
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       │                     │                     │
                       ▼                     ▼                     ▼
                ┌───────────┐         ┌─────────┐         ┌───────────┐
                │  Google   │         │Database │         │  Notion   │
                │  Calendar │         │         │         │  Sync     │
                │  • Update │         │ • Save  │         │ • Update  │
                │   events  │         │  tasks  │         │   pages   │
                └───────────┘         └─────────┘         └───────────┘
                       │                     │                     │
                       └─────────────────────┼─────────────────────┘
                                             │
                                             │ 6. Notify user
                                             ▼
                                       ┌─────────┐
                                       │ Student │
                                       │ "Plan   │
                                       │ updated"│
                                       └─────────┘
```

---

## Scheduling Algorithm Flow

```
START: Generate Schedule
         │
         ▼
┌────────────────────────────────┐
│ 1. Fetch Prioritized Topics    │
│    (from Mastery Engine)        │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 2. Get User Availability       │
│    • Weekly schedule            │
│    • Max hours per day          │
│    • Preferred block length     │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 3. Fetch Calendar Events       │
│    (from Google Calendar)       │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 4. Generate Available Slots    │
│    • Remove busy times          │
│    • Apply constraints          │
│    • Buffer before events       │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 5. Greedy Task Assignment      │
│    FOR each task:               │
│      FOR each slot:             │
│        Calculate score          │
│      Assign best task-slot pair │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 6. Workload Balancing          │
│    • Check daily totals         │
│    • Move tasks if overloaded   │
│    • Spread across week         │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 7. Sync to Calendar            │
│    • Create events              │
│    • Store event IDs            │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 8. Sync to Notion (Optional)   │
│    • Create/update pages        │
│    • Link to calendar           │
└────────────────────────────────┘
         │
         ▼
       END
```

---

## Mastery Update Flow

```
Performance Record (Quiz Result)
         │
         ▼
┌──────────────────────────────────┐
│  Extract Topic Scores            │
│  Topic 1: 8/10 correct           │
│  Topic 2: 6/8 correct            │
└──────────────────────────────────┘
         │
         ▼
    FOR each topic:
         │
         ▼
┌──────────────────────────────────┐
│  Get Current Mastery Record      │
│  • M_old = 65.0                  │
│  • CI = 10.0                     │
│  • Trend = stable                │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Apply EWMA Update               │
│  M_new = α × Score + (1-α) × M   │
│  M_new = 0.3 × 80 + 0.7 × 65     │
│  M_new = 69.5                    │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Update Confidence               │
│  CI_new = CI_old × 0.9           │
│  CI_new = 10.0 × 0.9 = 9.0       │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Detect Trend                    │
│  delta = 69.5 - 65 = 4.5         │
│  trend = stable (< 5 threshold)  │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Calculate Next Review           │
│  IF M >= 70: SM-2 algorithm      │
│  ELSE: review in 1 day           │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Save Updated Record             │
│  • mastery_score = 69.5          │
│  • confidence = 9.0              │
│  • trend = stable                │
│  • next_review = tomorrow        │
└──────────────────────────────────┘
         │
         ▼
    Trigger Replan
```

---

## Technology Stack Details

### Backend Stack
```
┌─────────────────────────────────────────┐
│ Application Layer                       │
│ • FastAPI 0.108.0                       │
│ • Python 3.9+                           │
│ • Pydantic (validation)                 │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Business Logic Layer                    │
│ • Custom algorithms (EWMA, SM-2, CSP)   │
│ • Service classes                       │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Data Access Layer                       │
│ • SQLAlchemy 2.0 ORM                    │
│ • Alembic (migrations)                  │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Database Layer                          │
│ • PostgreSQL 13+                        │
│ • Redis (caching & queue)               │
└─────────────────────────────────────────┘
```

### Frontend Stack (Planned)
```
┌─────────────────────────────────────────┐
│ UI Framework                            │
│ • React 18                              │
│ • TypeScript                            │
│ • Material-UI (components)              │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ State Management                        │
│ • Redux Toolkit                         │
│ • React Query (API calls)               │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Visualization                           │
│ • Recharts (analytics)                  │
│ • FullCalendar (schedule)               │
└─────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
└─────────────────────────────────────────────────────────────┘

Layer 1: Network Security
  • HTTPS/TLS encryption
  • CORS configuration
  • Rate limiting

Layer 2: Authentication
  • JWT tokens (30 min expiry)
  • Password hashing (bcrypt)
  • OAuth 2.0 (Google, Notion)

Layer 3: Authorization
  • Role-based access control
  • Resource ownership validation
  • API key permissions

Layer 4: Data Protection
  • Encrypted tokens at rest
  • Parameterized queries (SQL injection prevention)
  • Input validation (Pydantic)

Layer 5: Monitoring
  • Request logging
  • Error tracking
  • Anomaly detection
```

---

## Deployment Architecture (Production)

```
┌────────────────────────────────────────────────────────────────┐
│                         Cloud Provider                         │
│                      (AWS / GCP / Azure)                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Load Balancer (HTTPS)                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                 │
│            ┌─────────────────┴─────────────────┐              │
│            ▼                                   ▼              │
│  ┌────────────────────┐              ┌────────────────────┐  │
│  │  App Server 1      │              │  App Server 2      │  │
│  │  (FastAPI + Nginx) │              │  (FastAPI + Nginx) │  │
│  │  Docker Container  │              │  Docker Container  │  │
│  └────────────────────┘              └────────────────────┘  │
│            │                                   │              │
│            └─────────────────┬─────────────────┘              │
│                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            PostgreSQL (RDS / Cloud SQL)                  │ │
│  │            • Primary instance                            │ │
│  │            • Read replicas                               │ │
│  │            • Automated backups                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            Redis (ElastiCache / Memorystore)             │ │
│  │            • Session cache                               │ │
│  │            • Celery queue                                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            Celery Workers (Auto-scaled)                  │ │
│  │            • Background tasks                            │ │
│  │            • Scheduled jobs                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            Monitoring & Logging                          │ │
│  │            • CloudWatch / Stackdriver                    │ │
│  │            • Sentry (error tracking)                     │ │
│  │            • Grafana (metrics)                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## Module Dependencies

```
┌────────────────────────────────────────────────────────────────┐
│                     Module Dependency Graph                    │
└────────────────────────────────────────────────────────────────┘

            ┌─────────────────┐
            │  Module 1:      │
            │  Data Model     │
            └─────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Module 2: │  │Module 6: │  │Module 4: │
│Mastery   │  │Quiz      │  │Google    │
│Engine    │  │System    │  │Calendar  │
└──────────┘  └──────────┘  └──────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
            ┌─────────────────┐
            │  Module 3:      │
            │  Scheduler      │
            └─────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Module 5: │  │Module 7: │  │Module 8: │
│Notion    │  │Spaced    │  │UI/UX     │
│          │  │Rep       │  │          │
└──────────┘  └──────────┘  └──────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Module 9:      │
            │  Feedback Loop  │
            └─────────────────┘

All modules use: Module 10 (Architecture & Infrastructure)
```

---

## Performance Optimization Strategy

```
┌────────────────────────────────────────────────────────────────┐
│                   Performance Targets                          │
└────────────────────────────────────────────────────────────────┘

API Response Time:
  • GET requests: < 200ms (95th percentile)
  • POST requests: < 500ms (95th percentile)
  • Schedule generation: < 3 seconds
  • Mastery update: < 1 second

Database Queries:
  • Simple queries: < 50ms
  • Complex queries: < 100ms
  • Joins (< 3 tables): < 200ms

Optimization Techniques:
  ✓ Database indexing (8 strategic indexes)
  ✓ Query optimization (eager loading, join strategies)
  ✓ Redis caching (session data, calendar events)
  ✓ Async operations (FastAPI async/await)
  ✓ Connection pooling (10 connections, 20 overflow)
  ✓ Pagination (limit result sets)
  ✓ Background jobs (Celery for heavy operations)

Scalability:
  • Horizontal scaling (multiple app servers)
  • Database read replicas
  • CDN for static assets
  • Auto-scaling based on CPU/memory
```

---

**This architecture supports 10,000+ concurrent users with proper infrastructure scaling.**
