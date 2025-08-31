import Navigation from "@/components/Navigation";
import ModulesTable from "@/components/tables/ModulesTable";
import type { Module } from "@/types/module";
import EditModuleDialog from "@/components/dialogs/EditModuleDialog";
import RoleManagementTab from "@/components/tables/RoleManagementTab";
import DeleteModuleDialog from "@/components/dialogs/DeleteModuleDialog";
import LearningPathsTable from "@/components/tables/LearningPathsTable";
import EditLearningPathDialog from "@/components/dialogs/EditLearningPathDialog";
import ViewLearningPathDialog from "@/components/dialogs/ViewLearningPathDialog";
import DeleteLearningPathDialog from "@/components/dialogs/DeleteLearningPathDialog";
import MaterialManagerDialog from "@/components/dialogs/MaterialManagerDialog";
import OnboardingManagement from "@/components/OnboardingManagement";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Settings, BookOpen, Users, Database, Plus, Edit, Trash2, Eye, Upload, Download } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect, useRef } from "react";

import { LearningPath } from "@/types";



const AdminView = () => {
  // Stats for new joiners and enrollments
  const [totalNewJoiners, setTotalNewJoiners] = useState<number | null>(null);
  const [joinedThisMonth, setJoinedThisMonth] = useState<number | null>(null);
  const [activeEnrollments, setActiveEnrollments] = useState<number | null>(null);
  useEffect(() => {
    fetch("/api/admin/stats/new-joiners")
      .then(res => res.json())
      .then(data => {
        setTotalNewJoiners(data.total_new_joiners);
        setJoinedThisMonth(data.joined_this_month);
      })
      .catch(() => {
        setTotalNewJoiners(null);
        setJoinedThisMonth(null);
      });
    fetch("/api/admin/stats/active-enrollments")
      .then(res => res.json())
      .then(data => setActiveEnrollments(data.active_enrollments))
      .catch(() => setActiveEnrollments(null));
  }, []);
  // Module dialog state (should be inside the component)
  const [editModule, setEditModule] = useState<any | null>(null);
  const [deleteModule, setDeleteModule] = useState<any | null>(null);
  const [manageMaterialsModule, setManageMaterialsModule] = useState<Module | null>(null);
  const [isSavingModule, setIsSavingModule] = useState(false);
  // --- Learning Path State & API ---
  const queryClient = useQueryClient();
  const [newPath, setNewPath] = useState<Partial<LearningPath>>({});
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [viewPath, setViewPath] = useState<LearningPath | null>(null);
  const [editPath, setEditPath] = useState<LearningPath | null>(null);
  // Department list from backend
  const [departments, setDepartments] = useState<string[]>([]);
  useEffect(() => {
    fetch('/api/admin/departments')
      .then(res => res.json())
      .then(setDepartments)
      .catch(() => setDepartments([]));
  }, []);

  const [availableModules, setAvailableModules] = useState<Module[]>([]);
  const [modulesLoading, setModulesLoading] = useState(false);
  const [modulesError, setModulesError] = useState<string | null>(null);
  const [videoCount, setVideoCount] = useState(0);
  const [assessmentCount, setAssessmentCount] = useState(0);
  const [resourceCount, setResourceCount] = useState(0);
  const [audioCount, setAudioCount] = useState(0);
  const [textCount, setTextCount] = useState(0);
  const [slidesCount, setSlidesCount] = useState(0);

  // Function to refresh content stats
  const refreshContentStats = () => {
    fetch("/api/admin/content/stats")
      .then(res => res.json())
      .then(data => {
        setVideoCount(data.video_count || 0);
        setAssessmentCount(data.assessment_count || 0);
        setResourceCount(data.resource_count || 0);
        setAudioCount(data.audio_count || 0);
        setTextCount(data.text_count || 0);
        setSlidesCount(data.slides_count || 0);
      })
      .catch(e => {
        console.error('Error refreshing content stats:', e);
      });
  };

  // State to track which learning path's modules dropdown is open
  const [openModulesDropdownFor, setOpenModulesDropdownFor] = useState<string | null>(null);
  useEffect(() => {
    if (!openModulesDropdownFor) return;
    function handleClick(e: MouseEvent) {
      const dropdowns = document.querySelectorAll('.modules-dropdown, .modules-dropdown-menu');
      let inside = false;
      dropdowns.forEach(el => {
        if (el.contains(e.target as Node)) inside = true;
      });
      if (!inside) setOpenModulesDropdownFor(null);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [openModulesDropdownFor]);

  // Edit
  const editMutation = useMutation({
    mutationFn: async (data: LearningPath) => {
      const res = await fetch(`/api/admin/learning-paths/${data.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to update");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["learningPaths"] });
      setEditPath(null);
    },
  });

  // Fetch learning paths
  const { data: learningPaths = [], isLoading, isError } = useQuery<LearningPath[]>({
    queryKey: ["learningPaths"],
    queryFn: async () => {
      const res = await fetch("/api/admin/learning-paths");
      if (!res.ok) throw new Error("Failed to fetch");
      return res.json();
    },
    refetchOnWindowFocus: false,
  });

  // Create
  const createMutation = useMutation({
    mutationFn: async (data: Partial<LearningPath>) => {
      const res = await fetch("/api/admin/learning-paths", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to create");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["learningPaths"] });
      setCreateDialogOpen(false);
      setNewPath({});
    },
  });

  // Delete
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/admin/learning-paths/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["learningPaths"] });
      setDeleteId(null);
    },
  });

  const systemUsers = [
    {
      id: 1,
      name: "Alice Thompson",
      email: "alice.thompson@company.com",
      role: "Manager",
      department: "Engineering",
      status: "active",
      lastLogin: "2024-02-20"
    },
    {
      id: 2,
      name: "David Kumar",
      email: "david.kumar@company.com",
      role: "Manager",
      department: "Engineering",
      status: "active",
      lastLogin: "2024-02-19"
    },
    {
      id: 3,
      name: "Sarah Johnson",
      email: "sarah.johnson@company.com",
      role: "Employee",
      department: "Engineering",
      status: "active",
      lastLogin: "2024-02-20"
    }
  ];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Beginner": return "bg-learning-success text-white";
      case "Intermediate": return "bg-learning-warning text-white";
      case "Advanced": return "bg-primary text-primary-foreground";
      default: return "bg-muted text-muted-foreground";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-primary text-primary-foreground";
      case "draft": return "bg-learning-warning text-white";
      case "archived": return "bg-muted text-muted-foreground";
      default: return "bg-muted text-muted-foreground";
    }
  };

  useEffect(() => {
    setModulesLoading(true);
    const url = "/api/admin/modules";
    fetch(url)
      .then(async res => {
        if (!res.ok) {
          let text = await res.text();
          console.error('Modules fetch failed:', { status: res.status, statusText: res.statusText, url, body: text });
          throw new Error(`Failed to fetch modules: ${res.status} ${res.statusText}`);
        }
        try {
          return await res.json();
        } catch (jsonErr) {
          console.error('Modules response is not valid JSON:', { url, jsonErr });
          throw new Error('Modules response is not valid JSON');
        }
      })
      .then(data => {
  setAvailableModules(data);
  setModulesLoading(false);
      })
      .catch(e => {
        setModulesError(e.message);
        setModulesLoading(false);
        console.error('Error loading modules:', e);
      });

    // Fetch content statistics
    fetch("/api/admin/content/stats")
      .then(res => res.json())
      .then(data => {
        setVideoCount(data.video_count || 0);
        setAssessmentCount(data.assessment_count || 0);
        setResourceCount(data.resource_count || 0);
        setAudioCount(data.audio_count || 0);
        setTextCount(data.text_count || 0);
        setSlidesCount(data.slides_count || 0);
      })
      .catch(e => {
        console.error('Error loading content stats:', e);
      });
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage learning paths, users, and system configuration</p>
        </div>
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Learning Paths</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{learningPaths.length}</div>
              <p className="text-xs text-muted-foreground">{learningPaths.filter(p => p.status !== "archived").length} active, {learningPaths.filter(p => p.status === "archived").length} archived</p>
            </CardContent>
          </Card>
          {/* ...existing code for other cards... */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{totalNewJoiners !== null ? totalNewJoiners : "-"}</div>
              <p className="text-xs text-muted-foreground">
                {joinedThisMonth !== null ? `${joinedThisMonth} joined this month` : ""}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Enrollments</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{activeEnrollments !== null ? activeEnrollments : "-"}</div>
              <p className="text-xs text-muted-foreground">Total learning path enrollments by new joiners</p>
            </CardContent>
          </Card>
          
        </div>
        <Tabs defaultValue="learning-paths" className="space-y-6">
          <TabsList>
            <TabsTrigger value="learning-paths">Learning Paths</TabsTrigger>
            <TabsTrigger value="modules">Module Management</TabsTrigger>
            <TabsTrigger value="content">Content Library</TabsTrigger>
            <TabsTrigger value="roles">Role Management</TabsTrigger>
            <TabsTrigger value="onboarding">Onboarding</TabsTrigger>
          </TabsList>
          {/* Role Management Tab */}
          <TabsContent value="roles" className="space-y-6">
            <RoleManagementTab />
          </TabsContent>
          {/* Module Management Tab */}
          <TabsContent value="modules" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">Module Management</h2>
              <Button className="flex items-center space-x-2" onClick={() => setEditModule({ id: '', name: '', description: '', chapters: [] })}>
                <Plus className="w-4 h-4" />
                <span>Add Module</span>
              </Button>
            </div>
            <Card>
              <CardContent className="p-0">
                <ModulesTable
                  modules={availableModules}
                  onEdit={mod => setEditModule(mod)}
                  onDelete={mod => setDeleteModule(mod)}
                  onManageMaterials={mod => setManageMaterialsModule(mod)}
                />
                <EditModuleDialog
                  open={!!editModule}
                  onOpenChange={open => setEditModule(open ? editModule : null)}
                  module={editModule}
                  setModule={setEditModule}
                  onSave={async () => {
                    if (!editModule) return;
                    setIsSavingModule(true);
                    try {
                      const isNew = !editModule.id;
                      const url = isNew ? "/api/admin/modules" : `/api/admin/modules/${editModule.id}`;
                      const method = isNew ? "POST" : "PUT";
                      const res = await fetch(url, {
                        method,
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(editModule),
                      });
                      if (!res.ok) throw new Error("Failed to save module");
                      // Re-fetch modules
                      const modulesRes = await fetch("/api/admin/modules");
                      const modules = await modulesRes.json();
                      setAvailableModules(modules);
                      setEditModule(null);
                    } catch (e) {
                      // Optionally show error
                    } finally {
                      setIsSavingModule(false);
                    }
                  }}
                  isSaving={isSavingModule}
                />
                <DeleteModuleDialog
                  open={!!deleteModule}
                  onOpenChange={open => setDeleteModule(open ? deleteModule : null)}
                  moduleName={deleteModule?.name || ''}
                  onDelete={async () => {
                    if (!deleteModule) return;
                    try {
                      const response = await fetch(`/api/admin/modules/${deleteModule.id}`, {
                        method: "DELETE"
                      });
                      if (response.ok) {
                        // Re-fetch modules
                        const modulesRes = await fetch("/api/admin/modules");
                        const modules = await modulesRes.json();
                        setAvailableModules(modules);
                        setDeleteModule(null);
                      } else {
                        console.error("Failed to delete module");
                      }
                    } catch (error) {
                      console.error("Error deleting module:", error);
                    }
                  }}
                />
                <MaterialManagerDialog
                  open={!!manageMaterialsModule}
                  onOpenChange={open => setManageMaterialsModule(open ? manageMaterialsModule : null)}
                  module={manageMaterialsModule}
                  onMaterialUploaded={refreshContentStats}
                />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="learning-paths" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">Learning Paths Management</h2>
              <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="flex items-center space-x-2">
                    <Plus className="w-4 h-4" />
                    <span>Create New Path</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Create New Learning Path</DialogTitle>
                    <DialogDescription>
                      Design a comprehensive learning journey for your team members
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="title">Path Title</Label>
                        <Input id="title" value={newPath.title || ""} onChange={e => setNewPath(p => ({ ...p, title: e.target.value }))} placeholder="e.g., React Development Track" />
                      </div>
                      <div>
                        <Label htmlFor="duration">Duration</Label>
                        <Input id="duration" value={newPath.duration || ""} onChange={e => setNewPath(p => ({ ...p, duration: e.target.value }))} placeholder="e.g., 12 weeks" />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Textarea id="description" value={newPath.description || ""} onChange={e => setNewPath(p => ({ ...p, description: e.target.value }))} placeholder="Describe what learners will achieve in this path..." className="min-h-[100px]" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="difficulty">Difficulty Level</Label>
                        <Select value={newPath.difficulty || ""} onValueChange={val => setNewPath(p => ({ ...p, difficulty: val }))}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select difficulty" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Beginner">Beginner</SelectItem>
                            <SelectItem value="Intermediate">Intermediate</SelectItem>
                            <SelectItem value="Advanced">Advanced</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="department">Target Department</Label>
                        <Select value={newPath.department || ""} onValueChange={val => setNewPath(p => ({ ...p, department: val }))}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select department" />
                          </SelectTrigger>
                          <SelectContent>
                            {departments.map(dep => (
                              <SelectItem key={dep} value={dep}>{dep}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                      <Button
                        onClick={() => {
                          if (!newPath.title || !newPath.description || !newPath.difficulty || !newPath.duration || !newPath.department) return;
                          createMutation.mutate(newPath);
                        }}
                        disabled={
                          createMutation.isPending ||
                          !newPath.title ||
                          !newPath.description ||
                          !newPath.difficulty ||
                          !newPath.duration ||
                          !newPath.department
                        }
                      >
                        {createMutation.isPending ? "Creating..." : "Create Learning Path"}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <Card>
              <CardContent className="p-0">
                {isLoading ? (
                  <div className="p-8 text-center">Loading...</div>
                ) : isError ? (
                  <div className="p-8 text-center text-destructive">Failed to load learning paths.</div>
                ) : (
                  <LearningPathsTable
                    learningPaths={learningPaths}
                    getDifficultyColor={getDifficultyColor}
                    getStatusColor={getStatusColor}
                    viewPath={viewPath}
                    setViewPath={setViewPath}
                    editPath={editPath}
                    setEditPath={setEditPath}
                    deleteId={deleteId}
                    setDeleteId={setDeleteId}
                    availableModules={availableModules}
                    modulesLoading={modulesLoading}
                    modulesError={modulesError}
                    openModulesDropdownFor={openModulesDropdownFor}
                    setOpenModulesDropdownFor={setOpenModulesDropdownFor}
                    editMutation={editMutation}
                    deleteMutation={deleteMutation}
                  />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="content" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">Content Library</h2>
              <Button className="flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Add Content</span>
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Video Modules</CardTitle>
                  <CardDescription>Interactive video content</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary mb-2">{videoCount}</div>
                  <p className="text-sm text-muted-foreground">Total video modules</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Assessments</CardTitle>
                  <CardDescription>Quizzes and evaluations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary mb-2">{assessmentCount}</div>
                  <p className="text-sm text-muted-foreground">Active assessments</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Resources</CardTitle>
                  <CardDescription>Documents and references</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary mb-2">{resourceCount}</div>
                  <p className="text-sm text-muted-foreground">Resource files</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Audio Modules</CardTitle>
                  <CardDescription>Audio content</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary mb-2">{audioCount}</div>
                  <p className="text-sm text-muted-foreground">Audio modules</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Text Modules</CardTitle>
                  <CardDescription>Text-based content</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary mb-2">{textCount}</div>
                  <p className="text-sm text-muted-foreground">Text modules</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Slides Modules</CardTitle>
                  <CardDescription>Slide presentations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary mb-2">{slidesCount}</div>
                  <p className="text-sm text-muted-foreground">Slides modules</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Onboarding Management Tab */}
          <TabsContent value="onboarding" className="space-y-6">
            <OnboardingManagement />
          </TabsContent>

        </Tabs>
      </main>
    </div>
  );
};

export default AdminView;