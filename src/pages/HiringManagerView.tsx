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
import { Building2, Users, BarChart3, Calendar, Target, Star, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";

const HiringManagerView = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  // Get user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      
      // Check if user has hiring manager role
      if (parsedUser?.roleType !== 'Hiring Manager' && parsedUser?.roleType !== 'hiring_manager' && parsedUser?.roleType !== 'Director') {
        setError("Access denied. This page is only accessible to hiring managers.");
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
          <h1 className="text-4xl font-bold text-foreground mb-2">Hiring Manager Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor operational team performance and new hire integration
            {dashboardData.department && ` in ${dashboardData.department}`}
          </p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Department Managers</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.managers_count || 0}</div>
              <p className="text-xs text-muted-foreground">Under supervision</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">New Joiners</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.total_dept_new_joiners || 0}</div>
              <p className="text-xs text-muted-foreground">In onboarding</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Department Progress</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.avg_dept_progress || 0}%</div>
              <p className="text-xs text-muted-foreground">Department-wide progress</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Onboarding Completion</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardData.onboarding_completion_rate || 0}%</div>
              <p className="text-xs text-muted-foreground">New joiners at 80%+</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="teams" className="space-y-6">
          <TabsList>
            <TabsTrigger value="teams">Team Overview</TabsTrigger>
            <TabsTrigger value="joiners">New Joiners</TabsTrigger>
            <TabsTrigger value="hiring">Hiring Pipeline</TabsTrigger>
          </TabsList>

          <TabsContent value="teams" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {dashboardData.department_managers?.map((manager: any) => (
                <Card key={manager.user_id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{manager.name}</CardTitle>
                        <CardDescription>{manager.role} • {manager.team || 'Team Lead'}</CardDescription>
                      </div>
                      <Badge variant="outline">{manager.new_joiners_count || 0} new joiners</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Avatar className="w-8 h-8">
                        <AvatarFallback className="text-xs">
                          {manager.name.split(' ').map((n: string) => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{manager.name}</p>
                        <p className="text-xs text-muted-foreground">{manager.role}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Team Progress</span>
                          <span>{manager.avg_team_progress || 0}%</span>
                        </div>
                        <Progress value={manager.avg_team_progress || 0} className="h-2" />
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">New Joiners</span>
                          <p className="font-semibold text-primary">{manager.new_joiners_count || 0}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Avg Progress</span>
                          <p className="font-semibold text-primary">{manager.avg_team_progress || 0}%</p>
                        </div>
                      </div>
                    </div>
                    
                    <Button variant="outline" className="w-full" onClick={() => {
                      // TODO: Navigate to manager's team detail view
                      console.log('View team details for:', manager.user_id);
                    }}>
                      View Team Details
                    </Button>
                  </CardContent>
                </Card>
              )) || []}
            </div>
          </TabsContent>

          <TabsContent value="joiners" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>New Joiners Performance</CardTitle>
                <CardDescription>Track the progress of recently hired team members across all teams</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee</TableHead>
                      <TableHead>Manager</TableHead>
                      <TableHead>Progress</TableHead>
                      <TableHead>Time Invested</TableHead>
                      <TableHead>Modules</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dashboardData.department_new_joiners?.map((joiner: any) => (
                      <TableRow key={joiner.user_id}>
                        <TableCell>
                          <div className="flex items-center space-x-3">
                            <Avatar className="w-8 h-8">
                              <AvatarFallback className="text-xs">
                                {joiner.name.split(' ').map((n: string) => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{joiner.name}</p>
                              <p className="text-sm text-muted-foreground">New Joiner</p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          {/* Find manager name from department_managers */}
                          {(() => {
                            const manager = dashboardData.department_managers?.find((m: any) => 
                              m.new_joiners?.some((nj: any) => nj.user_id === joiner.user_id)
                            );
                            return manager ? manager.name : 'Unknown';
                          })()}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Progress value={joiner.progress?.overall_progress_percent || 0} className="w-16 h-2" />
                            <span className="text-sm">{joiner.progress?.overall_progress_percent || 0}%</span>
                          </div>
                        </TableCell>
                        <TableCell>{Math.round((joiner.progress?.time_invested_minutes || 0) / 60)}h</TableCell>
                        <TableCell>{joiner.progress?.modules_completed || 0}/{joiner.progress?.total_modules || 0}</TableCell>
                        <TableCell>
                          <Badge className={`${getStatusColor(joiner.progress?.overall_progress_percent || 0)} text-white`}>
                            {getStatusText(joiner.progress?.overall_progress_percent || 0)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm" onClick={() => {
                            // TODO: Navigate to user detail view
                            console.log('View profile for:', joiner.user_id);
                          }}>
                            View Profile
                          </Button>
                        </TableCell>
                      </TableRow>
                    )) || []}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Performance Insights</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {(() => {
                    const sortedJoiners = [...(dashboardData.department_new_joiners || [])]
                      .sort((a, b) => (b.progress?.overall_progress_percent || 0) - (a.progress?.overall_progress_percent || 0));
                    
                    const topPerformer = sortedJoiners[0];
                    const needsAttention = sortedJoiners[sortedJoiners.length - 1];
                    
                    return (
                      <>
                        {topPerformer && (
                          <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                            <span className="text-sm">Top Performer</span>
                            <div className="flex items-center space-x-2">
                              <span className="font-semibold">{topPerformer.name}</span>
                              <Badge className="bg-learning-success text-white">
                                {topPerformer.progress?.overall_progress_percent || 0}% Progress
                              </Badge>
                            </div>
                          </div>
                        )}
                        {needsAttention && needsAttention.progress?.overall_progress_percent < 60 && (
                          <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                            <span className="text-sm">Needs Support</span>
                            <div className="flex items-center space-x-2">
                              <span className="font-semibold">{needsAttention.name}</span>
                              <Badge className="bg-learning-warning text-white">
                                {needsAttention.progress?.overall_progress_percent || 0}% Progress
                              </Badge>
                            </div>
                          </div>
                        )}
                      </>
                    );
                  })()}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Department Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Overall Completion Rate</span>
                      <span className="font-semibold">{dashboardData.onboarding_completion_rate || 0}%</span>
                    </div>
                    <Progress value={dashboardData.onboarding_completion_rate || 0} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Average Progress</span>
                      <span className="font-semibold">{dashboardData.avg_dept_progress || 0}%</span>
                    </div>
                    <Progress value={dashboardData.avg_dept_progress || 0} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Active New Joiners</span>
                      <span className="font-semibold">{dashboardData.total_dept_new_joiners || 0}</span>
                    </div>
                    <Progress value={((dashboardData.total_dept_new_joiners || 0) / 10) * 100} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="hiring" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Hiring Pipeline Overview</CardTitle>
                <CardDescription>Track recruitment progress and upcoming onboarding</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-6 border rounded-lg">
                    <div className="text-2xl font-bold text-primary mb-2">{dashboardData.total_dept_new_joiners || 0}</div>
                    <p className="text-sm text-muted-foreground">Active Onboardings</p>
                  </div>
                  <div className="text-center p-6 border rounded-lg">
                    <div className="text-2xl font-bold text-primary mb-2">{dashboardData.onboarding_completion_rate || 0}%</div>
                    <p className="text-sm text-muted-foreground">Completion Rate</p>
                  </div>
                  <div className="text-center p-6 border rounded-lg">
                    <div className="text-2xl font-bold text-primary mb-2">{dashboardData.managers_count || 0}</div>
                    <p className="text-sm text-muted-foreground">Team Managers</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Manager Performance Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.department_managers?.map((manager: any, index: number) => (
                    <div key={manager.user_id} className="flex justify-between items-center p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Avatar>
                          <AvatarFallback>
                            {manager.name.split(' ').map((n: string) => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{manager.name}</p>
                          <p className="text-sm text-muted-foreground">{manager.role} • {manager.new_joiners_count || 0} new joiners</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{manager.avg_team_progress || 0}% avg progress</p>
                        <p className="text-xs text-muted-foreground">Team performance</p>
                      </div>
                    </div>
                  )) || []}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default HiringManagerView;