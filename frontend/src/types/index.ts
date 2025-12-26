export interface User {
  id: string;
  email: string;
  full_name: string;
  academic_level: string;
  created_at: string;
}

export interface Course {
  id: string;
  name: string;
  code: string;
  semester: string;
  color?: string;
  description?: string;
  is_archived: boolean;
  created_at: string;
  user_id: string;
}

export interface Topic {
  id: string;
  name: string;
  course_id: string;
  estimated_difficulty: 'easy' | 'medium' | 'hard';
  prerequisite_topic_ids?: string[];
  resource_links?: string[];
  notes?: string;
  created_at: string;
}

export interface MasteryRecord {
  id: string;
  topic_id: string;
  current_mastery: number;
  confidence_interval: number;
  trend: 'improving' | 'declining' | 'stable';
  next_review_date: string;
  total_questions_attempted: number;
  updated_at: string;
}

export interface StudyTask {
  id: string;
  user_id: string;
  course_id: string;
  topic_id?: string;
  assessment_id?: string;
  title: string;
  description?: string;
  task_type: 'study' | 'review' | 'practice' | 'exam_prep';
  priority_score: number;
  estimated_duration: number;
  scheduled_date: string;
  scheduled_start_time: string;
  scheduled_end_time: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  completion_date?: string;
  created_at: string;
}

export interface PerformanceRecord {
  id: string;
  user_id: string;
  topic_id: string;
  quiz_score: number;
  question_count: number;
  difficulty_level: 'easy' | 'medium' | 'hard';
  time_spent?: number;
  created_at: string;
}

export interface CourseMasteryOverview {
  course_id: string;
  course_name: string;
  average_mastery: number;
  topics: Array<{
    topic_id: string;
    topic_name: string;
    mastery: number;
    trend: string;
  }>;
}

export interface MasteryOverview {
  total_courses: number;
  total_topics: number;
  overall_mastery: number;
  courses: CourseMasteryOverview[];
}
