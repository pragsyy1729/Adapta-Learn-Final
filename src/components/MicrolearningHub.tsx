import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { usePersonalizedMicrolearning, useCompleteMicrolearningModule } from '@/hooks/useApi';
import { MicrolearningModule } from '@/types';
import { Clock, Play, CheckCircle, Star, BookOpen, Video, FileText, Zap } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface MicrolearningHubProps {
  userId: string;
}

const ModuleCard: React.FC<{
  module: MicrolearningModule;
  onStart: (module: MicrolearningModule) => void;
  completed?: boolean;
}> = ({ module, onStart, completed = false }) => {
  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="h-5 w-5" />;
      case 'interactive':
        return <Zap className="h-5 w-5" />;
      case 'text':
        return <FileText className="h-5 w-5" />;
      default:
        return <BookOpen className="h-5 w-5" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className={`hover:shadow-md transition-shadow ${completed ? 'opacity-75' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getContentTypeIcon(module.content_type)}
            <Badge className={getDifficultyColor(module.difficulty)}>
              {module.difficulty}
            </Badge>
          </div>
          {completed && (
            <CheckCircle className="h-5 w-5 text-green-600" />
          )}
        </div>
        <CardTitle className="text-lg">{module.title}</CardTitle>
        <CardDescription>{module.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            {module.duration_minutes} min
          </div>
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4" />
            {module.points_reward} pts
          </div>
        </div>

        {module.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {module.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}

        <Button
          onClick={() => onStart(module)}
          disabled={completed}
          className="w-full"
          variant={completed ? "secondary" : "default"}
        >
          {completed ? (
            <>
              <CheckCircle className="h-4 w-4 mr-2" />
              Completed
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              Start Learning
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

const ModuleViewer: React.FC<{
  module: MicrolearningModule;
  onComplete: (moduleId: string, score?: number) => void;
  onClose: () => void;
}> = ({ module, onComplete, onClose }) => {
  const [progress, setProgress] = useState(0);
  const [completed, setCompleted] = useState(false);

  const handleComplete = () => {
    setCompleted(true);
    // Simulate progress completion
    setProgress(100);
    setTimeout(() => {
      onComplete(module.id, 100);
    }, 1000);
  };

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {module.content_type === 'video' && <Video className="h-5 w-5" />}
              {module.content_type === 'interactive' && <Zap className="h-5 w-5" />}
              {module.content_type === 'text' && <FileText className="h-5 w-5" />}
              {module.title}
            </CardTitle>
            <CardDescription>{module.description}</CardDescription>
          </div>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Module Content Area */}
        <div className="min-h-96 bg-gray-50 rounded-lg p-8 mb-6 flex items-center justify-center">
          <div className="text-center">
            {module.content_type === 'video' && (
              <div>
                <Video className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Video content would be displayed here</p>
              </div>
            )}
            {module.content_type === 'interactive' && (
              <div>
                <Zap className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Interactive content would be displayed here</p>
              </div>
            )}
            {module.content_type === 'text' && (
              <div>
                <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Text content would be displayed here</p>
                <p className="text-sm text-muted-foreground mt-2">
                  {module.content_text || 'Sample text content for demonstration purposes.'}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            Duration: {module.duration_minutes} minutes • {module.points_reward} points reward
          </div>
          <Button
            onClick={handleComplete}
            disabled={completed}
            size="lg"
          >
            {completed ? (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Completed!
              </>
            ) : (
              'Mark as Complete'
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export const MicrolearningHub: React.FC<MicrolearningHubProps> = ({ userId }) => {
  const { data: microlearningData, isLoading } = usePersonalizedMicrolearning(userId);
  const completeModule = useCompleteMicrolearningModule();
  const { toast } = useToast();

  const [selectedModule, setSelectedModule] = useState<MicrolearningModule | null>(null);
  const [completedModules, setCompletedModules] = useState<Set<string>>(new Set());

  const handleStartModule = (module: MicrolearningModule) => {
    setSelectedModule(module);
  };

  const handleCompleteModule = async (moduleId: string, score?: number) => {
    try {
      await completeModule.mutateAsync({
        userId,
        moduleId,
        score,
      });

      setCompletedModules(prev => new Set([...prev, moduleId]));
      setSelectedModule(null);

      toast({
        title: "Module completed!",
        description: "Great job! You've earned points for completing this module.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to mark module as complete.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Microlearning Hub</CardTitle>
          <CardDescription>Loading your personalized learning modules...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-48 bg-gray-100 animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!microlearningData?.data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Microlearning Hub</CardTitle>
          <CardDescription>Unable to load microlearning modules</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const { recommended, trending, by_category, daily_challenge } = microlearningData.data;

  if (selectedModule) {
    return (
      <ModuleViewer
        module={selectedModule}
        onComplete={handleCompleteModule}
        onClose={() => setSelectedModule(null)}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Daily Challenge */}
      {daily_challenge && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5 text-primary" />
              Daily Challenge
            </CardTitle>
            <CardDescription>Complete today's challenge to earn bonus points!</CardDescription>
          </CardHeader>
          <CardContent>
            <ModuleCard
              module={daily_challenge}
              onStart={handleStartModule}
              completed={completedModules.has(daily_challenge.id)}
            />
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs defaultValue="recommended" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="recommended">
            Recommended ({recommended.length})
          </TabsTrigger>
          <TabsTrigger value="trending">
            Trending ({trending.length})
          </TabsTrigger>
          <TabsTrigger value="categories">
            Categories
          </TabsTrigger>
        </TabsList>

        <TabsContent value="recommended" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Recommended for You</CardTitle>
              <CardDescription>Personalized modules based on your learning style and progress</CardDescription>
            </CardHeader>
            <CardContent>
              {recommended.length === 0 ? (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No recommended modules available</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommended.map((module) => (
                    <ModuleCard
                      key={module.id}
                      module={module}
                      onStart={handleStartModule}
                      completed={completedModules.has(module.id)}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trending" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Trending Modules</CardTitle>
              <CardDescription>Popular modules that other learners are enjoying</CardDescription>
            </CardHeader>
            <CardContent>
              {trending.length === 0 ? (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No trending modules available</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {trending.map((module) => (
                    <ModuleCard
                      key={module.id}
                      module={module}
                      onStart={handleStartModule}
                      completed={completedModules.has(module.id)}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="mt-6">
          <div className="space-y-6">
            {Object.entries(by_category).map(([category, modules]) => (
              <Card key={category}>
                <CardHeader>
                  <CardTitle className="capitalize">{category.replace('_', ' ')}</CardTitle>
                  <CardDescription>{modules.length} modules available</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {modules.map((module) => (
                      <ModuleCard
                        key={module.id}
                        module={module}
                        onStart={handleStartModule}
                        completed={completedModules.has(module.id)}
                      />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};
