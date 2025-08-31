/**
 * Utility functions for time and duration formatting
 */

export const formatDuration = (seconds: number): string => {
  if (isNaN(seconds) || seconds < 0) return '0s';
  
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) {
    const remainingSeconds = seconds % 60;
    if (remainingSeconds < 5) { // Don't show seconds if less than 5
      return `${minutes}m`;
    }
    return `${minutes}m ${Math.round(remainingSeconds)}s`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (hours < 24) {
    if (remainingMinutes === 0) {
      return `${hours}h`;
    }
    return `${hours}h ${remainingMinutes}m`;
  }
  
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  if (remainingHours === 0) {
    return `${days}d`;
  }
  return `${days}d ${remainingHours}h`;
};

export const formatDurationMinutes = (minutes: number): string => {
  return formatDuration(minutes * 60);
};

export const getDurationInSeconds = (item: { 
  duration_seconds?: number; 
  duration_minutes?: number;
  end_time?: string | null;
  activities?: Array<{ duration_seconds?: number; duration_minutes?: number }>;
}): number => {
  // For ended sessions, use the session duration directly
  if (item.end_time && item.duration_seconds !== undefined) {
    return item.duration_seconds;
  }
  if (item.end_time && item.duration_minutes !== undefined) {
    return item.duration_minutes * 60;
  }
  
  // For active sessions or if session duration is not available, 
  // calculate from activities
  if (item.activities && item.activities.length > 0) {
    const totalSeconds = item.activities.reduce((total, activity) => {
      const activitySeconds = activity.duration_seconds || (activity.duration_minutes || 0) * 60;
      return total + activitySeconds;
    }, 0);
    return totalSeconds;
  }
  
  // Fallback to session duration properties
  if (item.duration_seconds !== undefined) {
    return item.duration_seconds;
  }
  if (item.duration_minutes !== undefined) {
    return item.duration_minutes * 60;
  }
  
  return 0;
};

export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

export const formatTime = (dateString: string): string => {
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });
};
