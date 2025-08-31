import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Brain,
  Target,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  Calendar,
  Award,
  BookOpen,
  Users,
  Zap,
  Heart,
  Star,
  ArrowRight,
  Loader2,
  RefreshCw
} from "lucide-react";
import { useSessionTracking } from "@/hooks/useSessionTracking";

interface AIRecommendation {
  learning_pace_assessment: {
    current_pace: string;
    assessment: string;
    recommendation: string;
  };
  priority_actions: Array<{
    action: string;
    timeframe: string;
    impact: string;
    reasoning: string;
  }>;
  deadline_management: {
    urgent_deadlines: string[];
    time_management_strategy: string;
    prioritization_plan: string;
  };
  stalled_paths_recovery: Array<{
    path_id: string;
    days_stalled: number;
    recovery_strategy: string;
    motivation_tip: string;
  }>;
  skill_gap_analysis: {
    critical_gaps: string[];
    skill_development_plan: string;
    recommended_learning_activities: string[];
    time_allocation: string;
  };
  skill_development_plan: {
    focus_areas: string[];
    learning_sequence: string[];
    difficulty_progression: string;
    practice_recommendations: string[];
  };
  time_management_advice: {
    daily_study_time: string;
    session_structure: string;
    consistency_tips: string[];
    break_strategies: string;
  };
  motivational_support: {
    progress_celebration: string;
    encouragement_message: string;
    mindset_tips: string[];
    goal_setting: string;
  };
  resource_suggestions: Array<{
    resource_type: string;
    name: string;
    purpose: string;
    time_commitment: string;
  }>;
  success_prediction: {
    confidence_level: string;
    estimated_completion: string;
    key_success_factors: string[];
    potential_challenges: string[];
  };
  metadata: {
    user_id: string;
    generated_at: string;
    analysis_timestamp: string;
    ai_model: string;
  };
}

const DashboardAIRecommendationsTab = () => {
  const [user, setUser] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<AIRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Get user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const userId = user?.user_id || '';
  const { trackActivity } = useSessionTracking(userId);

  const fetchRecommendations = async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true);
    else setLoading(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Authentication required. Please sign in.");
        return;
      }

      // Get user_id from /api/me
      const meRes = await fetch('/api/me', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!meRes.ok) {
        if (meRes.status === 401) {
          setError("Authentication required. Please sign in again.");
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          return;
        } else {
          throw new Error(`Failed to get user info: ${meRes.status}`);
        }
      }

      const meData = await meRes.json();
      const user_id = meData?.user?.user_id;
      if (!user_id) {
        setError("User information not found. Please sign in again.");
        return;
      }

      // Fetch AI recommendations
      const recsRes = await fetch(`/api/ai-recommendations/${user_id}`);
      if (recsRes.ok) {
        const recsData = await recsRes.json();
        setRecommendations(recsData.data);
        setError(null);
      } else {
        const errorData = await recsRes.json().catch(() => ({}));
        setError(errorData.error || `Failed to load AI recommendations (${recsRes.status})`);
      }
    } catch (error) {
      setError("Network error loading AI recommendations");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchRecommendations();
      trackActivity('ai_recommendations_view');
    }
  }, [userId]);

  const getPaceColor = (pace: string) => {
    switch (pace) {
      case 'too_slow': return 'text-red-600 bg-red-50 border-red-200';
      case 'optimal': return 'text-green-600 bg-green-50 border-green-200';
      case 'too_fast': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-700 bg-red-100';
      case 'medium': return 'text-yellow-700 bg-yellow-100';
      case 'low': return 'text-green-700 bg-green-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Analyzing Your Learning Journey</h3>
          <p className="text-muted-foreground">AI is generating personalized recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <Card className="p-8 text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Unable to Load Recommendations</h3>
          <p className="text-muted-foreground mb-4">{error}</p>
          {error.includes("Authentication") && (
            <Button onClick={() => window.location.href = '/signin'}>
              Sign In Again
            </Button>
          )}
        </Card>
      </div>
    );
  }

  if (!recommendations) {
    return (
      <div className="space-y-8">
        <Card className="p-8 text-center">
          <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No Recommendations Available</h3>
          <p className="text-muted-foreground">Complete some learning activities to get personalized AI recommendations.</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Brain className="w-8 h-8 text-primary" />
          <h2 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            AI Learning Recommendations
          </h2>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Personalized insights and actionable recommendations to accelerate your learning journey
        </p>
        <div className="flex items-center justify-center gap-4 mt-4">
          <Badge variant="outline" className="text-xs">
            Generated: {new Date(recommendations.metadata.generated_at).toLocaleString()}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchRecommendations(true)}
            disabled={refreshing}
          >
            {refreshing ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <RefreshCw className="w-4 h-4 mr-2" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Learning Pace Assessment */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-primary" />
            <CardTitle>Learning Pace Assessment</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className={`p-4 rounded-lg border ${getPaceColor(recommendations.learning_pace_assessment.current_pace)}`}>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="font-medium">
                {recommendations.learning_pace_assessment.current_pace.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
            <p className="text-sm font-medium mb-2">{recommendations.learning_pace_assessment.assessment}</p>
            <p className="text-sm">{recommendations.learning_pace_assessment.recommendation}</p>
          </div>
        </CardContent>
      </Card>

      {/* Priority Actions */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Target className="w-6 h-6 text-primary" />
            <CardTitle>Priority Actions</CardTitle>
            <Badge variant="secondary">{recommendations.priority_actions.length} actions</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recommendations.priority_actions.map((action, index) => (
              <div key={index} className="p-4 bg-gradient-card rounded-lg border">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className={getImpactColor(action.impact)}>
                        {action.impact.toUpperCase()} IMPACT
                      </Badge>
                      <Badge variant="outline">{action.timeframe}</Badge>
                    </div>
                    <p className="font-medium text-foreground mb-2">{action.action}</p>
                    <p className="text-sm text-muted-foreground">{action.reasoning}</p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-muted-foreground flex-shrink-0 ml-4" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Deadline Management */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6 text-primary" />
            <CardTitle>Deadline Management</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {recommendations.deadline_management.urgent_deadlines.length > 0 && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <h4 className="font-medium text-red-800 mb-2">🚨 Urgent Deadlines</h4>
              <ul className="text-sm text-red-700 space-y-1">
                {recommendations.deadline_management.urgent_deadlines.map((deadline, index) => (
                  <li key={index}>• {deadline}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">⏰ Time Management Strategy</h4>
              <p className="text-sm text-blue-700">{recommendations.deadline_management.time_management_strategy}</p>
            </div>

            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-medium text-green-800 mb-2">📋 Prioritization Plan</h4>
              <p className="text-sm text-green-700">{recommendations.deadline_management.prioritization_plan}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stalled Paths Recovery */}
      {recommendations.stalled_paths_recovery.length > 0 && (
        <Card className="shadow-card hover:shadow-elegant transition-smooth">
          <CardHeader>
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-6 h-6 text-orange-500" />
              <CardTitle>Stalled Learning Paths</CardTitle>
              <Badge variant="destructive">{recommendations.stalled_paths_recovery.length} stalled</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recommendations.stalled_paths_recovery.map((stalled, index) => (
                <div key={index} className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="destructive">{stalled.days_stalled} days stalled</Badge>
                        <span className="font-medium text-orange-800">{stalled.path_id}</span>
                      </div>
                      <p className="text-sm font-medium text-orange-800 mb-2">{stalled.recovery_strategy}</p>
                      <p className="text-sm text-orange-700 italic">💡 {stalled.motivation_tip}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Skill Gap Analysis */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Lightbulb className="w-6 h-6 text-yellow-500" />
            <CardTitle>Skill Gap Analysis</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {recommendations.skill_gap_analysis.critical_gaps.length > 0 && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-medium text-yellow-800 mb-2">🎯 Critical Gaps to Address</h4>
              <div className="flex flex-wrap gap-2">
                {recommendations.skill_gap_analysis.critical_gaps.map((gap, index) => (
                  <Badge key={index} variant="outline" className="text-yellow-700 border-yellow-300">
                    {gap}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <h4 className="font-medium text-purple-800 mb-2">📚 Skill Development Plan</h4>
              <p className="text-sm text-purple-700">{recommendations.skill_gap_analysis.skill_development_plan}</p>
            </div>

            <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
              <h4 className="font-medium text-indigo-800 mb-2">⏱️ Time Allocation</h4>
              <p className="text-sm text-indigo-700">{recommendations.skill_gap_analysis.time_allocation}</p>
            </div>
          </div>

          {recommendations.skill_gap_analysis.recommended_learning_activities.length > 0 && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-medium text-green-800 mb-2">✅ Recommended Activities</h4>
              <ul className="text-sm text-green-700 space-y-1">
                {recommendations.skill_gap_analysis.recommended_learning_activities.map((activity, index) => (
                  <li key={index}>• {activity}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skill Development Plan */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Award className="w-6 h-6 text-primary" />
            <CardTitle>Skill Development Plan</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gradient-card rounded-lg border">
              <h4 className="font-medium text-foreground mb-2">🎯 Focus Areas</h4>
              <div className="flex flex-wrap gap-2">
                {recommendations.skill_development_plan.focus_areas.map((area, index) => (
                  <Badge key={index} variant="default">{area}</Badge>
                ))}
              </div>
            </div>

            <div className="p-4 bg-gradient-card rounded-lg border">
              <h4 className="font-medium text-foreground mb-2">📈 Difficulty Progression</h4>
              <p className="text-sm text-muted-foreground">{recommendations.skill_development_plan.difficulty_progression}</p>
            </div>
          </div>

          <div className="p-4 bg-gradient-card rounded-lg border">
            <h4 className="font-medium text-foreground mb-2">📋 Learning Sequence</h4>
            <ol className="text-sm text-muted-foreground space-y-1">
              {recommendations.skill_development_plan.learning_sequence.map((step, index) => (
                <li key={index}>{index + 1}. {step}</li>
              ))}
            </ol>
          </div>

          {recommendations.skill_development_plan.practice_recommendations.length > 0 && (
            <div className="p-4 bg-gradient-card rounded-lg border">
              <h4 className="font-medium text-foreground mb-2">💪 Practice Recommendations</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                {recommendations.skill_development_plan.practice_recommendations.map((rec, index) => (
                  <li key={index}>• {rec}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Time Management Advice */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-primary" />
            <CardTitle>Time Management Advice</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">📅 Daily Study Time</h4>
              <p className="text-sm text-blue-700">{recommendations.time_management_advice.daily_study_time}</p>
            </div>

            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-medium text-green-800 mb-2">🏗️ Session Structure</h4>
              <p className="text-sm text-green-700">{recommendations.time_management_advice.session_structure}</p>
            </div>
          </div>

          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h4 className="font-medium text-purple-800 mb-2">🔄 Consistency Tips</h4>
            <ul className="text-sm text-purple-700 space-y-1">
              {recommendations.time_management_advice.consistency_tips.map((tip, index) => (
                <li key={index}>• {tip}</li>
              ))}
            </ul>
          </div>

          <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <h4 className="font-medium text-orange-800 mb-2">⏸️ Break Strategies</h4>
            <p className="text-sm text-orange-700">{recommendations.time_management_advice.break_strategies}</p>
          </div>
        </CardContent>
      </Card>

      {/* Motivational Support */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Heart className="w-6 h-6 text-pink-500" />
            <CardTitle>Motivational Support</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-pink-50 border border-pink-200 rounded-lg">
            <h4 className="font-medium text-pink-800 mb-2">🎉 Progress Celebration</h4>
            <p className="text-sm text-pink-700">{recommendations.motivational_support.progress_celebration}</p>
          </div>

          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h4 className="font-medium text-purple-800 mb-2">💪 Encouragement Message</h4>
            <p className="text-sm text-purple-700">{recommendations.motivational_support.encouragement_message}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">🧠 Mindset Tips</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                {recommendations.motivational_support.mindset_tips.map((tip, index) => (
                  <li key={index}>• {tip}</li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-medium text-green-800 mb-2">🎯 Goal Setting</h4>
              <p className="text-sm text-green-700">{recommendations.motivational_support.goal_setting}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resource Suggestions */}
      {recommendations.resource_suggestions.length > 0 && (
        <Card className="shadow-card hover:shadow-elegant transition-smooth">
          <CardHeader>
            <div className="flex items-center gap-3">
              <BookOpen className="w-6 h-6 text-primary" />
              <CardTitle>Resource Suggestions</CardTitle>
              <Badge variant="secondary">{recommendations.resource_suggestions.length} resources</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.resource_suggestions.map((resource, index) => (
                <div key={index} className="p-4 bg-gradient-card rounded-lg border">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">{resource.resource_type}</Badge>
                      </div>
                      <h4 className="font-medium text-foreground mb-1">{resource.name}</h4>
                      <p className="text-sm text-muted-foreground mb-2">{resource.purpose}</p>
                      <Badge variant="secondary" className="text-xs">
                        {resource.time_commitment}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Prediction */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Star className="w-6 h-6 text-yellow-500" />
            <CardTitle>Success Prediction</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gradient-card rounded-lg border">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium text-muted-foreground">Confidence Level:</span>
                <Badge className={getConfidenceColor(recommendations.success_prediction.confidence_level)}>
                  {recommendations.success_prediction.confidence_level.toUpperCase()}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{recommendations.success_prediction.estimated_completion}</p>
            </div>

            <div className="p-4 bg-gradient-card rounded-lg border">
              <h4 className="font-medium text-foreground mb-2">🎯 Key Success Factors</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                {recommendations.success_prediction.key_success_factors.map((factor, index) => (
                  <li key={index}>• {factor}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h4 className="font-medium text-red-800 mb-2">⚠️ Potential Challenges</h4>
            <ul className="text-sm text-red-700 space-y-1">
              {recommendations.success_prediction.potential_challenges.map((challenge, index) => (
                <li key={index}>• {challenge}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center py-8">
        <Separator className="mb-4" />
        <p className="text-sm text-muted-foreground">
          AI-generated recommendations based on your learning progress and skill gaps.
          These insights are updated regularly to help you succeed in your learning journey.
        </p>
      </div>
    </div>
  );
};

export default DashboardAIRecommendationsTab;
