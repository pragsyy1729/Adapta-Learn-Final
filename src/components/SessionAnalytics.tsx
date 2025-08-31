import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Clock, BarChart3, TrendingUp, User } from "lucide-react";
import { formatDuration, getDurationInSeconds, formatDateTime } from "@/utils/timeUtils";

interface SessionStats {
  total_sessions: number;
  total_time_spent_seconds: number;
  total_time_spent_minutes: number;
  average_session_duration: number;
  last_activity: string;
  sessions: Array<{
    session_id: string;
    start_time: string;
    end_time?: string;
    duration_seconds?: number;
    duration_minutes?: number; // For backward compatibility
    activities: Array<{
      activity_type: string;
      learning_path_id?: string;
      module_id?: string;
      start_time: string;
      duration_seconds?: number;
      duration_minutes?: number; // For backward compatibility
    }>;
  }>;
}

interface SessionAnalyticsProps {
  userId: string;
}

const SessionAnalytics: React.FC<SessionAnalyticsProps> = ({ userId }) => {
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [loading, setLoading] = useState(true);
  // Vite exposes env vars via import.meta.env (prefixed with VITE_)
  const BASE_SESSION_API_URL = ((import.meta as any).env?.VITE_SESSION_API_URL || 'http://localhost:5001').replace(/\/$/, '');

  const fetchStats = async () => {
    if (!userId || userId.trim() === '') {
      console.log('Skipping session stats fetch - no valid userId:', userId);
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
  const response = await fetch(`${BASE_SESSION_API_URL}/api/sessions/stats/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching session stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!userId || userId.trim() === '') {
      setLoading(false);
      return;
    }
    
    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [userId]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Session Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">Loading session data...</div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Session Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">No session data available</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_sessions}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatDuration(stats.total_time_spent_seconds || stats.total_time_spent_minutes * 60)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Session</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatDuration(stats.average_session_duration)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Activity</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm font-bold">
              {stats.last_activity ? formatDateTime(stats.last_activity) : 'Never'}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SessionAnalytics;
