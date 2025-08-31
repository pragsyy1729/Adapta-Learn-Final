import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface LearningPath {
  id: string;
  title: string;
  description: string;
  progress_percent: number;
  status: string;
  modules_completed_count: number;
  modules_total_count: number;
  tags: string[];
  duration_weeks: number;
}

const DashboardLearningPathsTab = () => {
  const navigate = useNavigate();
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  // Get user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
    }
  }, []);

  const userId = user?.user_id || '';

  useEffect(() => {
    if (!userId) return;

    const fetchLearningPaths = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/learning-paths/${userId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setPaths(data.assigned_learning_paths || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchLearningPaths();
  }, [userId]);

  const handleContinue = (pathId: string) => {
    console.log('Navigating to:', `/learning-path/${pathId}/modules`);
    console.log('Path ID:', pathId);
    navigate(`/learning-path/${pathId}/modules`);
  };

  const handleViewAll = () => {
    // Navigate to a full learning paths view (you'll need to implement this)
    navigate('/learning-paths');
  };

  if (loading) {
    return <div className="text-center p-8">Loading learning paths...</div>;
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">Error: {error}</div>;
  }

  if (!paths.length) {
    return (
      <div className="text-center p-8">
        <h2 className="text-2xl font-bold mb-4">Your Learning Paths</h2>
        <p className="text-muted-foreground">No learning paths assigned yet.</p>
        <Button onClick={handleViewAll} className="mt-4">
          Browse Available Paths
        </Button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Your Learning Paths</h2>
        <Button variant="outline" onClick={handleViewAll}>
          View All
        </Button>
      </div>
      
      <div className="space-y-4">
        {paths.map((path) => (
          <Card key={path.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="mb-2">{path.title || 'Untitled Learning Path'}</CardTitle>
                  <CardDescription>{path.description || 'No description available'}</CardDescription>
                </div>
                <div className="text-right">
                  <div className="text-sm text-muted-foreground mb-1">
                    {path.modules_completed_count || 0} of {path.modules_total_count || 0} modules
                  </div>
                  <div className="font-medium text-foreground">
                    {Math.round(path.progress_percent || 0)}% Complete
                  </div>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-4">
                {/* Progress Bar */}
                <div>
                  <Progress value={path.progress_percent || 0} className="h-2" />
                </div>
                
                {/* Tags and Duration */}
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center space-x-2">
                    {(path.tags && Array.isArray(path.tags) ? path.tags.slice(0, 3) : []).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-secondary rounded-md text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <span>{path.duration_weeks || 'N/A'} weeks</span>
                </div>
                
                {/* Action Button */}
                <Button 
                  onClick={() => {
                    console.log('Button clicked for path:', path);
                    console.log('Path ID being passed:', path.id);
                    handleContinue(path.id);
                  }}
                  className="w-full"
                  variant={(path.progress_percent || 0) > 0 ? "default" : "outline"}
                >
                  {(path.progress_percent || 0) > 0 ? "Continue" : "Start Learning"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default DashboardLearningPathsTab;
