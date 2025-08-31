import {
  User,
  Recommendation,
  RecommendationsResponse,
  UserGamification,
  LeaderboardResponse,
  Quiz,
  QuizAttempt,
  UserAnalytics,
  SystemAnalytics,
  ApiResponse,
  LoginForm,
  RegisterForm,
  RecommendationForm
} from '@/types';

const API_BASE_URL = 'http://localhost:5000/api';

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return {
        success: true,
        data: data as T,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Authentication
  async login(credentials: LoginForm): Promise<ApiResponse<{ user: User; token: string }>> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: RegisterForm): Promise<ApiResponse<{ user: User; token: string }>> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // User Management
  async getUserProfile(userId: string): Promise<ApiResponse<User>> {
    return this.request(`/user/profile/${userId}`);
  }

  async updateUserProfile(userId: string, profile: Partial<User['profile']>): Promise<ApiResponse<User>> {
    return this.request(`/user/profile/${userId}`, {
      method: 'PUT',
      body: JSON.stringify({ profile }),
    });
  }

  // Recommendations
  async getUserRecommendations(userId: string): Promise<ApiResponse<RecommendationsResponse>> {
    return this.request(`/recommendations/user/${userId}`);
  }

  async getAIRecommendations(userId: string): Promise<ApiResponse<{ recommendations: Recommendation[] }>> {
    return this.request(`/recommendations/user/${userId}/ai`);
  }

  async getHRRecommendations(userId: string): Promise<ApiResponse<{ recommendations: Recommendation[] }>> {
    return this.request(`/recommendations/user/${userId}/hr`);
  }

  async getAdminRecommendations(userId: string): Promise<ApiResponse<{ recommendations: Recommendation[] }>> {
    return this.request(`/recommendations/user/${userId}/admin`);
  }

  async addHRRecommendation(recommendation: RecommendationForm): Promise<ApiResponse<{ recommendation: Recommendation }>> {
    return this.request('/recommendations/hr/add', {
      method: 'POST',
      body: JSON.stringify(recommendation),
    });
  }

  async addAdminRecommendation(recommendation: RecommendationForm): Promise<ApiResponse<{ recommendation: Recommendation }>> {
    return this.request('/recommendations/admin/add', {
      method: 'POST',
      body: JSON.stringify(recommendation),
    });
  }

  async generateAIRecommendations(userId: string): Promise<ApiResponse<{ recommendations: Recommendation[]; count: number }>> {
    return this.request(`/recommendations/ai/generate/${userId}`, {
      method: 'POST',
    });
  }

  async trackRecommendationInteraction(
    userId: string,
    recommendationId: string,
    interactionType: string
  ): Promise<ApiResponse<any>> {
    return this.request(`/recommendations/user/${userId}/interaction/${recommendationId}`, {
      method: 'POST',
      body: JSON.stringify({ interaction_type: interactionType }),
    });
  }

  async getRecommendationsAnalytics(): Promise<ApiResponse<{
    total_recommendations: number;
    recommendations_by_source: Record<string, number>;
    users_with_recommendations: number;
  }>> {
    return this.request('/recommendations/analytics');
  }

  // Gamification
  async getUserGamification(userId: string): Promise<ApiResponse<UserGamification>> {
    const response = await fetch(`${this.baseURL}/gamification/user/${userId}/stats`);
    if (!response.ok) {
      return {
        success: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
      };
    }
    const data = await response.json();
    return {
      success: true,
      data: data as UserGamification,
    };
  }

  async getLeaderboard(limit?: number): Promise<ApiResponse<LeaderboardResponse>> {
    const params = limit ? `?limit=${limit}` : '';
    const response = await fetch(`${this.baseURL}/gamification/leaderboard${params}`);
    if (!response.ok) {
      return {
        success: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
      };
    }
    const data = await response.json();
    return {
      success: true,
      data: data as LeaderboardResponse,
    };
  }

  async awardPoints(userId: string, points: number, reason: string): Promise<ApiResponse<any>> {
    return this.request(`/gamification/user/${userId}/award-points`, {
      method: 'POST',
      body: JSON.stringify({ activity_type: 'manual_award', points, reason }),
    });
  }

  async checkAndAwardBadges(userId: string): Promise<ApiResponse<any>> {
    return this.request(`/gamification/user/${userId}/check-badges`, {
      method: 'POST',
    });
  }

  // Quiz System
  async getAdaptiveQuiz(chapterId: string, userId: string): Promise<ApiResponse<Quiz>> {
    return this.request(`/quiz/chapter/${chapterId}?user_id=${userId}`);
  }

  async submitQuiz(attempt: {
    user_id: string;
    quiz_id: string;
    answers: Record<string, number>;
    time_taken_minutes: number;
  }): Promise<ApiResponse<QuizAttempt>> {
    return this.request('/quiz/submit', {
      method: 'POST',
      body: JSON.stringify(attempt),
    });
  }

  async getQuizHistory(userId: string): Promise<ApiResponse<QuizAttempt[]>> {
    return this.request(`/quiz/history/${userId}`);
  }

  // Learning Paths
  async getUserLearningPaths(userId: string): Promise<ApiResponse<any[]>> {
    return this.request(`/user/${userId}/learning-paths`);
  }

  async enrollInLearningPath(userId: string, pathId: string): Promise<ApiResponse<any>> {
    return this.request('/enrollment/enroll', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, learning_path_id: pathId }),
    });
  }

  // Analytics
  async getUserAnalytics(userId: string): Promise<ApiResponse<UserAnalytics>> {
    return this.request(`/analytics/user/${userId}`);
  }

  async getSystemAnalytics(): Promise<ApiResponse<SystemAnalytics>> {
    return this.request('/analytics/system');
  }

  // VARK Assessment
  async submitVARKAssessment(userId: string, answers: Record<string, number>): Promise<ApiResponse<any>> {
    return this.request('/assessment/vark', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, answers }),
    });
  }

  async getVARKResults(userId: string): Promise<ApiResponse<any>> {
    return this.request(`/assessment/vark/${userId}`);
  }
}
export const apiClient = new ApiClient();

// Export individual functions for convenience
export const {
  login,
  register,
  getUserProfile,
  updateUserProfile,
  getUserRecommendations,
  getAIRecommendations,
  getHRRecommendations,
  getAdminRecommendations,
  addHRRecommendation,
  addAdminRecommendation,
  generateAIRecommendations,
  trackRecommendationInteraction,
  getRecommendationsAnalytics,
  getUserGamification,
  getLeaderboard,
  awardPoints,
  checkAndAwardBadges,
  getAdaptiveQuiz,
  submitQuiz,
  getQuizHistory,
  getUserLearningPaths,
  enrollInLearningPath,
  getUserAnalytics,
  getSystemAnalytics,
  submitVARKAssessment,
  getVARKResults,
} = apiClient;

export default apiClient;
