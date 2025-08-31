import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ArrowLeft, BookOpen, Clock, CheckCircle, PlayCircle, Calendar, Tag } from "lucide-react";
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const UserDetailView = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [userData, setUserData] = useState<any>(null);
  const [learningPaths, setLearningPaths] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserData = async () => {
      if (!userId) return;

      try {
        setLoading(true);

        // Fetch user learning paths
        const token = localStorage.getItem("token");
        const response = await fetch(`/api/user-learning-paths/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error(`Failed to load user data: ${response.status}`);
        }

        const data = await response.json();
        setLearningPaths(data);

        // For now, we'll get basic user info from the dashboard API
        // In a real app, you'd have a dedicated user API endpoint
        const userDataString = localStorage.getItem('user');
        let currentUserId = null;
        
        if (userDataString) {
          try {
            const userObj = JSON.parse(userDataString);
            currentUserId = userObj.user_id;
          } catch (e) {
            console.error('Error parsing user data from localStorage:', e);
          }
        }
        
        if (!currentUserId) {
          throw new Error('Unable to get current user ID');
        }
        
        const dashboardResponse = await fetch(`/api/dashboard?user_id=${currentUserId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (dashboardResponse.ok) {
          const dashboardData = await dashboardResponse.json();
          // Find the user in the new_joiners array
          const user = dashboardData.new_joiners?.find((u: any) => u.user_id === userId);
          if (user) {
            setUserData(user);
          }
        }

      } catch (error) {
        console.error('Error fetching user data:', error);
        setError("Failed to load user data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [userId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'in_progress': return 'bg-blue-500';
      case 'not_started': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'in_progress': return 'In Progress';
      case 'not_started': return 'Not Started';
      default: return 'Unknown';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8 pt-24">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading user details...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8 pt-24">
          <div className="text-center text-red-600">
            <p className="font-medium mb-2">Error Loading User Data</p>
            <p className="text-sm mb-3">{error}</p>
            <Button onClick={() => navigate('/manager')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>
        </main>
      </div>
    );
  }

  if (!learningPaths || !userData) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8 pt-24">
          <div className="text-center text-muted-foreground">
            <p>No data available for this user</p>
            <Button onClick={() => navigate('/manager')} className="mt-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <main className="container mx-auto px-4 py-8 pt-24">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/manager')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>

          <div className="flex items-center space-x-4 mb-6">
            <Avatar className="w-16 h-16">
              <AvatarFallback className="text-lg">
                {userData.name.split(' ').map((n: string) => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-3xl font-bold text-foreground">{userData.name}</h1>
              <p className="text-muted-foreground">{userData.roleType}</p>
              <p className="text-sm text-muted-foreground">{userData.email}</p>
            </div>
          </div>

          {/* User Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Learning Paths</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-primary">{learningPaths.total_paths}</div>
                <p className="text-xs text-muted-foreground">Total assigned</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{learningPaths.completed_paths}</div>
                <p className="text-xs text-muted-foreground">Paths finished</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{learningPaths.in_progress_paths}</div>
                <p className="text-xs text-muted-foreground">Currently active</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Not Started</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-600">{learningPaths.not_started_paths}</div>
                <p className="text-xs text-muted-foreground">Pending start</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Learning Paths Section */}
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-2">Learning Paths Assigned</h2>
            <p className="text-muted-foreground">Detailed progress for each learning path</p>
          </div>

          {learningPaths.learning_paths.length === 0 ? (
            <Card>
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center">
                  <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No learning paths assigned</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6">
              {learningPaths.learning_paths.map((path: any) => (
                <Card key={path.learning_path_id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <CardTitle className="text-xl mb-2">{path.title}</CardTitle>
                        <CardDescription className="mb-3">{path.description}</CardDescription>

                        <div className="flex flex-wrap gap-2 mb-3">
                          <Badge className={getDifficultyColor(path.difficulty)}>
                            {path.difficulty}
                          </Badge>
                          <Badge variant="outline">
                            <Clock className="w-3 h-3 mr-1" />
                            {path.duration}
                          </Badge>
                          {path.department && (
                            <Badge variant="outline">
                              <Tag className="w-3 h-3 mr-1" />
                              {path.department}
                            </Badge>
                          )}
                        </div>

                        {path.tags && path.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {path.tags.map((tag: string) => (
                              <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>

                      <Badge className={`${getStatusColor(path.progress.status)} text-white ml-4`}>
                        {getStatusText(path.progress.status)}
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent>
                    <div className="space-y-4">
                      {/* Progress Bar */}
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Progress</span>
                          <span>{path.progress.progress_percent}%</span>
                        </div>
                        <Progress value={path.progress.progress_percent} className="h-2" />
                      </div>

                      {/* Progress Details */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <span className="text-muted-foreground block">Modules</span>
                          <p className="font-semibold text-blue-700">
                            {path.progress.modules_completed_count}/{path.progress.modules_total_count}
                          </p>
                        </div>

                        <div className="bg-green-50 p-3 rounded-lg">
                          <span className="text-muted-foreground block">Time Invested</span>
                          <p className="font-semibold text-green-700">
                            {Math.round(path.progress.time_invested_minutes / 60)}h
                          </p>
                        </div>

                        <div className="bg-purple-50 p-3 rounded-lg">
                          <span className="text-muted-foreground block">Status</span>
                          <p className="font-semibold text-purple-700">
                            {getStatusText(path.progress.status)}
                          </p>
                        </div>

                        <div className="bg-orange-50 p-3 rounded-lg">
                          <span className="text-muted-foreground block">Enrolled</span>
                          <p className="font-semibold text-orange-700">
                            {path.progress.enrolled_at ?
                              new Date(path.progress.enrolled_at).toLocaleDateString() :
                              'N/A'
                            }
                          </p>
                        </div>
                      </div>

                      {/* Additional Details */}
                      {path.progress.last_accessed_at && (
                        <div className="text-sm text-muted-foreground">
                          <span>Last accessed: {new Date(path.progress.last_accessed_at).toLocaleDateString()}</span>
                        </div>
                      )}

                      {path.progress.current_module_id && (
                        <div className="text-sm text-muted-foreground">
                          <span>Current module: {path.progress.current_module_id}</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default UserDetailView;
