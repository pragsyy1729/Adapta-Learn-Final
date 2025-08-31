// User and Authentication Types
export interface User {
  user_id: string;
  email: string;
  profile: {
    firstName: string;
    lastName: string;
    department: string;
    role: string;
    learningStyle?: string;
    varkScores?: {
      visual: number;
      auditory: number;
      reading: number;
      kinesthetic: number;
    };
  };
  preferences?: {
    notifications: boolean;
    theme: 'light' | 'dark';
    language: string;
  };
  created_at: string;
  last_login?: string;
}

// Recommendation Types
export interface Recommendation {
  id: string;
  type: 'skill_development' | 'general' | 'compliance';
  title: string;
  description: string;
  reason?: string;
  priority: 'low' | 'medium' | 'high';
  content_id: string;
  content_type: 'learning_path' | 'module' | 'quiz';
  source: 'ai' | 'hr' | 'admin';
  assigned_by?: string;
  due_date?: string;
  confidence_score?: number;
  generated_at: string;
}

export interface RecommendationsResponse {
  recommendations: {
    ai: Recommendation[];
    hr: Recommendation[];
    admin: Recommendation[];
    all: Recommendation[];
  };
  total_count: number;
  counts_by_source: {
    ai: number;
    hr: number;
    admin: number;
  };
}

// Gamification Types
export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'achievement' | 'skill' | 'streak' | 'social';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  points_required: number;
  criteria: string;
  unlocked_at?: string;
}

export interface UserGamification {
  user_id: string;
  total_points: number;
  current_streak: number;
  longest_streak: number;
  badges_earned: any[];
  level: number;
  experience_points: number;
  last_activity: string;
  activity_history: any[];
  category_progress: Record<string, any>;
}

export interface LeaderboardEntry {
  user_id: string;
  name: string;
  department: string;
  role: string;
  total_points: number;
  score: number;
  level: number;
  current_streak: number;
  badges_count: number;
  rank?: number;
}

export interface LeaderboardResponse {
  leaderboard: LeaderboardEntry[];
  department?: string;
  timeframe: string;
  total_participants: number;
}

// Quiz and Assessment Types
export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
}

export interface Quiz {
  id: string;
  title: string;
  description: string;
  questions: QuizQuestion[];
  time_limit_minutes?: number;
  passing_score: number;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  total_questions: number;
}

export interface QuizAttempt {
  id: string;
  user_id: string;
  quiz_id: string;
  answers: Record<string, number>;
  score: number;
  passed: boolean;
  time_taken_minutes: number;
  completed_at: string;
  feedback?: string;
}

// Analytics Types
export interface UserAnalytics {
  total_modules_completed: number;
  total_quizzes_taken: number;
  average_score: number;
  total_time_spent_hours: number;
  current_streak_days: number;
  badges_earned: number;
  learning_path_progress: Record<string, number>;
  skill_gaps: string[];
  recommendations_viewed: number;
}

export interface SystemAnalytics {
  total_users: number;
  active_users_today: number;
  total_modules: number;
  total_quizzes: number;
  average_completion_rate: number;
  popular_categories: Record<string, number>;
  user_engagement_trends: Array<{
    date: string;
    active_users: number;
    completions: number;
  }>;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  department: string;
  role: string;
}

export interface RecommendationForm {
  user_id: string;
  title: string;
  description: string;
  reason?: string;
  priority: 'low' | 'medium' | 'high';
  content_id: string;
  content_type: 'learning_path' | 'module' | 'quiz';
  assigned_by: string;
  due_date?: string;
  target_audience?: string;
}

// Notification Types
export interface Notification {
  id: string;
  user_id: string;
  type: 'recommendation' | 'achievement' | 'deadline' | 'system';
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  action_url?: string;
  priority: 'low' | 'medium' | 'high';
}

export * from './learningPath';
