import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import LiveTimer from "@/components/LiveTimer";
import { useSessionTracking } from "@/hooks/useSessionTracking";
import HomeTab from "./DashboardHomeTab";
import LearningPathsTab from "./DashboardLearningPathsTab";
import CollaborationTab from "./DashboardCollaborationTab";
import DashboardMyProfileTab from "./DashboardMyProfileTab";
import ConversationAgent from "@/components/ConversationAgent";
import { RecommendationsPanel } from "@/components/RecommendationsPanel";
import { GamificationDashboard } from "@/components/GamificationDashboard";

const Dashboard = () => {
  const [tab, setTab] = useState("home");
  const [learningStyle, setLearningStyle] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  
  // Get user from localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      console.log('Dashboard - User loaded:', parsedUser);
      console.log('Dashboard - User department:', parsedUser?.profile?.department || parsedUser?.department);
    }
  }, []);
  
  const userId = user?.user_id || ''; // Don't use fallback user_001
  const userDepartment = user?.profile?.department || user?.department || '';
  const userDepartmentId = user?.profile?.department_id || user?.department_id || '';
  const { 
    trackActivity, 
    liveTimer, 
    currentActivityType 
  } = useSessionTracking(userId);

  useEffect(() => {
    const style = localStorage.getItem("learningStyle");
    setLearningStyle(style);
    
    // Only track dashboard activity if we have a valid user
    if (user?.user_id) {
      trackActivity('dashboard_view');
    }
  }, [user]);

  const handleTabChange = (newTab: string) => {
    setTab(newTab);
    // Track tab navigation activities
    switch(newTab) {
      case 'home':
        trackActivity('dashboard_home_view');
        break;
      case 'learning':
        trackActivity('learning_paths_view');
        break;
      case 'gamification':
        trackActivity('gamification_view');
        break;
      case 'recommendations':
        trackActivity('recommendations_view');
        break;
      case 'profile':
        trackActivity('profile_view');
        break;
      case 'collab':
        trackActivity('collaboration_view');
        break;
    }
  };

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-gradient-to-br from-background to-muted/30 py-20">
        <div className="max-w-7xl mx-auto px-6">
          {/* Live Timer at top right when active */}
          {currentActivityType && (
            <div className="fixed top-24 right-6 z-10">
              <LiveTimer
                seconds={liveTimer}
                activityType={currentActivityType}
                isActive={true}
                variant="compact"
              />
            </div>
          )}
          
          {learningStyle && (
            <div className="mb-6 p-4 rounded bg-primary/10 border border-primary text-primary font-semibold text-center">
              Your learning style: <span className="font-bold">{learningStyle}</span>
              {learningStyle === "Visual" && <span> 4c8 Visual learners benefit from diagrams, charts, and images.</span>}
              {learningStyle === "Aural" && <span> 3a7 Aural learners benefit from listening and discussions.</span>}
              {learningStyle === "Read/Write" && <span> 4dd Read/Write learners benefit from reading and note-taking.</span>}
              {learningStyle === "Kinesthetic" && <span> 9be Kinesthetic learners benefit from hands-on activities.</span>}
            </div>
          )}
          <div className="flex gap-4 mb-8 border-b overflow-x-auto">
            <button className={`px-4 py-2 font-semibold whitespace-nowrap ${tab === "home" ? "border-b-2 border-primary" : "text-muted-foreground"}`} onClick={() => handleTabChange("home")}>Home</button>
            <button className={`px-4 py-2 font-semibold whitespace-nowrap ${tab === "learning" ? "border-b-2 border-primary" : "text-muted-foreground"}`} onClick={() => handleTabChange("learning")}>Learning Paths</button>
            <button className={`px-4 py-2 font-semibold whitespace-nowrap ${tab === "gamification" ? "border-b-2 border-primary" : "text-muted-foreground"}`} onClick={() => handleTabChange("gamification")}>Achievements</button>
            <button className={`px-4 py-2 font-semibold whitespace-nowrap ${tab === "recommendations" ? "border-b-2 border-primary" : "text-muted-foreground"}`} onClick={() => handleTabChange("recommendations")}>Recommendations</button>
            <button className={`px-4 py-2 font-semibold whitespace-nowrap ${tab === "profile" ? "border-b-2 border-primary" : "text-muted-foreground"}`} onClick={() => handleTabChange("profile")}>My Profile</button>
            <button className={`px-4 py-2 font-semibold whitespace-nowrap ${tab === "collab" ? "border-b-2 border-primary" : "text-muted-foreground"}`} onClick={() => handleTabChange("collab")}>Collaboration</button>
          </div>
          {tab === "home" && <HomeTab />}
          {tab === "learning" && <LearningPathsTab />}
          {tab === "gamification" && <GamificationDashboard userId={userId} />}
          {tab === "recommendations" && <RecommendationsPanel userId={userId} />}
          {tab === "profile" && <DashboardMyProfileTab />}
          {tab === "collab" && <CollaborationTab />}
        </div>
      </div>

      {/* Conversation Agent - Available on all dashboard pages */}
      <ConversationAgent
        departmentId={userDepartmentId}
        departmentName={userDepartment}
        userId={userId}
      />
    </>
  );
};

export default Dashboard;
