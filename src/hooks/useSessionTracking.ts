import { useState, useEffect, useRef, useCallback } from 'react';

interface Activity {
  activity_type: string;
  learning_path_id?: string;
  module_id?: string;
  start_time: string;
  end_time?: string;
  duration_seconds: number;
}

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
    duration_seconds: number;
    activities: Activity[];
  }>;
}

export const useSessionTracking = (userId: string) => {
  // Session tracking API base URL. Default to session tracking server on port 5001.
  // Prefer Vite env var `VITE_SESSION_API_URL` when set; fallback to localhost:5001.
  // Note: `process.env` is not available in the browser with Vite.
  const BASE_SESSION_API_URL = ((import.meta as any).env?.VITE_SESSION_API_URL || 'http://localhost:5001').replace(/\/$/, '');
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isTracking, setIsTracking] = useState(false);
  const [currentActivityType, setCurrentActivityType] = useState<string | null>(null);
  const [activityStartTime, setActivityStartTime] = useState<Date | null>(null);
  const [liveTimer, setLiveTimer] = useState<number>(0); // Live timer in seconds
  
  const sessionStartTime = useRef<Date | null>(null);
  const currentActivity = useRef<string | null>(null);
  const timerInterval = useRef<NodeJS.Timeout | null>(null);
  const updateInterval = useRef<NodeJS.Timeout | null>(null);
  const trackingInProgress = useRef<boolean>(false);

  // Don't allow session tracking for invalid/default userIds
  const isValidUserId = userId && userId.trim() !== '' && userId !== 'user_001' && !userId.includes('user_001') && userId !== 'undefined' && userId !== 'null';

  // Update activity progress without ending it
  const updateActivityProgress = useCallback(async () => {
    if (!currentSessionId || !currentActivityType || !activityStartTime || !isValidUserId) {
      console.log('Skipping activity update - missing requirements:', {
        hasSessionId: !!currentSessionId,
        hasActivityType: !!currentActivityType,
        hasStartTime: !!activityStartTime,
        isValidUser: isValidUserId,
        userId: userId
      });
      return;
    }

    console.log('Updating activity progress for session:', currentSessionId);
    try {
  const response = await fetch(`${BASE_SESSION_API_URL}/api/sessions/update-activity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: currentSessionId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Activity progress updated successfully:', data);
      } else {
        console.error('Failed to update activity progress:', response.status);
      }
    } catch (error) {
      console.error('Error updating activity progress:', error);
    }
  }, [userId, currentSessionId, isValidUserId]);

  // Live timer effect
  useEffect(() => {
    if (activityStartTime && currentActivityType) {
      console.log('Setting up live timer for activity:', currentActivityType);
      
      // Update timer every second
      timerInterval.current = setInterval(() => {
        const now = new Date();
        const elapsed = Math.floor((now.getTime() - activityStartTime.getTime()) / 1000);
        setLiveTimer(elapsed);
      }, 1000);

      // Save progress every 30 seconds
      updateInterval.current = setInterval(() => {
        console.log('30-second interval triggered - calling updateActivityProgress');
        updateActivityProgress();
      }, 30000);

      console.log('Live timer and update interval started');

      return () => {
        console.log('Cleaning up timers for:', currentActivityType);
        if (timerInterval.current) {
          clearInterval(timerInterval.current);
        }
        if (updateInterval.current) {
          clearInterval(updateInterval.current);
        }
      };
    } else {
      setLiveTimer(0);
      if (timerInterval.current) {
        clearInterval(timerInterval.current);
      }
      if (updateInterval.current) {
        clearInterval(updateInterval.current);
      }
    }
  }, [activityStartTime, currentActivityType, updateActivityProgress]);

  // Update activity progress without ending it
  // Start a new session
  const startSession = async (): Promise<string | null> => {
    // Don't start session for invalid users
    if (!isValidUserId) {
      console.log('Skipping session start - invalid userId:', userId);
      return null;
    }

    // Don't start new session if we already have one
    if (currentSessionId) {
      console.log('Session already exists:', currentSessionId);
      return currentSessionId;
    }

    try {
      console.log('Starting session for user:', userId);
      
  const response = await fetch(`${BASE_SESSION_API_URL}/api/sessions/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (response.ok) {
        const data = await response.json();
        const sessionId = data.session_id;
        setCurrentSessionId(sessionId);
        setIsTracking(true);
        sessionStartTime.current = new Date();
        
        if (data.existing_session) {
          console.log('Resumed existing session:', sessionId);
        } else {
          console.log('New session started:', sessionId);
        }
        
        return sessionId;
      } else {
        const errorText = await response.text();
        console.error('Failed to start session:', response.status, errorText);
        return null;
      }
    } catch (error) {
      console.error('Error starting session:', error);
      return null;
    }
  };

  // End the current activity
  const endActivity = async () => {
    if (!currentSessionId || !currentActivity.current) return;

    try {
  const response = await fetch(`${BASE_SESSION_API_URL}/api/sessions/end-activity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: currentSessionId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Activity ended:', data.activity_ended, 'Duration:', data.duration_seconds, 'seconds (', data.duration_minutes, 'minutes)');
        
        // Reset activity state
        currentActivity.current = null;
        setCurrentActivityType(null);
        setActivityStartTime(null);
        setLiveTimer(0);
        
        // Reset tracking flags
        trackingInProgress.current = false;
        
        // Clear timers
        if (timerInterval.current) {
          clearInterval(timerInterval.current);
          timerInterval.current = null;
        }
        if (updateInterval.current) {
          clearInterval(updateInterval.current);
          updateInterval.current = null;
        }
      }
    } catch (error) {
      console.error('Error ending activity:', error);
    }
  };

  // End the current session
  const endSession = async () => {
    if (!currentSessionId) return;

    // First end any ongoing activity
    await endActivity();

    try {
  const response = await fetch(`${BASE_SESSION_API_URL}/api/sessions/end`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: currentSessionId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSessionId(null);
        setIsTracking(false);
        sessionStartTime.current = null;
        console.log('Session ended. Duration:', data.duration_seconds, 'seconds (', data.duration_minutes, 'minutes)');
      }
    } catch (error) {
      console.error('Error ending session:', error);
    }
  };

  // Track an activity within the session
  const trackActivity = async (
    activityType: string,
    learningPathId?: string,
    moduleId?: string
  ) => {
    console.log('trackActivity called with:', {
      activityType,
      userId,
      isValidUserId,
      learningPathId,
      moduleId
    });

    // Don't track activity for invalid users
    if (!isValidUserId) {
      console.log('Skipping activity tracking - invalid userId:', userId);
      return;
    }

    // Simple check - if already tracking the exact same activity, skip
    const activityKey = `${activityType}:${learningPathId || ''}:${moduleId || ''}`;
    if (currentActivity.current === activityKey) {
      console.log('Same activity already being tracked, skipping');
      return;
    }

    // Simple tracking flag check
    if (trackingInProgress.current) {
      console.log('Another request in progress, skipping');
      return;
    }

    trackingInProgress.current = true;

    try {
      // Only start session if we don't have one
      let sessionId = currentSessionId;
      if (!sessionId) {
        console.log('No session, starting one for activity:', activityType);
        sessionId = await startSession();
        // Give the state time to update
        await new Promise(resolve => setTimeout(resolve, 200)); 
      }

      // Check if we have a session now
      if (!sessionId) {
        console.error('Failed to establish session for activity tracking - no session ID available');
        console.log('Debug: trackingInProgress:', trackingInProgress.current);
        console.log('Debug: userId:', userId);
        console.log('Debug: isValidUserId:', isValidUserId);
        return;
      }

      console.log('Tracking activity:', activityType, 'with session:', sessionId);

  const response = await fetch(`${BASE_SESSION_API_URL}/api/sessions/activity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          activity_type: activityType,
          learning_path_id: learningPathId,
          module_id: moduleId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Activity tracking response:', data);
        
        // Set up live tracking
        currentActivity.current = activityKey;
        setCurrentActivityType(activityType);
        setActivityStartTime(new Date());
        setLiveTimer(0);
      } else {
        const errorText = await response.text();
        console.error('Failed to track activity:', response.status, errorText);
      }
    } catch (error) {
      console.error('Error tracking activity:', error);
    } finally {
      trackingInProgress.current = false;
    }
  };

  // Get session statistics
  const getSessionStats = async (): Promise<SessionStats | null> => {
    if (!isValidUserId) {
      console.log('Skipping session stats - invalid userId:', userId);
      return null;
    }

    try {
  const response = await fetch(`${BASE_SESSION_API_URL}/api/sessions/stats/${userId}`);
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Error getting session stats:', error);
    }
    return null;
  };

  // Format duration for display
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

  // Auto-start session when component mounts - DISABLED to prevent runaway sessions
  useEffect(() => {
    // Don't auto-start session - let it start when user actually does an activity
    // startSession();

    // Auto-end session when page is closed/refreshed
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (currentSessionId && isValidUserId) {
        // Try to end session properly first
        endSession().catch(() => {
          // If fetch fails, fall back to sendBeacon
            navigator.sendBeacon(
            `${BASE_SESSION_API_URL}/api/sessions/end`,
            JSON.stringify({
              user_id: userId,
              session_id: currentSessionId,
            })
          );
        });
      }
    };

    const handleUnload = () => {
      if (currentSessionId && isValidUserId) {
        navigator.sendBeacon(
          `${BASE_SESSION_API_URL}/api/sessions/end`,
          JSON.stringify({
            user_id: userId,
            session_id: currentSessionId,
          })
        );
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('unload', handleUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('unload', handleUnload);
      if (isValidUserId) {
        endSession();
      }
    };
  }, [userId, isValidUserId]);

  // Track page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!isValidUserId) {
        console.log('Skipping visibility change handler - invalid userId:', userId);
        return;
      }

      if (document.hidden) {
        // Page is hidden, user might be inactive
        console.log('Page hidden - user inactive');
        updateActivityProgress(); // Save current progress
      } else {
        // Page is visible again
        console.log('Page visible - user active');
        // Don't start a new session if already tracking or if we already have a session
        if (!isTracking && userId && !currentSessionId && isValidUserId) {
          console.log('Visibility change: Starting session for valid user:', userId);
          startSession(); // Start new session only if not already tracking
        } else {
          console.log('Skipping session start on visibility change:', {
            isTracking,
            hasUserId: !!userId,
            hasSession: !!currentSessionId,
            isValidUser: isValidUserId
          });
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isTracking, userId, currentSessionId, updateActivityProgress, isValidUserId]);

  return {
    currentSessionId,
    isTracking,
    currentActivityType,
    liveTimer,
    formatDuration,
    startSession,
    endSession,
    endActivity,
    trackActivity,
    getSessionStats,
    updateActivityProgress,
  };
};
