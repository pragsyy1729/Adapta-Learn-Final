import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Users, TrendingUp, Clock, Award, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const ManagerView = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const navigate = useNavigate();

  // Get user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      
      // Check if user has manager role
      if (parsedUser?.roleType !== 'Manager') {
        setError("Access denied. This page is only accessible to managers.");
        return;
      }
    }
  }, []);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!user?.user_id) return;

      try {
        setLoading(true);
        const token = localStorage.getItem("token");
        if (!token) {
          setError("Authentication required. Please sign in.");
          return;
        }

        const response = await fetch(`/api/dashboard?user_id=${user.user_id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          if (response.status === 401) {
            setError("Authentication required. Please sign in again.");
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            return;
          } else {
            throw new Error(`Failed to load dashboard: ${response.status}`);
          }
        }

        const data = await response.json();
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError("Failed to load dashboard data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    if (user?.user_id) {
      fetchDashboardData();
    }
  }, [user?.user_id]);

  const getStatusColor = (progress: number) => {
    if (progress >= 80) return "bg-learning-success";
    if (progress >= 60) return "bg-learning-info";
    if (progress >= 40) return "bg-learning-warning";
    return "bg-destructive";
  };

  const getStatusText = (progress: number) => {
    if (progress >= 80) return "Excellent";
    if (progress >= 60) return "Good";
    if (progress >= 40) return "Needs Attention";
    return "Critical";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8 pt-24">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
              <p className="text-muted-foreground">Loading dashboard...</p>
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
            <p className="font-medium mb-2">Access Denied</p>
            <p className="text-sm mb-3">{error}</p>
            <div className="flex gap-2 justify-center">
              <Button 
                variant="outline" 
                onClick={() => window.location.href = '/dashboard'}
              >
                Go to Dashboard
              </Button>
              <Button 
                variant="outline" 
                onClick={() => window.location.href = '/signin'}
              >
                Sign In Again
              </Button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8 pt-24">
          <div className="text-center text-muted-foreground">
            <p>No dashboard data available</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Team Performance Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor and support your new team members' learning progress
            {dashboardData.department && ` in ${dashboardData.department}`}
          </p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Team Members</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.team_size || 0}</div>
              <p className="text-xs text-muted-foreground">Active team members</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">New Joiners</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.new_joiners_count || 0}</div>
              <p className="text-xs text-muted-foreground">Currently onboarding</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">New Joiners Progress</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.average_new_joiner_progress || 0}%</div>
              <p className="text-xs text-muted-foreground">Average onboarding progress</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Onboarding Completion</CardTitle>
              <Award className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.new_joiners_completion_rate || 0}%</div>
              <p className="text-xs text-muted-foreground">New joiners at 80%+</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Team Overview</TabsTrigger>
            <TabsTrigger value="new-joiners">New Joiners Progress</TabsTrigger>
            <TabsTrigger value="detailed">Detailed Progress</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {dashboardData.new_joiners?.map((member: any) => (
                <Card key={member.user_id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center space-x-4">
                      <Avatar>
                        <AvatarImage src="" />
                        <AvatarFallback>{member.name.split(' ').map((n: string) => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <CardTitle className="text-lg">{member.name}</CardTitle>
                        <CardDescription>{member.roleType}</CardDescription>
                      </div>
                      <Badge className={`${getStatusColor(member.progress?.overall_progress_percent || 0)} text-white`}>
                        {getStatusText(member.progress?.overall_progress_percent || 0)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Overall Progress</span>
                        <span>{member.progress?.overall_progress_percent || 0}%</span>
                      </div>
                      <Progress value={member.progress?.overall_progress_percent || 0} className="h-2" />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Completed</span>
                        <p className="font-semibold">{member.progress?.modules_completed || 0}/{member.progress?.total_modules || 0}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Time Spent</span>
                        <p className="font-semibold">{Math.round((member.progress?.time_invested_minutes || 0) / 60)}h</p>
                      </div>
                    </div>
                    
                    {member.newJoiner === 'Yes' && (
                      <Badge variant="outline" className="w-full justify-center">
                        New Joiner
                      </Badge>
                    )}
                    
                    <Button variant="outline" className="w-full" onClick={() => {
                      navigate(`/manager/user/${member.user_id}`);
                    }}>
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              )) || []}
            </div>
          </TabsContent>

          <TabsContent value="new-joiners" className="space-y-6">
            {/* New Joiners Summary KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Total New Joiners</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dashboardData.new_joiners?.length || 0}</div>
                  <p className="text-xs text-muted-foreground">Active onboarding</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Avg. Progress</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {dashboardData.new_joiners?.length > 0 
                      ? Math.round(dashboardData.new_joiners.reduce((sum: number, joiner: any) => 
                          sum + (joiner.progress?.overall_progress_percent || 0), 0) / dashboardData.new_joiners.length)
                      : 0}%
                  </div>
                  <p className="text-xs text-muted-foreground">Across all new joiners</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Onboarding Complete</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {dashboardData.new_joiners?.filter((joiner: any) => 
                      (joiner.progress?.overall_progress_percent || 0) >= 80).length || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">80%+ completion rate</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">At Risk</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">
                    {dashboardData.new_joiners?.filter((joiner: any) => {
                      const joinDate = new Date(joiner.dateOfJoining);
                      const today = new Date();
                      const daysSinceJoining = Math.floor((today.getTime() - joinDate.getTime()) / (1000 * 60 * 60 * 24));
                      const progressPercent = joiner.progress?.overall_progress_percent || 0;
                      return progressPercent < 30 && daysSinceJoining > 7;
                    }).length || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">Need attention</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>New Joiners Progress</CardTitle>
                <CardDescription>Detailed view of onboarding progress for new team members</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.new_joiners?.map((joiner: any) => {
                    const joinDate = new Date(joiner.dateOfJoining);
                    const today = new Date();
                    const daysSinceJoining = Math.floor((today.getTime() - joinDate.getTime()) / (1000 * 60 * 60 * 24));
                    const lastAccessed = joiner.progress?.last_accessed_at ? new Date(joiner.progress.last_accessed_at) : null;
                    const daysSinceLastAccess = lastAccessed ? Math.floor((today.getTime() - lastAccessed.getTime()) / (1000 * 60 * 60 * 24)) : null;
                    
                    // Calculate expected completion (assuming 30-day onboarding period)
                    const expectedCompletionDate = new Date(joinDate);
                    expectedCompletionDate.setDate(expectedCompletionDate.getDate() + 30);
                    const daysToExpectedCompletion = Math.floor((expectedCompletionDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
                    
                    // Risk assessment
                    const progressPercent = joiner.progress?.overall_progress_percent || 0;
                    const isAtRisk = progressPercent < 30 && daysSinceJoining > 7;
                    const isBehindSchedule = progressPercent < (daysSinceJoining / 30) * 100;
                    
                    return (
                      <div key={joiner.user_id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-center mb-3">
                          <div className="flex items-center space-x-3">
                            <Avatar className="w-10 h-10">
                              <AvatarFallback>
                                {joiner.name.split(' ').map((n: string) => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <h4 className="font-semibold">{joiner.name}</h4>
                              <p className="text-sm text-muted-foreground">{joiner.roleType}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge className={`${getStatusColor(progressPercent)} text-white`}>
                              {progressPercent}% Complete
                            </Badge>
                            {isAtRisk && (
                              <Badge variant="destructive" className="ml-2">
                                At Risk
                              </Badge>
                            )}
                            <p className="text-xs text-muted-foreground mt-1">
                              Joined: {joinDate.toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span>Onboarding Progress</span>
                              <span>{progressPercent}%</span>
                            </div>
                            <Progress value={progressPercent} className="h-2" />
                          </div>
                          
                          {/* Enhanced KPIs Grid */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div className="bg-blue-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Days Since Joining</span>
                              <p className="font-semibold text-blue-700">{daysSinceJoining} days</p>
                            </div>
                            <div className="bg-green-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Modules Done</span>
                              <p className="font-semibold text-green-700">{joiner.progress?.modules_completed || 0}/{joiner.progress?.total_modules || 0}</p>
                            </div>
                            <div className="bg-purple-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Time Invested</span>
                              <p className="font-semibold text-purple-700">{Math.round((joiner.progress?.time_invested_minutes || 0) / 60)}h</p>
                            </div>
                            <div className="bg-orange-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Quiz Average</span>
                              <p className="font-semibold text-orange-700">{joiner.progress?.quiz_average_percent || 0}%</p>
                            </div>
                          </div>
                          
                          {/* Additional KPIs Row */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div className="bg-indigo-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Last Accessed</span>
                              <p className="font-semibold text-indigo-700">
                                {daysSinceLastAccess !== null ? `${daysSinceLastAccess} days ago` : 'Never'}
                              </p>
                            </div>
                            <div className="bg-teal-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Days to Complete</span>
                              <p className="font-semibold text-teal-700">
                                {daysToExpectedCompletion > 0 ? `${daysToExpectedCompletion} days` : 'Overdue'}
                              </p>
                            </div>
                            <div className="bg-pink-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Badges Earned</span>
                              <p className="font-semibold text-pink-700">{joiner.badges_count || 0}</p>
                            </div>
                            <div className="bg-yellow-50 p-3 rounded-lg">
                              <span className="text-muted-foreground block">Learning Style</span>
                              <p className="font-semibold text-yellow-700">{joiner.learner_type || 'Unknown'}</p>
                            </div>
                          </div>
                          
                          {/* Risk Indicators */}
                          {(isAtRisk || isBehindSchedule || daysSinceLastAccess > 7) && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                              <h5 className="font-semibold text-red-800 mb-2">⚠️ Attention Required</h5>
                              <div className="space-y-1 text-sm text-red-700">
                                {isAtRisk && <p>• Low progress despite being onboard for {daysSinceJoining} days</p>}
                                {isBehindSchedule && <p>• Behind expected schedule</p>}
                                {daysSinceLastAccess > 7 && <p>• Last accessed {daysSinceLastAccess} days ago</p>}
                              </div>
                            </div>
                          )}
                          
                          {/* Milestone Progress */}
                          <div className="bg-gray-50 rounded-lg p-3">
                            <h5 className="font-semibold mb-2">Milestone Progress</h5>
                            <div className="grid grid-cols-3 gap-2 text-xs">
                              <div className={`p-2 rounded ${progressPercent >= 25 ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'}`}>
                                25% Complete {progressPercent >= 25 ? '✓' : '○'}
                              </div>
                              <div className={`p-2 rounded ${progressPercent >= 50 ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'}`}>
                                50% Complete {progressPercent >= 50 ? '✓' : '○'}
                              </div>
                              <div className={`p-2 rounded ${progressPercent >= 80 ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'}`}>
                                80% Complete {progressPercent >= 80 ? '✓' : '○'}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  }) || []}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="detailed" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Detailed Progress Report</CardTitle>
                <CardDescription>Comprehensive view of each team member's learning journey</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Team Member</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Progress</TableHead>
                      <TableHead>Modules</TableHead>
                      <TableHead>Time Spent</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dashboardData.new_joiners?.map((member: any) => (
                      <TableRow key={member.user_id}>
                        <TableCell>
                          <div className="flex items-center space-x-3">
                            <Avatar className="w-8 h-8">
                              <AvatarFallback className="text-xs">
                                {member.name.split(' ').map((n: string) => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{member.name}</p>
                              <p className="text-sm text-muted-foreground">{member.email}</p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{member.roleType}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Progress value={member.progress?.overall_progress_percent || 0} className="w-16 h-2" />
                            <span className="text-sm">{member.progress?.overall_progress_percent || 0}%</span>
                          </div>
                        </TableCell>
                        <TableCell>{member.progress?.modules_completed || 0}/{member.progress?.total_modules || 0}</TableCell>
                        <TableCell>{Math.round((member.progress?.time_invested_minutes || 0) / 60)}h</TableCell>
                        <TableCell>
                          <Badge className={`${getStatusColor(member.progress?.overall_progress_percent || 0)} text-white`}>
                            {getStatusText(member.progress?.overall_progress_percent || 0)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm" onClick={() => {
                            navigate(`/manager/user/${member.user_id}`);
                          }}>
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    )) || []}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default ManagerView;