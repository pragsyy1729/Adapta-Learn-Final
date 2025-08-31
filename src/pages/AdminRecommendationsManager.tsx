import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useAddHRRecommendation, useAddAdminRecommendation, useGenerateAIRecommendations, useRecommendationsAnalytics } from '@/hooks/useApi';
import { useToast } from '@/hooks/use-toast';
import { Users, Award, TrendingUp, Plus, Bot, User, Shield, BarChart3 } from 'lucide-react';

const AdminRecommendationsManager = () => {
  const [hrForm, setHrForm] = useState({
    user_id: '',
    title: '',
    description: '',
    reason: '',
    priority: 'medium' as const,
    content_id: '',
    content_type: 'learning_path' as const,
    assigned_by: 'admin@example.com',
    due_date: ''
  });

  const [adminForm, setAdminForm] = useState({
    user_id: '',
    title: '',
    description: '',
    reason: '',
    priority: 'high' as const,
    content_id: '',
    content_type: 'module' as const,
    assigned_by: 'admin@example.com',
    target_audience: 'all_employees'
  });

  const [aiUserId, setAiUserId] = useState('');

  const addHRRecommendation = useAddHRRecommendation();
  const addAdminRecommendation = useAddAdminRecommendation();
  const generateAIRecommendations = useGenerateAIRecommendations();
  const { data: analyticsData } = useRecommendationsAnalytics();
  const { toast } = useToast();

  const handleHRSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addHRRecommendation.mutateAsync(hrForm);
      toast({
        title: "Success",
        description: "HR recommendation added successfully",
      });
      // Reset form
      setHrForm({
        user_id: '',
        title: '',
        description: '',
        reason: '',
        priority: 'medium',
        content_id: '',
        content_type: 'learning_path',
        assigned_by: 'admin@example.com',
        due_date: ''
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add HR recommendation",
        variant: "destructive",
      });
    }
  };

  const handleAdminSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addAdminRecommendation.mutateAsync(adminForm);
      toast({
        title: "Success",
        description: "Admin recommendation added successfully",
      });
      // Reset form
      setAdminForm({
        user_id: '',
        title: '',
        description: '',
        reason: '',
        priority: 'high',
        content_id: '',
        content_type: 'module',
        assigned_by: 'admin@example.com',
        target_audience: 'all_employees'
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add admin recommendation",
        variant: "destructive",
      });
    }
  };

  const handleGenerateAI = async () => {
    if (!aiUserId) {
      toast({
        title: "Error",
        description: "Please enter a user ID",
        variant: "destructive",
      });
      return;
    }

    try {
      await generateAIRecommendations.mutateAsync(aiUserId);
      toast({
        title: "Success",
        description: "AI recommendations generated successfully",
      });
      setAiUserId('');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate AI recommendations",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <Shield className="h-6 w-6" />
        <h1 className="text-2xl font-bold">Admin Recommendations Manager</h1>
      </div>

      {/* Analytics Overview */}
      {analyticsData?.data && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-2xl font-bold">{analyticsData.data.total_recommendations}</p>
                  <p className="text-xs text-muted-foreground">Total Recommendations</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">{analyticsData.data.recommendations_by_source.ai}</p>
                  <p className="text-xs text-muted-foreground">AI Generated</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">{analyticsData.data.recommendations_by_source.hr}</p>
                  <p className="text-xs text-muted-foreground">HR Created</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-red-600" />
                <div>
                  <p className="text-2xl font-bold">{analyticsData.data.recommendations_by_source.admin}</p>
                  <p className="text-xs text-muted-foreground">Admin Created</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="hr" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="hr" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            HR Recommendations
          </TabsTrigger>
          <TabsTrigger value="admin" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Admin Recommendations
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-2">
            <Bot className="h-4 w-4" />
            AI Generation
          </TabsTrigger>
        </TabsList>

        <TabsContent value="hr" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Add HR Recommendation</CardTitle>
              <CardDescription>
                Create personalized recommendations for career development and performance improvement
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleHRSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="hr-user-id">User ID</Label>
                    <Input
                      id="hr-user-id"
                      value={hrForm.user_id}
                      onChange={(e) => setHrForm(prev => ({ ...prev, user_id: e.target.value }))}
                      placeholder="user_123"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="hr-assigned-by">Assigned By</Label>
                    <Input
                      id="hr-assigned-by"
                      value={hrForm.assigned_by}
                      onChange={(e) => setHrForm(prev => ({ ...prev, assigned_by: e.target.value }))}
                      placeholder="hr_manager@example.com"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="hr-title">Title</Label>
                  <Input
                    id="hr-title"
                    value={hrForm.title}
                    onChange={(e) => setHrForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Leadership Development Program"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="hr-description">Description</Label>
                  <Textarea
                    id="hr-description"
                    value={hrForm.description}
                    onChange={(e) => setHrForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Advanced leadership skills training for senior roles"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="hr-reason">Reason</Label>
                  <Textarea
                    id="hr-reason"
                    value={hrForm.reason}
                    onChange={(e) => setHrForm(prev => ({ ...prev, reason: e.target.value }))}
                    placeholder="Based on performance review and career progression plan"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="hr-priority">Priority</Label>
                    <Select value={hrForm.priority} onValueChange={(value: any) => setHrForm(prev => ({ ...prev, priority: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="hr-content-type">Content Type</Label>
                    <Select value={hrForm.content_type} onValueChange={(value: any) => setHrForm(prev => ({ ...prev, content_type: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="learning_path">Learning Path</SelectItem>
                        <SelectItem value="module">Module</SelectItem>
                        <SelectItem value="microlearning">Microlearning</SelectItem>
                        <SelectItem value="quiz">Quiz</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="hr-due-date">Due Date</Label>
                    <Input
                      id="hr-due-date"
                      type="date"
                      value={hrForm.due_date}
                      onChange={(e) => setHrForm(prev => ({ ...prev, due_date: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="hr-content-id">Content ID</Label>
                  <Input
                    id="hr-content-id"
                    value={hrForm.content_id}
                    onChange={(e) => setHrForm(prev => ({ ...prev, content_id: e.target.value }))}
                    placeholder="LP_LEADERSHIP_001"
                    required
                  />
                </div>

                <Button type="submit" disabled={addHRRecommendation.isPending}>
                  {addHRRecommendation.isPending ? 'Adding...' : 'Add HR Recommendation'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="admin" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Add Admin Recommendation</CardTitle>
              <CardDescription>
                Create organization-wide recommendations for compliance and mandatory training
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAdminSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="admin-user-id">User ID</Label>
                    <Input
                      id="admin-user-id"
                      value={adminForm.user_id}
                      onChange={(e) => setAdminForm(prev => ({ ...prev, user_id: e.target.value }))}
                      placeholder="user_123"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="admin-assigned-by">Assigned By</Label>
                    <Input
                      id="admin-assigned-by"
                      value={adminForm.assigned_by}
                      onChange={(e) => setAdminForm(prev => ({ ...prev, assigned_by: e.target.value }))}
                      placeholder="admin@example.com"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="admin-title">Title</Label>
                  <Input
                    id="admin-title"
                    value={adminForm.title}
                    onChange={(e) => setAdminForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Compliance Training Update"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="admin-description">Description</Label>
                  <Textarea
                    id="admin-description"
                    value={adminForm.description}
                    onChange={(e) => setAdminForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Mandatory compliance training for all employees"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="admin-reason">Reason</Label>
                  <Textarea
                    id="admin-reason"
                    value={adminForm.reason}
                    onChange={(e) => setAdminForm(prev => ({ ...prev, reason: e.target.value }))}
                    placeholder="New regulatory requirements"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="admin-priority">Priority</Label>
                    <Select value={adminForm.priority} onValueChange={(value: any) => setAdminForm(prev => ({ ...prev, priority: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="admin-content-type">Content Type</Label>
                    <Select value={adminForm.content_type} onValueChange={(value: any) => setAdminForm(prev => ({ ...prev, content_type: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="learning_path">Learning Path</SelectItem>
                        <SelectItem value="module">Module</SelectItem>
                        <SelectItem value="microlearning">Microlearning</SelectItem>
                        <SelectItem value="quiz">Quiz</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="admin-target-audience">Target Audience</Label>
                    <Select value={adminForm.target_audience} onValueChange={(value: any) => setAdminForm(prev => ({ ...prev, target_audience: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all_employees">All Employees</SelectItem>
                        <SelectItem value="management">Management</SelectItem>
                        <SelectItem value="specific_department">Specific Department</SelectItem>
                        <SelectItem value="new_hires">New Hires</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="admin-content-id">Content ID</Label>
                  <Input
                    id="admin-content-id"
                    value={adminForm.content_id}
                    onChange={(e) => setAdminForm(prev => ({ ...prev, content_id: e.target.value }))}
                    placeholder="MODULE_COMPLIANCE_2024"
                    required
                  />
                </div>

                <Button type="submit" disabled={addAdminRecommendation.isPending}>
                  {addAdminRecommendation.isPending ? 'Adding...' : 'Add Admin Recommendation'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ai" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Generate AI Recommendations</CardTitle>
              <CardDescription>
                Automatically generate personalized recommendations using AI analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="ai-user-id">User ID</Label>
                  <Input
                    id="ai-user-id"
                    value={aiUserId}
                    onChange={(e) => setAiUserId(e.target.value)}
                    placeholder="user_123"
                  />
                </div>

                <Button
                  onClick={handleGenerateAI}
                  disabled={generateAIRecommendations.isPending || !aiUserId}
                  className="w-full"
                >
                  {generateAIRecommendations.isPending ? (
                    'Generating...'
                  ) : (
                    <>
                      <Bot className="h-4 w-4 mr-2" />
                      Generate AI Recommendations
                    </>
                  )}
                </Button>

                <div className="mt-4 p-4 bg-muted rounded-lg">
                  <h4 className="font-semibold mb-2">AI Generation Process:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Analyzes user's learning history and performance</li>
                    <li>• Considers department, role, and VARK learning style</li>
                    <li>• Identifies skill gaps and career progression opportunities</li>
                    <li>• Generates personalized recommendations with confidence scores</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminRecommendationsManager;
