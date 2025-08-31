import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../utils/api';
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
  LoginForm,
  RegisterForm,
  RecommendationForm
} from '@/types';

// Authentication Hooks
export const useLogin = () => {
  return useMutation({
    mutationFn: (credentials: LoginForm) => apiClient.login(credentials),
  });
};

export const useRegister = () => {
  return useMutation({
    mutationFn: (userData: RegisterForm) => apiClient.register(userData),
  });
};

// User Management Hooks
export const useUserProfile = (userId: string) => {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => apiClient.getUserProfile(userId),
    enabled: !!userId,
  });
};

export const useUpdateUserProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, profile }: { userId: string; profile: Partial<User['profile']> }) =>
      apiClient.updateUserProfile(userId, profile),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user', variables.userId] });
    },
  });
};

// Recommendations Hooks
export const useUserRecommendations = (userId: string) => {
  return useQuery({
    queryKey: ['recommendations', userId],
    queryFn: () => apiClient.getUserRecommendations(userId),
    enabled: !!userId,
  });
};

export const useAIRecommendations = (userId: string) => {
  return useQuery({
    queryKey: ['recommendations', userId, 'ai'],
    queryFn: () => apiClient.getAIRecommendations(userId),
    enabled: !!userId,
  });
};

export const useHRRecommendations = (userId: string) => {
  return useQuery({
    queryKey: ['recommendations', userId, 'hr'],
    queryFn: () => apiClient.getHRRecommendations(userId),
    enabled: !!userId,
  });
};

export const useAdminRecommendations = (userId: string) => {
  return useQuery({
    queryKey: ['recommendations', userId, 'admin'],
    queryFn: () => apiClient.getAdminRecommendations(userId),
    enabled: !!userId,
  });
};

export const useAddHRRecommendation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (recommendation: RecommendationForm) => apiClient.addHRRecommendation(recommendation),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', variables.user_id] });
      queryClient.invalidateQueries({ queryKey: ['recommendations', variables.user_id, 'hr'] });
    },
  });
};

export const useAddAdminRecommendation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (recommendation: RecommendationForm) => apiClient.addAdminRecommendation(recommendation),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', variables.user_id] });
      queryClient.invalidateQueries({ queryKey: ['recommendations', variables.user_id, 'admin'] });
    },
  });
};

export const useGenerateAIRecommendations = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => apiClient.generateAIRecommendations(userId),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', variables] });
      queryClient.invalidateQueries({ queryKey: ['recommendations', variables, 'ai'] });
    },
  });
};

export const useTrackRecommendationInteraction = () => {
  return useMutation({
    mutationFn: ({
      userId,
      recommendationId,
      interactionType
    }: {
      userId: string;
      recommendationId: string;
      interactionType: string;
    }) => apiClient.trackRecommendationInteraction(userId, recommendationId, interactionType),
  });
};

export const useRecommendationsAnalytics = () => {
  return useQuery({
    queryKey: ['recommendations', 'analytics'],
    queryFn: () => apiClient.getRecommendationsAnalytics(),
  });
};

// Gamification Hooks
export const useUserGamification = (userId: string) => {
  return useQuery({
    queryKey: ['gamification', userId],
    queryFn: () => apiClient.getUserGamification(userId),
    enabled: !!userId,
  });
};

export const useLeaderboard = (limit: number = 50) => {
  return useQuery({
    queryKey: ['leaderboard', limit],
    queryFn: () => apiClient.getLeaderboard(limit),
  });
};

export const useAwardPoints = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, points, reason }: { userId: string; points: number; reason: string }) =>
      apiClient.awardPoints(userId, points, reason),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['gamification', variables.userId] });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
    },
  });
};

export const useCheckAndAwardBadges = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => apiClient.checkAndAwardBadges(userId),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['gamification', variables] });
    },
  });
};

// Quiz Hooks
export const useAdaptiveQuiz = (chapterId: string, userId: string) => {
  return useQuery({
    queryKey: ['quiz', chapterId, userId],
    queryFn: () => apiClient.getAdaptiveQuiz(chapterId, userId),
    enabled: !!chapterId && !!userId,
  });
};

export const useSubmitQuiz = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (attempt: {
      user_id: string;
      quiz_id: string;
      answers: Record<string, number>;
      time_taken_minutes: number;
    }) => apiClient.submitQuiz(attempt),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['quiz', 'history', variables.user_id] });
      queryClient.invalidateQueries({ queryKey: ['gamification', variables.user_id] });
    },
  });
};

export const useQuizHistory = (userId: string) => {
  return useQuery({
    queryKey: ['quiz', 'history', userId],
    queryFn: () => apiClient.getQuizHistory(userId),
    enabled: !!userId,
  });
};

// Learning Path Hooks
export const useUserLearningPaths = (userId: string) => {
  return useQuery({
    queryKey: ['learning-paths', userId],
    queryFn: () => apiClient.getUserLearningPaths(userId),
    enabled: !!userId,
  });
};

export const useEnrollInLearningPath = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, pathId }: { userId: string; pathId: string }) =>
      apiClient.enrollInLearningPath(userId, pathId),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['learning-paths', variables.userId] });
    },
  });
};

// Analytics Hooks
export const useUserAnalytics = (userId: string) => {
  return useQuery({
    queryKey: ['analytics', 'user', userId],
    queryFn: () => apiClient.getUserAnalytics(userId),
    enabled: !!userId,
  });
};

export const useSystemAnalytics = () => {
  return useQuery({
    queryKey: ['analytics', 'system'],
    queryFn: () => apiClient.getSystemAnalytics(),
  });
};

// VARK Assessment Hooks
export const useSubmitVARKAssessment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, answers }: { userId: string; answers: Record<string, number> }) =>
      apiClient.submitVARKAssessment(userId, answers),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user', variables.userId] });
    },
  });
};

export const useVARKResults = (userId: string) => {
  return useQuery({
    queryKey: ['vark', userId],
    queryFn: () => apiClient.getVARKResults(userId),
    enabled: !!userId,
  });
};
