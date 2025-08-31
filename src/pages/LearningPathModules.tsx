import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import LiveTimer from "@/components/LiveTimer";
import { useSessionTracking } from "@/hooks/useSessionTracking";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft, 
  BookOpen, 
  PlayCircle, 
  FileText, 
  Clock,
  CheckCircle2,
  Lock
} from "lucide-react";

interface Module {
  id: string;
  title: string;
  description: string;
  duration_hours: number;
  chapter_count: number;
  order: number;
  prerequisite_module_ids: string[];
  unlock_condition: string;
  status: 'completed' | 'in_progress' | 'not_started';
  progress_percent: number;
  is_locked: boolean;
  chapters_completed?: number;
  time_spent_minutes?: number;
  last_accessed_at?: string;
  started_at?: string;
  completed_at?: string;
}

interface LearningPath {
  id: string;
  title: string;
  description: string;
  progress_percent?: number;
  overall_progress_percent?: number;
  module_items: Array<{module_id: string; order: number; is_required: boolean}>;
  modules_completed_count?: number;
  modules_total_count?: number;
}

const LearningPathModules = () => {
  const { pathId } = useParams();
  const navigate = useNavigate();
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  // Get user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const userId = user?.user_id || ''; // Don't use fallback user_001
  const { 
    trackActivity, 
    liveTimer, 
    currentActivityType 
  } = useSessionTracking(userId);

  // Debug logging
  console.log('LearningPathModules mounted with pathId:', pathId);

  useEffect(() => {
    if (!pathId || !user?.user_id) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        console.log('Fetching data for pathId:', pathId);
        
        // Track that user is viewing learning path modules
        trackActivity('learning_path_modules_view', pathId);
        
        // Fetch learning path details with progress from the list endpoint
        const pathResponse = await fetch(`/api/learning-paths?user_id=${userId}`);
        if (!pathResponse.ok) throw new Error('Failed to fetch learning paths');
        if (!pathResponse.ok) throw new Error('Failed to fetch learning paths');
        const pathData = await pathResponse.json();
        
        console.log('All paths from API:', pathData.results);
        console.log('Looking for pathId:', pathId);
        
        // Find the specific learning path - try both direct ID match and fallback to first path for debugging
        let currentPath = pathData.results.find((path: any) => path.id === pathId);
        
        // Temporary debugging fallback - if pathId is "1", use the first path
        if (!currentPath && pathId === '1' && pathData.results.length > 0) {
          console.log('PathId is "1", using first available path as fallback');
          currentPath = pathData.results[0];
        }
        
        console.log('Found path:', currentPath);
        
        if (!currentPath) throw new Error(`Learning path not found for ID: ${pathId}. Available IDs: ${pathData.results.map((p: any) => p.id).join(', ')}`);
        
        // Use the actual path ID for the modules API call (in case we used fallback)
        const actualPathId = currentPath.id;
        console.log('Using actual pathId for modules API:', actualPathId);
        
        // Fetch modules for this learning path
        const modulesResponse = await fetch(`/api/learning-paths/${actualPathId}/modules?user_id=${userId}`);
        if (!modulesResponse.ok) throw new Error('Failed to fetch modules');
        const modulesData = await modulesResponse.json();
        
        setLearningPath(currentPath);
        setModules(modulesData.modules || []);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [pathId, userId, user]);

  const handleModuleAction = async (module: Module) => {
    if (module.is_locked) return;
    
    // Track module interaction
    trackActivity('module_interaction', pathId, module.id);
    
    try {
      if (module.status === 'not_started') {
        // Track module start
        trackActivity('module_start', pathId, module.id);
        
        // Start the module
        const response = await fetch(`/api/modules/${module.id}/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId })
        });
        
        if (!response.ok) throw new Error('Failed to start module');
        
        // Update local state
        setModules(prev => prev.map(m => 
          m.id === module.id 
            ? { ...m, status: 'in_progress', started_at: new Date().toISOString() }
            : m
        ));
      }
      
      // Navigate to module content (you'll need to implement this route)
      navigate(`/learning-path/${pathId}/module/${module.id}`);
    } catch (err) {
      console.error('Error handling module action:', err);
      // You could show a toast/notification here
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-learning-success";
      case "in_progress": return "bg-learning-warning";  
      case "not_started": return "bg-muted";
      default: return "bg-muted";
    }
  };

  const getStatusIcon = (status: string, isLocked: boolean) => {
    if (isLocked) return <Lock className="w-4 h-4" />;
    if (status === "completed") return <CheckCircle2 className="w-4 h-4" />;
    if (status === "in_progress") return <PlayCircle className="w-4 h-4" />;
    return <BookOpen className="w-4 h-4" />;
  };

  const getButtonText = (module: Module) => {
    if (module.is_locked) return "Complete previous modules first";
    if (module.status === "completed") return "Review Module";
    if (module.status === "in_progress") return "Continue Module";
    return "Start Module";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8 pt-24">
          <div className="text-center">Loading...</div>
        </main>
      </div>
    );
  }

  if (error || !learningPath) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8 pt-24">
          <div className="text-center text-red-500">{error || 'Learning path not found'}</div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate("/dashboard")}
            className="mb-4 flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Dashboard</span>
          </Button>
          
          <div className="mb-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-foreground mb-2">{learningPath.title}</h1>
                <p className="text-muted-foreground text-lg">{learningPath.description}</p>
              </div>
              {/* Live Timer in header */}
              {currentActivityType && (
                <LiveTimer
                  seconds={liveTimer}
                  activityType={currentActivityType}
                  isActive={true}
                  variant="compact"
                  className="ml-4"
                />
              )}
            </div>
          </div>

          <Card className="mb-8">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-muted-foreground">Overall Progress</span>
                <span className="font-medium text-foreground">
                  {Math.round(learningPath.progress_percent || learningPath.overall_progress_percent || 0)}%
                </span>
              </div>
              <Progress value={learningPath.progress_percent || learningPath.overall_progress_percent || 0} className="h-3" />
              <p className="text-sm text-muted-foreground mt-2">
                Complete all modules to finish this learning path
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {modules.map((module) => (
            <Card 
              key={module.id} 
              className={`shadow-card hover:shadow-elegant transition-smooth ${
                module.is_locked ? 'opacity-60' : 'hover:scale-105'
              }`}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="flex items-center gap-2 mb-2">
                      {getStatusIcon(module.status, module.is_locked)}
                      {module.title}
                    </CardTitle>
                    <CardDescription>{module.description}</CardDescription>
                  </div>
                  <Badge className={`${getStatusColor(module.status)} text-white`}>
                    {module.is_locked ? "Locked" : module.status.replace("_", " ")}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{module.duration_hours} hours</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <FileText className="w-4 h-4" />
                        <span>{module.chapter_count} chapters</span>
                      </div>
                    </div>
                  </div>
                  
                  {!module.is_locked && module.progress_percent > 0 && (
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium text-foreground">{Math.round(module.progress_percent)}%</span>
                      </div>
                      <Progress value={module.progress_percent} className="h-2" />
                    </div>
                  )}
                  
                  <Button 
                    className="w-full" 
                    variant={module.status === "completed" ? "outline" : "default"}
                    disabled={module.is_locked}
                    onClick={() => handleModuleAction(module)}
                  >
                    {getButtonText(module)}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
};

export default LearningPathModules;