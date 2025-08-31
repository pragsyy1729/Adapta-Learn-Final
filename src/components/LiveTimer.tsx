import React from 'react';
import { Clock } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";

interface LiveTimerProps {
  seconds: number;
  activityType?: string;
  isActive: boolean;
  className?: string;
  variant?: 'compact' | 'full';
}

const LiveTimer: React.FC<LiveTimerProps> = ({ 
  seconds, 
  activityType, 
  isActive, 
  className = '',
  variant = 'compact'
}) => {
  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    if (minutes < 60) {
      return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  if (variant === 'compact') {
    return (
      <div className={`inline-flex items-center space-x-2 px-3 py-2 rounded-lg border ${
        isActive 
          ? 'bg-learning-primary/10 border-learning-primary/30 text-learning-primary' 
          : 'bg-muted border-muted-foreground/20 text-muted-foreground'
      } ${className}`}>
        <Clock className={`w-4 h-4 ${isActive ? 'animate-pulse' : ''}`} />
        <span className="text-sm font-medium">{formatDuration(seconds)}</span>
        {isActive && <div className="w-2 h-2 bg-learning-primary rounded-full animate-pulse" />}
      </div>
    );
  }

  return (
    <Card className={`${className}`}>
      <CardContent className="p-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${
            isActive 
              ? 'bg-learning-primary/10 text-learning-primary' 
              : 'bg-muted text-muted-foreground'
          }`}>
            <Clock className={`w-5 h-5 ${isActive ? 'animate-pulse' : ''}`} />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-foreground">
                  {isActive ? 'Active Session' : 'Time Spent'}
                </p>
                {activityType && (
                  <p className="text-xs text-muted-foreground capitalize">
                    {activityType.replace(/_/g, ' ')}
                  </p>
                )}
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-foreground">{formatDuration(seconds)}</p>
                {isActive && (
                  <div className="flex items-center justify-end space-x-1">
                    <div className="w-2 h-2 bg-learning-primary rounded-full animate-pulse" />
                    <span className="text-xs text-learning-primary">Live</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LiveTimer;
