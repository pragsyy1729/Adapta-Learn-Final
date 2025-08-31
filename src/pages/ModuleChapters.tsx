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
  PlayCircle, 
  FileText, 
  Clock,
  CheckCircle2,
  Video,
  BookOpen,
  HelpCircle
} from "lucide-react";

const ModuleChapters = () => {
  const { pathId, moduleId } = useParams();
  const navigate = useNavigate();
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
    endActivity, 
    liveTimer, 
    currentActivityType, 
    formatDuration 
  } = useSessionTracking(userId);

  // Track module activity on mount
  useEffect(() => {
    if (pathId && moduleId && user?.user_id) {
      trackActivity('module_study', pathId, moduleId);
    }

    // Cleanup on unmount
    return () => {
      if (user?.user_id) {
        endActivity();
      }
    };
  }, [pathId, moduleId, trackActivity, endActivity, user]);

  // Mock data - in real app this would come from API
  const module = {
    id: moduleId,
    title: "React Hooks & State Management",
    description: "Deep dive into useState, useEffect, and custom hooks",
    progress: 85,
    totalChapters: 7
  };

  const chapters = [
    {
      id: 1,
      title: "Introduction to React Hooks",
      description: "Understanding the motivation behind hooks and their benefits",
      type: "video",
      duration: "15 min",
      status: "completed",
      materials: [
        { type: "video", title: "What are React Hooks?", duration: "10 min" },
        { type: "text", title: "Reading: Hooks Overview", duration: "5 min" }
      ],
      quiz: { id: 1, title: "Hooks Basics Quiz", questions: 5, duration: "10 min" }
    },
    {
      id: 2,
      title: "useState Hook Deep Dive",
      description: "Managing component state with the useState hook",
      type: "video",
      duration: "25 min",
      status: "completed",
      materials: [
        { type: "video", title: "useState in Action", duration: "15 min" },
        { type: "text", title: "State Management Patterns", duration: "10 min" }
      ],
      quiz: { id: 2, title: "useState Mastery Quiz", questions: 8, duration: "15 min" }
    },
    {
      id: 3,
      title: "useEffect and Side Effects",
      description: "Handling side effects and lifecycle methods with useEffect",
      type: "video",
      duration: "30 min",
      status: "in-progress",
      materials: [
        { type: "video", title: "useEffect Fundamentals", duration: "20 min" },
        { type: "text", title: "Cleanup and Dependencies", duration: "10 min" }
      ],
      quiz: { id: 3, title: "useEffect Challenge", questions: 10, duration: "20 min" }
    },
    {
      id: 4,
      title: "Custom Hooks",
      description: "Creating reusable logic with custom hooks",
      type: "video",
      duration: "20 min",
      status: "not-started",
      materials: [
        { type: "video", title: "Building Custom Hooks", duration: "15 min" },
        { type: "text", title: "Hook Patterns", duration: "5 min" }
      ],
      quiz: { id: 4, title: "Custom Hooks Quiz", questions: 6, duration: "12 min" }
    },
    {
      id: 5,
      title: "useContext for State Sharing",
      description: "Sharing state across components with Context API",
      type: "video",
      duration: "25 min",
      status: "not-started",
      materials: [
        { type: "video", title: "Context API Explained", duration: "18 min" },
        { type: "text", title: "Context Best Practices", duration: "7 min" }
      ],
      quiz: { id: 5, title: "Context API Quiz", questions: 7, duration: "15 min" }
    },
    {
      id: 6,
      title: "useReducer for Complex State",
      description: "Managing complex state logic with useReducer",
      type: "video",
      duration: "30 min",
      status: "not-started",
      materials: [
        { type: "video", title: "useReducer Patterns", duration: "20 min" },
        { type: "text", title: "Reducer Best Practices", duration: "10 min" }
      ],
      quiz: { id: 6, title: "useReducer Mastery", questions: 9, duration: "18 min" }
    },
    {
      id: 7,
      title: "Performance Hooks",
      description: "Optimizing performance with useMemo and useCallback",
      type: "video",
      duration: "25 min",
      status: "not-started",
      materials: [
        { type: "video", title: "Performance Optimization", duration: "15 min" },
        { type: "text", title: "When to Optimize", duration: "10 min" }
      ],
      quiz: { id: 7, title: "Performance Quiz", questions: 8, duration: "15 min" }
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-learning-success";
      case "in-progress": return "bg-learning-warning";
      case "not-started": return "bg-muted";
      default: return "bg-muted";
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === "completed") return <CheckCircle2 className="w-4 h-4" />;
    if (status === "in-progress") return <PlayCircle className="w-4 h-4" />;
    return <BookOpen className="w-4 h-4" />;
  };

  const getMaterialIcon = (type: string) => {
    if (type === "video") return <Video className="w-4 h-4" />;
    return <FileText className="w-4 h-4" />;
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate(`/learning-path/${pathId}`)}
            className="mb-4 flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Modules</span>
          </Button>
          
          <div className="mb-6">
            <h1 className="text-4xl font-bold text-foreground mb-2">{module.title}</h1>
            <p className="text-muted-foreground text-lg">{module.description}</p>
          </div>

          <Card className="mb-8">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-muted-foreground">Module Progress</span>
                <span className="font-medium text-foreground">{module.progress}%</span>
              </div>
              <Progress value={module.progress} className="h-3" />
              <p className="text-sm text-muted-foreground mt-2">
                {Math.floor((module.progress / 100) * module.totalChapters)} of {module.totalChapters} chapters completed
              </p>
            </CardContent>
          </Card>

          {/* Live Timer Display */}
          <LiveTimer
            seconds={liveTimer}
            activityType={currentActivityType || undefined}
            isActive={currentActivityType === 'module_study'}
            variant="full"
            className="mb-8"
          />
        </div>

        <div className="space-y-6">
          {chapters.map((chapter) => (
            <Card key={chapter.id} className="shadow-card hover:shadow-elegant transition-smooth">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="flex items-center gap-2 mb-2">
                      {getStatusIcon(chapter.status)}
                      Chapter {chapter.id}: {chapter.title}
                    </CardTitle>
                    <CardDescription>{chapter.description}</CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={`${getStatusColor(chapter.status)} text-white`}>
                      {chapter.status.replace("-", " ")}
                    </Badge>
                    <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>{chapter.duration}</span>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  {/* Learning Materials */}
                  <div>
                    <h4 className="font-medium text-foreground mb-3">Learning Materials</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {chapter.materials.map((material, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gradient-card rounded-lg border">
                          <div className="flex items-center space-x-3">
                            {getMaterialIcon(material.type)}
                            <div>
                              <p className="text-sm font-medium text-foreground">{material.title}</p>
                              <p className="text-xs text-muted-foreground">{material.duration}</p>
                            </div>
                          </div>
                          <Button variant="outline" size="sm">
                            {material.type === "video" ? "Watch" : "Read"}
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Quiz Section */}
                  <div className="border-t pt-4">
                    <h4 className="font-medium text-foreground mb-3">Chapter Assessment</h4>
                    <div className="flex items-center justify-between p-4 bg-gradient-primary/10 rounded-lg border border-primary/20">
                      <div className="flex items-center space-x-3">
                        <HelpCircle className="w-5 h-5 text-primary" />
                        <div>
                          <p className="text-sm font-medium text-foreground">{chapter.quiz.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {chapter.quiz.questions} questions • {chapter.quiz.duration}
                          </p>
                        </div>
                      </div>
                      <Button 
                        onClick={() => navigate(`/quiz/${chapter.quiz.id}`)}
                        disabled={chapter.status === "not-started"}
                      >
                        {chapter.status === "completed" ? "Retake Quiz" : "Start Quiz"}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
};

export default ModuleChapters;