import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Brain, 
  Clock, 
  Trophy, 
  BookOpen, 
  Target,
  TrendingUp,
  Calendar,
  CheckCircle2,
  Loader2
} from "lucide-react";
import learningPathsImage from "@/assets/learning-paths.jpg";
import { useState, useEffect } from "react";
import SessionAnalytics from "@/components/SessionAnalytics";
import { useSessionTracking } from "@/hooks/useSessionTracking";

const Dashboard = () => {
  const [user, setUser] = useState<any>(null);
  
  // Get user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);
  
  const userId = user?.user_id || ''; // Don't use fallback user_001
  const { trackActivity } = useSessionTracking(userId);

  // Dashboard stats from backend
  const [dashboardStats, setDashboardStats] = useState<{
    modules_completed: number;
    overall_progress_percent: number;
    time_invested_minutes: number;
    quiz_average_percent: number;
  } | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [learningPaths, setLearningPaths] = useState<any[]>([]);
  const [learningPathsLoading, setLearningPathsLoading] = useState(true);
  const [learningPathsError, setLearningPathsError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [recommendationsLoading, setRecommendationsLoading] = useState(true);
  const [recommendationsError, setRecommendationsError] = useState<string | null>(null);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [assessmentsLoading, setAssessmentsLoading] = useState(true);
  const [assessmentsError, setAssessmentsError] = useState<string | null>(null);
  const [startingAssessment, setStartingAssessment] = useState<string | null>(null);

  // Transform AI recommendations into display format
  const transformAIRecommendations = (aiData: any) => {
    if (!aiData) return [];

    const recommendations = [];

    // Add priority actions as recommendations
    if (aiData.priority_actions) {
      aiData.priority_actions.forEach((action: any, index: number) => {
        recommendations.push({
          id: `priority_${index}`,
          title: action.action,
          description: action.reasoning,
          source: 'ai_priority',
          confidence_score: action.impact === 'high' ? 0.9 : action.impact === 'medium' ? 0.7 : 0.5,
          action_url: null,
          expires_at: null
        });
      });
    }

    // Add stalled path recovery recommendations
    if (aiData.stalled_paths_recovery) {
      aiData.stalled_paths_recovery.forEach((stalled: any, index: number) => {
        recommendations.push({
          id: `stalled_${index}`,
          title: `Restart ${stalled.path_id}`,
          description: stalled.recovery_strategy,
          source: 'ai_stalled',
          confidence_score: 0.8,
          action_url: null,
          expires_at: null
        });
      });
    }

    // Add deadline management recommendations
    if (aiData.deadline_management && aiData.deadline_management.urgent_deadlines) {
      recommendations.push({
        id: 'deadline_mgmt',
        title: 'Deadline Management Required',
        description: aiData.deadline_management.time_management_strategy,
        source: 'ai_deadlines',
        confidence_score: 0.9,
        action_url: null,
        expires_at: null
      });
    }

    // Add motivational support
    if (aiData.motivational_support) {
      recommendations.push({
        id: 'motivation',
        title: aiData.motivational_support.encouragement_message,
        description: aiData.motivational_support.goal_setting,
        source: 'ai_motivation',
        confidence_score: 0.6,
        action_url: null,
        expires_at: null
      });
    }

    return recommendations.slice(0, 5); // Limit to 5 recommendations
  };

  useEffect(() => {
    // Track dashboard view activity
    trackActivity('dashboard_view');

    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setStatsError("Authentication required. Please sign in.");
          setLearningPathsError("Authentication required. Please sign in.");
          setRecommendationsError("Authentication required. Please sign in.");
          setAssessmentsError("Authentication required. Please sign in.");
          setStatsLoading(false);
          setLearningPathsLoading(false);
          setRecommendationsLoading(false);
          setAssessmentsLoading(false);
          return;
        }
        // 1. Get user_id from /api/me
        const meRes = await fetch('/api/me', {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (!meRes.ok) {
          if (meRes.status === 401) {
            setStatsError("Authentication required. Please sign in again.");
            setLearningPathsError("Authentication required. Please sign in again.");
            setRecommendationsError("Authentication required. Please sign in again.");
            setAssessmentsError("Authentication required. Please sign in again.");
            // Clear invalid token
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            setStatsLoading(false);
            setLearningPathsLoading(false);
            setRecommendationsLoading(false);
            setAssessmentsLoading(false);
            return;
          } else {
            throw new Error(`Failed to get user info: ${meRes.status}`);
          }
        }
        
        const meData = await meRes.json();
        const user_id = meData?.user?.user_id;
        if (!user_id) {
          setStatsError("User information not found. Please sign in again.");
          setLearningPathsError("User information not found. Please sign in again.");
          setRecommendationsError("User information not found. Please sign in again.");
          setAssessmentsError("User information not found. Please sign in again.");
          setStatsLoading(false);
          setLearningPathsLoading(false);
          setRecommendationsLoading(false);
          setAssessmentsLoading(false);
          return;
        }
        
        // 2. Fetch dashboard stats using user_id
        const dashRes = await fetch(`/api/dashboard?user_id=${user_id}`);
        if (dashRes.ok) {
          const data = await dashRes.json();
          setDashboardStats(data);
        } else {
          const errorData = await dashRes.json().catch(() => ({}));
          setStatsError(errorData.error || `Failed to load dashboard stats (${dashRes.status})`);
        }

        // 3. Fetch learning paths with progress using user_id
        const pathsRes = await fetch(`/api/learning-paths/${user_id}`);
        if (pathsRes.ok) {
          const pathsData = await pathsRes.json();
          const formattedPaths = pathsData.assigned_learning_paths?.map((path: any) => ({
            id: path.id,
            title: path.title,
            progress: Math.round(path.progress_percent || 0),
            modules: path.modules_total_count || 0,
            completedModules: path.modules_completed_count || 0,
            timeRemaining: path.status === 'completed' ? 'Completed' : 
                          path.status === 'not_started' ? 'Not Started' :
                          `${path.duration_weeks || 'Unknown'} weeks`,
            difficulty: path.difficulty || 'Unknown',
            skills: path.tags || [],
            status: path.status,
            progressId: path.progress_id
          })) || [];
          setLearningPaths(formattedPaths);
        } else {
          const errorData = await pathsRes.json().catch(() => ({}));
          setLearningPathsError(errorData.error || `Failed to load learning paths (${pathsRes.status})`);
        }

        // 4. Fetch AI recommendations using user_id
        const recsRes = await fetch(`/api/ai-recommendations/${user_id}`);
        if (recsRes.ok) {
          const recsData = await recsRes.json();
          // Transform AI recommendations into display format
          const transformedRecs = transformAIRecommendations(recsData.data);
          setRecommendations(transformedRecs || []);
        } else {
          const errorData = await recsRes.json().catch(() => ({}));
          setRecommendationsError(errorData.error || `Failed to load AI recommendations (${recsRes.status})`);
        }

        // 5. Fetch upcoming assessments using user_id
        const assessRes = await fetch(`/api/assessments?user_id=${user_id}`);
        if (assessRes.ok) {
          const assessData = await assessRes.json();
          setAssessments(assessData || []);
        } else {
          const errorData = await assessRes.json().catch(() => ({}));
          setAssessmentsError(errorData.error || `Failed to load assessments (${assessRes.status})`);
        }
      } catch (error) {
        setStatsError("Network error loading dashboard stats");
        setLearningPathsError("Network error loading learning paths");
        setRecommendationsError("Network error loading recommendations");
        setAssessmentsError("Network error loading assessments");
      }
      setStatsLoading(false);
      setLearningPathsLoading(false);
      setRecommendationsLoading(false);
      setAssessmentsLoading(false);
    };
    fetchData();
  }, []);

  const handleContinueReview = async (pathId: string, progressId: string, currentStatus: string) => {
    if (!pathId || !progressId) {
      alert('Missing required data. Please refresh the page and try again.');
      return;
    }

    setActionLoading(pathId);
    try {
      const token = localStorage.getItem("token");
      
      // 1. Get learning path details
      const pathRes = await fetch(`/api/learning-paths/${pathId}`);
      if (!pathRes.ok) {
        throw new Error("Failed to load learning path details");
      }
      
      // 2. Update learning path progress
      const updateData = {
        status: currentStatus === 'completed' ? 'completed' : 'in_progress',
        last_accessed_at: new Date().toISOString()
      };
      
      const progressRes = await fetch(`/api/learning-path-progress/${progressId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
      });
      
      if (!progressRes.ok) {
        throw new Error("Failed to update progress");
      }
      
      // 3. Update the UI by refreshing the learning paths
      const user_id = await getCurrentUserId();
      if (user_id) {
        await refreshLearningPaths(user_id);
      }
      
      // TODO: Navigate to the learning path content page
      console.log(`${currentStatus === 'completed' ? 'Reviewing' : 'Continuing'} learning path:`, pathId);
      
      // Show success feedback (you could replace this with a toast notification)
      alert(`Successfully updated! ${currentStatus === 'completed' ? 'Review' : 'Continue'} mode activated.`);
      
    } catch (error) {
      console.error('Error handling continue/review:', error);
      alert(`Failed to ${currentStatus === 'completed' ? 'start review' : 'continue learning path'}. Please try again.`);
    } finally {
      setActionLoading(null);
    }
  };

  const getCurrentUserId = async () => {
    try {
      const token = localStorage.getItem("token");
      const meRes = await fetch('/api/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const meData = await meRes.json();
      return meData?.user?.user_id;
    } catch (error) {
      return null;
    }
  };

    const dismissRecommendation = async (recId: string) => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`/api/recommendations/${recId}/dismiss`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        }
      });
      
      if (res.ok) {
        // Remove the dismissed recommendation from the list
        setRecommendations(prev => prev.filter(rec => rec.id !== recId));
      } else {
        const errorData = await res.json();
        alert(errorData.error || "Failed to dismiss recommendation");
      }
    } catch (error) {
      alert("Network error dismissing recommendation");
    }
  };

  const startAssessment = async (assessmentId: string) => {
    setStartingAssessment(assessmentId);
    try {
      const token = localStorage.getItem("token");
      // Get user_id from /api/me first
      const meRes = await fetch('/api/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const meData = await meRes.json();
      const user_id = meData?.user?.user_id;
      
      if (!user_id) {
        alert("User not authenticated");
        return;
      }

      const res = await fetch('/api/assessment-attempts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          assessment_id: assessmentId,
          user_id: user_id
        }),
      });

      if (res.ok) {
        const data = await res.json();
        alert(`Assessment started successfully! Attempt ID: ${data.attempt?.attributes?.id || data.attempt_id}`);
        
        // Refresh assessments to update status
        const assessRes = await fetch(`/api/assessments?user_id=${user_id}`);
        if (assessRes.ok) {
          const assessData = await assessRes.json();
          setAssessments(assessData || []);
        }
      } else {
        const errorData = await res.json();
        alert(errorData.error || "Failed to start assessment");
      }
    } catch (error) {
      alert("Network error starting assessment");
    }
    setStartingAssessment(null);
  };

  const refreshLearningPaths = async (user_id: string) => {
    try {
      const pathsRes = await fetch(`/api/learning-paths/${user_id}`);
      if (pathsRes.ok) {
        const pathsData = await pathsRes.json();
        const formattedPaths = pathsData.assigned_learning_paths?.map((path: any) => ({
          id: path.id,
          title: path.title,
          progress: Math.round(path.progress_percent || 0),
          modules: path.modules_total_count || 0,
          completedModules: path.modules_completed_count || 0,
          timeRemaining: path.status === 'completed' ? 'Completed' : 
                        path.status === 'not_started' ? 'Not Started' :
                        `${path.duration_weeks || 'Unknown'} weeks`,
          difficulty: path.difficulty || 'Unknown',
          skills: path.tags || [],
          status: path.status,
          progressId: path.progress_id
        })) || [];
        setLearningPaths(formattedPaths);
      }
    } catch (error) {
      console.error('Error refreshing learning paths:', error);
    }
  };

  return (
    <section className="min-h-screen bg-gradient-to-br from-background to-muted/30 py-20">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="mb-12 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-primary bg-clip-text text-transparent">
            Your Learning Dashboard
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Track your personalized learning journey, monitor progress, and achieve your onboarding goals
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <Card className="p-6 shadow-card hover:shadow-elegant transition-smooth">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center">
                <Trophy className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {statsLoading ? "-" : dashboardStats?.modules_completed ?? "-"}
                </p>
                <p className="text-sm text-muted-foreground">Modules Completed</p>
              </div>
            </div>
          </Card>

          <Card className="p-6 shadow-card hover:shadow-elegant transition-smooth">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-learning-progress rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {statsLoading ? "-" : `${dashboardStats?.overall_progress_percent ?? "-"}%`}
                </p>
                <p className="text-sm text-muted-foreground">Overall Progress</p>
              </div>
            </div>
          </Card>

          <Card className="p-6 shadow-card hover:shadow-elegant transition-smooth">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-learning-info rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {statsLoading ? "-" : `${Math.round((dashboardStats?.time_invested_minutes ?? 0) / 60)}h`}
                </p>
                <p className="text-sm text-muted-foreground">Time Invested</p>
              </div>
            </div>
          </Card>

          <Card className="p-6 shadow-card hover:shadow-elegant transition-smooth">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-learning-warning rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {statsLoading ? "-" : `${dashboardStats?.quiz_average_percent ?? "-"}%`}
                </p>
                <p className="text-sm text-muted-foreground">Quiz Average</p>
              </div>
            </div>
          </Card>
        </div>
        {statsError && (
          <div className="text-red-600 mb-4 p-4 bg-red-50 rounded-lg border border-red-200">
            <p className="font-medium mb-2">Authentication Error</p>
            <p className="text-sm mb-3">{statsError}</p>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => window.location.href = '/signin'}
              className="bg-white hover:bg-gray-50"
            >
              Sign In Again
            </Button>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Learning Paths */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-foreground">Your Learning Paths</h3>
              <Button variant="outline" size="sm">
                View All
              </Button>
            </div>

            <div className="space-y-6">
              {learningPathsLoading ? (
                <Card className="p-6 shadow-card">
                  <div className="animate-pulse">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="h-4 bg-muted rounded w-48"></div>
                      <div className="h-5 bg-muted rounded w-20"></div>
                    </div>
                    <div className="h-3 bg-muted rounded w-32 mb-4"></div>
                    <div className="flex gap-2 mb-4">
                      <div className="h-6 bg-muted rounded w-16"></div>
                      <div className="h-6 bg-muted rounded w-20"></div>
                    </div>
                    <div className="space-y-3">
                      <div className="h-2 bg-muted rounded"></div>
                      <div className="flex gap-3">
                        <div className="h-8 bg-muted rounded flex-1"></div>
                        <div className="h-8 bg-muted rounded w-8"></div>
                      </div>
                    </div>
                  </div>
                </Card>
              ) : learningPathsError ? (
                <Card className="p-6 shadow-card">
                  <div className="text-center text-red-600">
                    <p className="font-medium mb-2">Failed to load learning paths</p>
                    <p className="text-sm mb-3">{learningPathsError}</p>
                    {learningPathsError.includes("Authentication") && (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => window.location.href = '/signin'}
                        className="bg-white hover:bg-gray-50"
                      >
                        Sign In Again
                      </Button>
                    )}
                  </div>
                </Card>
              ) : learningPaths.length === 0 ? (
                <Card className="p-6 shadow-card">
                  <div className="text-center text-muted-foreground">
                    <p className="font-medium mb-2">No learning paths enrolled</p>
                    <p className="text-sm">Contact your manager to get enrolled in learning paths.</p>
                  </div>
                </Card>
              ) : (
                learningPaths.map((path, index) => (
                  <Card key={path.id || index} className="p-6 shadow-card hover:shadow-elegant transition-smooth">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="text-lg font-semibold text-foreground">{path.title}</h4>
                          <Badge variant={path.progress === 100 ? "default" : "secondary"}>
                            {path.difficulty}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          {path.completedModules}/{path.modules} modules • {path.timeRemaining}
                        </p>
                        <div className="flex flex-wrap gap-2 mb-4">
                          {path.skills.map((skill: string, skillIndex: number) => (
                            <Badge key={skillIndex} variant="outline" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      {path.progress === 100 && (
                        <CheckCircle2 className="w-6 h-6 text-learning-success" />
                      )}
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium text-foreground">{path.progress}%</span>
                      </div>
                      <Progress value={path.progress} className="h-2" />
                      <div className="flex gap-3">
                        <Button 
                          variant="default" 
                          size="sm" 
                          className="flex-1"
                          disabled={actionLoading === path.id}
                          onClick={() => window.location.href = `/learning-path/${path.id}`}
                        >
                          {actionLoading === path.id ? (
                            <div className="flex items-center gap-2">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              Loading...
                            </div>
                          ) : (
                            path.progress === 100 ? "Review" : "Continue"
                          )}
                        </Button>
                        <Button variant="outline" size="sm">
                          <BookOpen className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* AI Recommendations */}
            <Card className="p-6 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-semibold text-foreground">AI Recommendations</h3>
              </div>
              <div className="space-y-3">
                {recommendationsLoading ? (
                  <div className="space-y-3">
                    <div className="animate-pulse">
                      <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-muted rounded w-full"></div>
                    </div>
                    <div className="animate-pulse">
                      <div className="h-4 bg-muted rounded w-2/3 mb-2"></div>
                      <div className="h-3 bg-muted rounded w-5/6"></div>
                    </div>
                  </div>
                ) : recommendationsError ? (
                  <div className="text-center text-red-600">
                    <p className="text-sm mb-2">{recommendationsError}</p>
                    {recommendationsError.includes("Authentication") && (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => window.location.href = '/signin'}
                        className="bg-white hover:bg-gray-50"
                      >
                        Sign In Again
                      </Button>
                    )}
                  </div>
                ) : recommendations.length === 0 ? (
                  <div className="text-center text-muted-foreground">
                    <p className="text-sm">No recommendations available at the moment.</p>
                  </div>
                ) : (
                  recommendations.map((rec) => (
                    <div key={rec.id} className="p-3 bg-gradient-card rounded-lg border relative group">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-sm font-medium text-foreground">{rec.title}</p>
                            {rec.source && (
                              <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                                {rec.source.replace('_', ' ')}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">{rec.description}</p>
                          <div className="flex items-center justify-between mt-2">
                            {rec.confidence_score && (
                              <span className="text-xs text-muted-foreground">
                                Confidence: {Math.round(rec.confidence_score * 100)}%
                              </span>
                            )}
                            {rec.expires_at && (
                              <span className="text-xs text-muted-foreground">
                                Expires: {new Date(rec.expires_at).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="opacity-0 group-hover:opacity-100 transition-opacity ml-2"
                          onClick={() => dismissRecommendation(rec.id)}
                        >
                          ✕
                        </Button>
                      </div>
                      {rec.action_url && (
                        <div className="mt-2">
                          <Button 
                            variant="link" 
                            size="sm" 
                            className="p-0 h-auto text-primary"
                            onClick={() => window.open(rec.action_url, '_blank')}
                          >
                            Take Action →
                          </Button>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </Card>

            {/* Upcoming Assessments */}
            <Card className="p-6 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <Calendar className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-semibold text-foreground">Upcoming Assessments</h3>
              </div>
              <div className="space-y-3">
                {assessmentsLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-gradient-card rounded-lg border">
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-muted rounded animate-pulse" />
                          <div className="h-3 bg-muted rounded animate-pulse w-2/3" />
                        </div>
                        <div className="w-16 h-8 bg-muted rounded animate-pulse" />
                      </div>
                    ))}
                  </div>
                ) : assessmentsError ? (
                  <div>
                    <p className="text-sm text-destructive mb-2">{assessmentsError}</p>
                    {assessmentsError.includes("Authentication") && (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => window.location.href = '/signin'}
                        className="bg-white hover:bg-gray-50"
                      >
                        Sign In Again
                      </Button>
                    )}
                  </div>
                ) : assessments.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No upcoming assessments</p>
                ) : (
                  assessments.map((assessment) => (
                    <div key={assessment.id} className="flex items-center justify-between p-3 bg-gradient-card rounded-lg border">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="text-sm font-medium text-foreground">{assessment.title}</p>
                          {assessment.is_locked && (
                            <Badge variant="secondary" className="text-xs">Locked</Badge>
                          )}
                          {assessment.has_in_progress && (
                            <Badge variant="outline" className="text-xs">In Progress</Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mb-1">{assessment.description}</p>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span>{assessment.points} points</span>
                          {assessment.time_limit_seconds && (
                            <span>{Math.round(assessment.time_limit_seconds / 60)} min</span>
                          )}
                          {assessment.attempts_allowed && (
                            <span>{assessment.attempts_used || 0}/{assessment.attempts_allowed} attempts</span>
                          )}
                          {assessment.due_at && (
                            <span>Due: {new Date(assessment.due_at).toLocaleDateString()}</span>
                          )}
                        </div>
                      </div>
                      <Button 
                        variant={assessment.is_locked ? "secondary" : "learning"} 
                        size="sm"
                        disabled={assessment.is_locked || startingAssessment === assessment.id}
                        onClick={() => startAssessment(assessment.id)}
                      >
                        {startingAssessment === assessment.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : assessment.has_in_progress ? (
                          "Continue"
                        ) : assessment.is_locked ? (
                          "Locked"
                        ) : (
                          "Start"
                        )}
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>
        </div>

        {/* Visual Break / Divider */}
        <div className="mb-12">
          <div className="flex items-center justify-center">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-border to-transparent"></div>
            <div className="px-4">
              <div className="w-2 h-2 rounded-full bg-border"></div>
            </div>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-border to-transparent"></div>
          </div>
        </div>

        {/* Session Analytics - only show when user is loaded */}
        {user?.user_id && (
          <div className="mb-12">
            <SessionAnalytics userId={userId} />
          </div>
        )}
      </div>
    </section>
  );
};

export default Dashboard;