import React, { useState, useEffect } from 'react';
import DepartmentDocsManager from './DepartmentDocsManager';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Trash2, Plus, Users, BookOpen, Settings, CheckCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from '@/components/ui/use-toast';

const OnboardingManagement = () => {
  const [departments, setDepartments] = useState([]);
  const [learningPaths, setLearningPaths] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDepartment, setSelectedDepartment] = useState(null);

  // Load initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch departments with their learning path mappings
        const deptResponse = await fetch('/api/onboarding/departments');
        const deptData = await deptResponse.json();
        if (deptData.success) {
          setDepartments(deptData.data);
        }
        
        // Fetch available learning paths
        const pathsResponse = await fetch('/api/learning-paths');
        const pathsData = await pathsResponse.json();
        if (pathsData && pathsData.results) {
          setLearningPaths(pathsData.results);
        }
        
        // Fetch roles
        const rolesResponse = await fetch('/api/roles');
        const rolesData = await rolesResponse.json();
        if (rolesData) {
          setRoles(rolesData);
        }
        
      } catch (error) {
        console.error('Error fetching data:', error);
        toast({
          title: "Error",
          description: "Failed to load onboarding data",
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const addLearningPathToDepartment = async (deptId, pathMapping) => {
    try {
      const response = await fetch(`/api/onboarding/departments/${deptId}/learning-paths`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pathMapping)
      });
      
      const result = await response.json();
      if (result.success) {
        toast({
          title: "Success",
          description: "Learning path added to department"
        });
        // Refresh departments data
        const deptResponse = await fetch('/api/onboarding/departments');
        const deptData = await deptResponse.json();
        if (deptData.success) {
          setDepartments(deptData.data);
        }
        // Refresh learning paths data
        const pathsResponse = await fetch('/api/learning-paths');
        const pathsData = await pathsResponse.json();
        if (pathsData && pathsData.results) {
          setLearningPaths(pathsData.results);
        }
      } else {
        throw new Error(result.error || 'Failed to add learning path');
      }
    } catch (error) {
      toast({
        title: "Error", 
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const removeLearningPathFromDepartment = async (deptId, pathId) => {
    try {
      const response = await fetch(`/api/onboarding/departments/${deptId}/learning-paths/${pathId}`, {
        method: 'DELETE'
      });
      
      const result = await response.json();
      if (result.success) {
        toast({
          title: "Success",
          description: "Learning path removed from department"
        });
        // Refresh departments data
        const deptResponse = await fetch('/api/onboarding/departments');
        const deptData = await deptResponse.json();
        if (deptData.success) {
          setDepartments(deptData.data);
        }
        // Refresh learning paths data
        const pathsResponse = await fetch('/api/learning-paths');
        const pathsData = await pathsResponse.json();
        if (pathsData && pathsData.results) {
          setLearningPaths(pathsData.results);
        }
      } else {
        throw new Error(result.error || 'Failed to remove learning path');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message, 
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading onboarding management...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Onboarding Management</h2>
          <p className="text-muted-foreground">Configure department learning paths and role requirements</p>
        </div>
      </div>

      <Tabs defaultValue="departments" className="space-y-4">
        <TabsList>
          <TabsTrigger value="departments">Department Learning Paths</TabsTrigger>
          <TabsTrigger value="onboarding">Onboarding Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="departments" className="space-y-4">
          <div className="grid gap-6">
            {departments.map((dept) => (
              <DepartmentCard
                key={dept.id}
                department={dept}
                learningPaths={learningPaths}
                onAddPath={addLearningPathToDepartment}
                onRemovePath={removeLearningPathFromDepartment}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="onboarding" className="space-y-4">
          <OnboardingAnalytics />
        </TabsContent>
      </Tabs>
    </div>
  );
};

const DepartmentCard = ({ department, learningPaths, onAddPath, onRemovePath }) => {
  const [isAddingPath, setIsAddingPath] = useState(false);
  const [newPathMapping, setNewPathMapping] = useState({
    learning_path_id: '',
    is_mandatory: true,
    priority: 1,
    estimated_duration_weeks: null
  });

  const handleAddPath = async () => {
    if (!newPathMapping.learning_path_id) return;
    
    await onAddPath(department.id, newPathMapping);
    setIsAddingPath(false);
    setNewPathMapping({
      learning_path_id: '',
      is_mandatory: true,
      priority: 1,
      estimated_duration_weeks: null
    });
  };

  const availablePaths = (learningPaths || []).filter(path => 
    path && path.id && !(department.learning_paths || []).some(deptPath => deptPath && deptPath.learning_path_id === path.id)
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="w-5 h-5" />
          {department.name}
        </CardTitle>
        <CardDescription>{department.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {department.mandatory_paths?.length || 0} mandatory paths, 
            {department.learning_paths?.length || 0} total paths
          </div>
          <Dialog open={isAddingPath} onOpenChange={setIsAddingPath}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Add Learning Path
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Learning Path to {department.name}</DialogTitle>
                <DialogDescription>
                  Configure how this learning path applies to new joiners in this department
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="learning-path">Learning Path</Label>
                  <Select
                    value={newPathMapping.learning_path_id}
                    onValueChange={(value) => setNewPathMapping(prev => ({ ...prev, learning_path_id: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select learning path" />
                    </SelectTrigger>
                    <SelectContent>
                      {availablePaths.map(path => (
                        <SelectItem key={path.id} value={path.id}>
                          {path.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newPathMapping.is_mandatory}
                    onCheckedChange={(checked) => setNewPathMapping(prev => ({ ...prev, is_mandatory: checked }))}
                  />
                  <Label>Mandatory for all new joiners</Label>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="priority">Priority (1 = highest)</Label>
                    <Input
                      id="priority"
                      type="number"
                      min="1"
                      max="10"
                      value={newPathMapping.priority}
                      onChange={(e) => setNewPathMapping(prev => ({ ...prev, priority: parseInt(e.target.value) }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="duration">Est. Duration (weeks)</Label>
                    <Input
                      id="duration"
                      type="number"
                      placeholder="Optional"
                      value={newPathMapping.estimated_duration_weeks || ''}
                      onChange={(e) => setNewPathMapping(prev => ({ 
                        ...prev, 
                        estimated_duration_weeks: e.target.value ? parseInt(e.target.value) : null 
                      }))}
                    />
                  </div>
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsAddingPath(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddPath}>
                    Add Learning Path
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {department.learning_paths && department.learning_paths.length > 0 ? (
          <div className="space-y-2">
            {department.learning_paths
              .filter(pathMapping => pathMapping && pathMapping.learning_path_id)
              .sort((a, b) => a.priority - b.priority)
              .map((pathMapping) => {
                const path = (learningPaths || []).find(lp => lp && lp.id === pathMapping.learning_path_id);
                return (
                  <div key={pathMapping.learning_path_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <BookOpen className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <div className="font-medium">{path?.title || 'Unknown Path'}</div>
                        <div className="text-sm text-muted-foreground">
                          Priority {pathMapping.priority}
                          {pathMapping.estimated_duration_weeks && ` • ${pathMapping.estimated_duration_weeks} weeks`}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {pathMapping.is_mandatory ? (
                        <Badge variant="default">Mandatory</Badge>
                      ) : (
                        <Badge variant="secondary">Optional</Badge>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onRemovePath(department.id, pathMapping.learning_path_id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                );
              })}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No learning paths configured for this department
          </div>
        )}
      </CardContent>
      {/* Department Documentation Management */}
      <div className="mt-4">
        <DepartmentDocsManager departmentId={department.id} departmentName={department.name} />
      </div>
    </Card>
  );
};

const RoleManagement = ({ roles }) => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Role Skill Requirements</h3>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create New Role
        </Button>
      </div>
      
      <div className="grid gap-4">
        {roles.map((role) => (
          <Card key={role.role_id}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{role.role_name}</span>
                <Badge variant="outline">{role.department}</Badge>
              </CardTitle>
              <CardDescription>{role.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm font-medium">Required Skills ({role.skills?.length || 0})</div>
                <div className="flex flex-wrap gap-2">
                  {role.skills?.map((skill) => (
                    <Badge key={skill.skill_name} variant="secondary">
                      {skill.skill_name} (Level {skill.required_level})
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

const OnboardingAnalytics = () => {
  const [analytics, setAnalytics] = useState({
    totalOnboarded: 0,
    averageCompletionTime: 0,
    successRate: 92
  });

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch('/api/admin/stats/onboarding-analytics');
        const data = await response.json();
        setAnalytics({
          totalOnboarded: data.total_onboarded || 0,
          averageCompletionTime: data.average_completion_time || 0,
          successRate: data.success_rate || 92
        });
      } catch (error) {
        console.error('Error fetching analytics:', error);
      }
    };

    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Onboarding Analytics</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users Onboarded</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalOnboarded}</div>
            <p className="text-xs text-muted-foreground">This quarter</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Completion Time</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.averageCompletionTime} weeks</div>
            <p className="text-xs text-muted-foreground">Across all departments</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.successRate}%</div>
            <p className="text-xs text-muted-foreground">Complete within target time</p>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Department Performance</CardTitle>
          <CardDescription>Onboarding success rates by department</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Analytics dashboard coming soon...
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OnboardingManagement;
