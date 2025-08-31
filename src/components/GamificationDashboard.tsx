import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useUserGamification, useLeaderboard } from '@/hooks/useApi';
import { UserGamification, LeaderboardEntry } from '@/types';
import { Trophy, Medal, Star, Crown, TrendingUp, Users, Target, Award } from 'lucide-react';

interface GamificationDashboardProps {
  userId: string;
}

const BadgeCard: React.FC<{ badge: any }> = ({ badge }) => {
  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return 'bg-gradient-to-r from-yellow-400 to-orange-500';
      case 'epic':
        return 'bg-gradient-to-r from-purple-400 to-pink-500';
      case 'rare':
        return 'bg-gradient-to-r from-blue-400 to-cyan-500';
      default:
        return 'bg-gradient-to-r from-gray-400 to-gray-500';
    }
  };

  const getRarityIcon = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return <Crown className="h-6 w-6" />;
      case 'epic':
        return <Star className="h-6 w-6" />;
      case 'rare':
        return <Medal className="h-6 w-6" />;
      default:
        return <Award className="h-6 w-6" />;
    }
  };

  return (
    <Card className="relative overflow-hidden">
      <div className={`absolute inset-0 ${getRarityColor(badge.rarity)} opacity-10`} />
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getRarityIcon(badge.rarity)}
            <Badge variant="outline" className="capitalize">
              {badge.rarity}
            </Badge>
          </div>
        </div>
        <CardTitle className="text-lg">{badge.name}</CardTitle>
        <CardDescription>{badge.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground">
          <strong>Category:</strong> {badge.category}
        </div>
        {badge.unlocked_at && (
          <div className="text-sm text-muted-foreground mt-2">
            <strong>Unlocked:</strong> {new Date(badge.unlocked_at).toLocaleDateString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const LeaderboardItem: React.FC<{ entry: LeaderboardEntry; currentUserId?: string }> = ({
  entry,
  currentUserId
}) => {
  const isCurrentUser = entry.user_id === currentUserId;

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="h-5 w-5 text-yellow-500" />;
      case 2:
        return <Medal className="h-5 w-5 text-gray-400" />;
      case 3:
        return <Award className="h-5 w-5 text-amber-600" />;
      default:
        return <span className="text-lg font-bold text-muted-foreground">#{rank}</span>;
    }
  };

  return (
    <div className={`flex items-center justify-between p-4 rounded-lg border ${
      isCurrentUser ? 'bg-primary/5 border-primary' : 'bg-card'
    }`}>
      <div className="flex items-center gap-3">
        {getRankIcon(entry.rank || 0)}
        <div>
          <p className={`font-medium ${isCurrentUser ? 'text-primary' : ''}`}>
            {entry.name}
            {isCurrentUser && <span className="ml-2 text-xs">(You)</span>}
          </p>
          <p className="text-sm text-muted-foreground">{entry.department}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-bold">{entry.total_points.toLocaleString()} pts</p>
        <p className="text-sm text-muted-foreground">
          Level {entry.level} • {entry.badges_count} badges
        </p>
      </div>
    </div>
  );
};

export const GamificationDashboard: React.FC<GamificationDashboardProps> = ({ userId }) => {
  const { data: gamificationData, isLoading: gamificationLoading } = useUserGamification(userId);
  const { data: leaderboardData, isLoading: leaderboardLoading } = useLeaderboard();

  if (gamificationLoading || leaderboardLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Gamification Dashboard</CardTitle>
            <CardDescription>Loading your achievements...</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="h-20 bg-gray-100 animate-pulse rounded-lg" />
              <div className="h-32 bg-gray-100 animate-pulse rounded-lg" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const gamification = gamificationData?.data;
  const leaderboard = leaderboardData?.data;

  if (!gamification) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Gamification Dashboard</CardTitle>
          <CardDescription>Unable to load gamification data</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const nextLevelPoints = (gamification.current_level + 1) * 1000;
  const progressToNextLevel = (gamification.total_points / nextLevelPoints) * 100;

  return (
    <div className="space-y-6">
      {/* Points and Level Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Your Progress
          </CardTitle>
          <CardDescription>Track your learning achievements and progress</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">{gamification.total_points.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Total Points</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">Level {gamification.current_level}</div>
              <div className="text-sm text-muted-foreground">Current Level</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{gamification.badges.length}</div>
              <div className="text-sm text-muted-foreground">Badges Earned</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{gamification.streak_days}</div>
              <div className="text-sm text-muted-foreground">Day Streak</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress to Level {gamification.current_level + 1}</span>
              <span>{gamification.total_points}/{nextLevelPoints} pts</span>
            </div>
            <Progress value={Math.min(progressToNextLevel, 100)} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Badges and Leaderboard Tabs */}
      <Tabs defaultValue="badges" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="badges" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            Badges ({gamification.badges.length})
          </TabsTrigger>
          <TabsTrigger value="leaderboard" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Leaderboard
          </TabsTrigger>
        </TabsList>

        <TabsContent value="badges" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Badges</CardTitle>
              <CardDescription>Achievements you've earned through your learning journey</CardDescription>
            </CardHeader>
            <CardContent>
              {gamification.badges.length === 0 ? (
                <div className="text-center py-8">
                  <Trophy className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No badges earned yet. Keep learning to unlock achievements!</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {gamification.badges.map((badge) => (
                    <BadgeCard key={badge.id} badge={badge} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="leaderboard" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Leaderboard
              </CardTitle>
              <CardDescription>See how you rank among other learners</CardDescription>
            </CardHeader>
            <CardContent>
              {leaderboard?.leaderboard ? (
                <div className="space-y-2">
                  {leaderboard.leaderboard.map((entry, index) => (
                    <LeaderboardItem
                      key={entry.user_id}
                      entry={{ ...entry, rank: index + 1 }}
                      currentUserId={userId}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Leaderboard data not available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
