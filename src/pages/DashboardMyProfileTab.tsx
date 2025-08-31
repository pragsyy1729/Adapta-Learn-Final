import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Award,
  TrendingUp,
  Target,
  BookOpen,
  Clock,
  BarChart3,
  PieChart,
  Activity,
  Zap,
  Star,
  Trophy,
  Loader2,
  RefreshCw
} from "lucide-react";
import { useSessionTracking } from "@/hooks/useSessionTracking";

interface UserProfile {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  department: string;
  role: string;
  profile?: {
    phone?: string;
    location?: string;
    join_date?: string;
    manager?: string;
    skills?: string[];
    certifications?: string[];
  };
}

interface SkillGapData {
  skill: string;
  current_level: number;
  required_level: number;
  gap_score: number;
  progress_percentage: number;
  estimated_completion: string;
}

interface LearningPathProgress {
  path_id: string;
  path_title: string;
  progress_percentage: number;
  modules_completed: number;
  total_modules: number;
  time_spent_hours: number;
  learning_rate: number; // modules per day
  last_activity: string;
  status: string;
}

interface LearningRateData {
  date: string;
  modules_completed: number;
  time_spent: number;
  learning_rate: number;
}

const DashboardMyProfileTab = () => {
  const [user, setUser] = useState<any>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [skillGaps, setSkillGaps] = useState<SkillGapData[]>([]);
  const [learningPaths, setLearningPaths] = useState<LearningPathProgress[]>([]);
  const [learningRateData, setLearningRateData] = useState<LearningRateData[]>([]);
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

  const fetchProfileData = async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true);
    else setLoading(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Authentication required. Please sign in.");
        return;
      }

      // Get user profile data
      const profileRes = await fetch(`/api/user/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setProfile(profileData);
      } else {
        const errorData = await profileRes.json().catch(() => ({}));
        setError(errorData.error || `Failed to load profile (${profileRes.status})`);
      }

      // Get skill gap analysis
      const skillGapRes = await fetch(`/api/user/${userId}/skill-gaps`);
      if (skillGapRes.ok) {
        const skillGapData = await skillGapRes.json();
        setSkillGaps(skillGapData || []);
      }

      // Get learning paths progress
      const pathsRes = await fetch(`/api/learning-paths/${userId}`);
      if (pathsRes.ok) {
        const pathsData = await pathsRes.json();
        const formattedPaths = (pathsData.assigned_learning_paths || []).map((path: any) => ({
          path_id: path.id,
          path_title: path.title,
          progress_percentage: Math.round(path.progress_percent || 0),
          modules_completed: path.modules_completed_count || 0,
          total_modules: path.modules_total_count || 0,
          time_spent_hours: Math.round((path.time_spent_minutes || 0) / 60),
          learning_rate: path.learning_rate || 0,
          last_activity: path.last_accessed_at || path.created_at,
          status: path.status
        }));
        setLearningPaths(formattedPaths);
      }

      // Get learning rate data for graphs
      const rateRes = await fetch(`/api/user/${userId}/learning-rate-data`);
      if (rateRes.ok) {
        const rateData = await rateRes.json();
        setLearningRateData(rateData || []);
      }

      setError(null);
    } catch (error) {
      setError("Network error loading profile data");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchProfileData();
      trackActivity('profile_view');
    }
  }, [userId]);

  const getSkillLevelColor = (level: number) => {
    if (level >= 4) return 'text-green-600 bg-green-50 border-green-200';
    if (level >= 3) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (level >= 2) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getSkillLevelName = (level: number) => {
    if (level >= 4) return 'Expert';
    if (level >= 3) return 'Advanced';
    if (level >= 2) return 'Intermediate';
    return 'Beginner';
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 60) return 'bg-blue-500';
    if (progress >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-700 bg-green-100';
      case 'in_progress': return 'text-blue-700 bg-blue-100';
      case 'not_started': return 'text-gray-700 bg-gray-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Loading Your Profile</h3>
          <p className="text-muted-foreground">Fetching your learning data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <Card className="p-8 text-center">
          <User className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Unable to Load Profile</h3>
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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <User className="w-8 h-8 text-primary" />
          <h2 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            My Profile
          </h2>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Your learning journey overview, skill development progress, and performance analytics
        </p>
        <div className="flex items-center justify-center gap-4 mt-4">
          <Badge variant="outline" className="text-xs">
            Last Updated: {new Date().toLocaleString()}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchProfileData(true)}
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

      {/* Basic Profile Information */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <User className="w-6 h-6 text-primary" />
            <CardTitle>Profile Information</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="flex items-center gap-3 p-4 bg-gradient-card rounded-lg border">
              <Mail className="w-5 h-5 text-primary" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Email</p>
                <p className="text-sm font-semibold text-foreground">{profile?.email || 'Not provided'}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-gradient-card rounded-lg border">
              <User className="w-5 h-5 text-primary" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Full Name</p>
                <p className="text-sm font-semibold text-foreground">
                  {profile?.first_name || ''} {profile?.last_name || ''}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-gradient-card rounded-lg border">
              <MapPin className="w-5 h-5 text-primary" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Department</p>
                <p className="text-sm font-semibold text-foreground">{profile?.department || 'Not assigned'}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-gradient-card rounded-lg border">
              <Award className="w-5 h-5 text-primary" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Role</p>
                <p className="text-sm font-semibold text-foreground">{profile?.role || 'Not assigned'}</p>
              </div>
            </div>

            {profile?.profile?.phone && (
              <div className="flex items-center gap-3 p-4 bg-gradient-card rounded-lg border">
                <Phone className="w-5 h-5 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Phone</p>
                  <p className="text-sm font-semibold text-foreground">{profile.profile.phone}</p>
                </div>
              </div>
            )}

            {profile?.profile?.join_date && (
              <div className="flex items-center gap-3 p-4 bg-gradient-card rounded-lg border">
                <Calendar className="w-5 h-5 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Join Date</p>
                  <p className="text-sm font-semibold text-foreground">
                    {new Date(profile.profile.join_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            )}
          </div>

          {profile?.profile?.skills && profile.profile.skills.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-muted-foreground mb-3">Skills</h4>
              <div className="flex flex-wrap gap-2">
                {profile.profile.skills.map((skill, index) => (
                  <Badge key={index} variant="secondary">{skill}</Badge>
                ))}
              </div>
            </div>
          )}

          {profile?.profile?.certifications && profile.profile.certifications.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-muted-foreground mb-3">Certifications</h4>
              <div className="flex flex-wrap gap-2">
                {profile.profile.certifications.map((cert, index) => (
                  <Badge key={index} variant="outline" className="text-green-700 border-green-300">
                    <Trophy className="w-3 h-3 mr-1" />
                    {cert}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skill Gap Analysis */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Target className="w-6 h-6 text-primary" />
            <CardTitle>Skill Gap Analysis</CardTitle>
            <Badge variant="secondary">{skillGaps.length} skills analyzed</Badge>
          </div>
          <CardDescription>
            Your current skill levels compared to expert requirements
          </CardDescription>
        </CardHeader>
        <CardContent>
          {skillGaps.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No skill gap data available</p>
            </div>
          ) : (
            <div className="space-y-6">
              {skillGaps.map((skill, index) => (
                <div key={index} className="p-6 bg-gradient-card rounded-lg border">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-semibold text-foreground">{skill.skill}</h4>
                        <Badge className={getSkillLevelColor(skill.current_level)}>
                          Current: {getSkillLevelName(skill.current_level)}
                        </Badge>
                        <Badge variant="outline" className="text-blue-700 border-blue-300">
                          Target: {getSkillLevelName(skill.required_level)}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        Gap Score: {skill.gap_score.toFixed(2)} •
                        Estimated Completion: {skill.estimated_completion}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Progress to Expert Level</span>
                      <span className="font-medium text-foreground">{skill.progress_percentage}%</span>
                    </div>
                    <Progress
                      value={skill.progress_percentage}
                      className="h-3"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Current Level {skill.current_level}</span>
                      <span>Expert Level {skill.required_level}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Learning Paths Progress */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-primary" />
            <CardTitle>Learning Paths Progress</CardTitle>
            <Badge variant="secondary">{learningPaths.length} paths</Badge>
          </div>
          <CardDescription>
            Your progress across all enrolled learning paths
          </CardDescription>
        </CardHeader>
        <CardContent>
          {learningPaths.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No learning paths enrolled</p>
            </div>
          ) : (
            <div className="space-y-6">
              {learningPaths.map((path, index) => (
                <div key={index} className="p-6 bg-gradient-card rounded-lg border">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-semibold text-foreground">{path.path_title}</h4>
                        <Badge className={getStatusColor(path.status)}>
                          {path.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Modules</p>
                          <p className="font-semibold text-foreground">
                            {path.modules_completed}/{path.total_modules}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Time Spent</p>
                          <p className="font-semibold text-foreground">{path.time_spent_hours}h</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Learning Rate</p>
                          <p className="font-semibold text-foreground">{path.learning_rate.toFixed(1)} modules/day</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Last Activity</p>
                          <p className="font-semibold text-foreground">
                            {new Date(path.last_activity).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Overall Progress</span>
                      <span className="font-medium text-foreground">{path.progress_percentage}%</span>
                    </div>
                    <Progress
                      value={path.progress_percentage}
                      className="h-3"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Learning Rate Analytics */}
      <Card className="shadow-card hover:shadow-elegant transition-smooth">
        <CardHeader>
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-primary" />
            <CardTitle>Learning Rate Analytics</CardTitle>
          </div>
          <CardDescription>
            Your learning velocity and progress trends over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          {learningRateData.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No learning rate data available</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Simple bar chart representation */}
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-muted-foreground">Daily Learning Rate (Modules/Day)</h4>
                <div className="space-y-2">
                  {learningRateData.slice(-7).map((data, index) => (
                    <div key={index} className="flex items-center gap-4">
                      <div className="w-20 text-xs text-muted-foreground">
                        {new Date(data.date).toLocaleDateString()}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-6">
                            <div
                              className="bg-primary h-6 rounded-full transition-all duration-300"
                              style={{ width: `${Math.min(data.learning_rate * 20, 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-foreground w-12 text-right">
                            {data.learning_rate.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Summary Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 border-t">
                <div className="text-center p-4 bg-gradient-card rounded-lg border">
                  <Activity className="w-8 h-8 text-primary mx-auto mb-2" />
                  <p className="text-2xl font-bold text-foreground">
                    {learningRateData.length > 0 ?
                      (learningRateData.reduce((sum, d) => sum + d.learning_rate, 0) / learningRateData.length).toFixed(1)
                      : '0.0'
                    }
                  </p>
                  <p className="text-sm text-muted-foreground">Avg Learning Rate</p>
                </div>

                <div className="text-center p-4 bg-gradient-card rounded-lg border">
                  <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-foreground">
                    {learningRateData.length > 0 ?
                      Math.max(...learningRateData.map(d => d.learning_rate)).toFixed(1)
                      : '0.0'
                    }
                  </p>
                  <p className="text-sm text-muted-foreground">Peak Rate</p>
                </div>

                <div className="text-center p-4 bg-gradient-card rounded-lg border">
                  <Clock className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-foreground">
                    {learningRateData.length > 0 ?
                      learningRateData.reduce((sum, d) => sum + d.time_spent, 0)
                      : 0
                    }h
                  </p>
                  <p className="text-sm text-muted-foreground">Total Study Time</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center py-8">
        <Separator className="mb-4" />
        <p className="text-sm text-muted-foreground">
          Your profile data is updated regularly to reflect your latest learning achievements and skill development.
        </p>
      </div>
    </div>
  );
};

export default DashboardMyProfileTab;
