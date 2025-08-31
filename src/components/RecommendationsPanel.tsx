import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useUserRecommendations, useTrackRecommendationInteraction } from '@/hooks/useApi';
import { Recommendation } from '@/types';
import { Calendar, Clock, User, Bot, Shield, Award, ExternalLink } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import DashboardAIRecommendationsTab from '@/pages/DashboardAIRecommendationsTab';

interface RecommendationsPanelProps {
  userId: string;
}

const RecommendationCard: React.FC<{
  recommendation: Recommendation;
  onInteract: (interactionType: string) => void;
}> = ({ recommendation, onInteract }) => {
  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'ai':
        return <Bot className="h-4 w-4" />;
      case 'hr':
        return <User className="h-4 w-4" />;
      case 'admin':
      case 'manager':
        return <Shield className="h-4 w-4" />;
      default:
        return <Award className="h-4 w-4" />;
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'ai':
        return 'bg-blue-100 text-blue-800';
      case 'hr':
        return 'bg-green-100 text-green-800';
      case 'admin':
      case 'manager':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="mb-4 hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getSourceIcon(recommendation.source)}
            <Badge className={getSourceColor(recommendation.source)}>
              {recommendation.source.toUpperCase()}
            </Badge>
            <Badge className={getPriorityColor(recommendation.priority)}>
              {recommendation.priority}
            </Badge>
          </div>
          {recommendation.confidence_score && (
            <Badge variant="outline">
              {Math.round(recommendation.confidence_score * 100)}% confidence
            </Badge>
          )}
        </div>
        <CardTitle className="text-lg">{recommendation.title}</CardTitle>
        <CardDescription>{recommendation.description}</CardDescription>
      </CardHeader>
      <CardContent>
        {recommendation.reason && (
          <p className="text-sm text-muted-foreground mb-3">
            <strong>Reason:</strong> {recommendation.reason}
          </p>
        )}

        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            {new Date(recommendation.generated_at).toLocaleDateString()}
          </div>
          {recommendation.due_date && (
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              Due: {new Date(recommendation.due_date).toLocaleDateString()}
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={() => onInteract('viewed')}
            className="flex-1"
          >
            View Details
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onInteract('started')}
            className="flex-1"
          >
            Start Learning
            <ExternalLink className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({ userId }) => {
  const { data: recommendationsData, isLoading, error } = useUserRecommendations(userId);
  const trackInteraction = useTrackRecommendationInteraction();
  const { toast } = useToast();

  const handleInteraction = async (recommendationId: string, interactionType: string) => {
    try {
      await trackInteraction.mutateAsync({
        userId,
        recommendationId,
        interactionType,
      });

      toast({
        title: "Interaction tracked",
        description: `Recommendation ${interactionType} recorded successfully.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to track interaction.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
          <CardDescription>Loading your personalized recommendations...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-gray-100 animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !recommendationsData?.data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
          <CardDescription>Unable to load recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            {error?.message || 'No recommendations available at this time.'}
          </p>
        </CardContent>
      </Card>
    );
  }

  const { recommendations, total_count, counts_by_source } = recommendationsData.data;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Award className="h-5 w-5" />
          Recommendations
        </CardTitle>
        <CardDescription>
          AI-powered insights and recommendations from AI, HR, and Managers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="ai-recommendations" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="ai-recommendations">
              AI Recommendations
            </TabsTrigger>
            <TabsTrigger value="hr">
              HR ({counts_by_source.hr})
            </TabsTrigger>
            <TabsTrigger value="manager">
              Manager ({counts_by_source.admin})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="ai-recommendations" className="mt-4">
            <DashboardAIRecommendationsTab />
          </TabsContent>

          <TabsContent value="hr" className="mt-4">
            {recommendations.hr.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                No HR recommendations available
              </p>
            ) : (
              recommendations.hr.map((rec) => (
                <RecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  onInteract={(type) => handleInteraction(rec.id, type)}
                />
              ))
            )}
          </TabsContent>

          <TabsContent value="manager" className="mt-4">
            {recommendations.admin.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                No Manager recommendations available
              </p>
            ) : (
              recommendations.admin.map((rec) => (
                <RecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  onInteract={(type) => handleInteraction(rec.id, type)}
                />
              ))
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
