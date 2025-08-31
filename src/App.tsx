import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import SignIn from "./pages/SignIn";
import GetStarted from "./pages/GetStarted";
import Dashboard from "./pages/Dashboard";
import ManagerView from "./pages/ManagerView";
import HiringManagerView from "./pages/HiringManagerView";
import AdminView from "./pages/AdminView";
import VARKQuiz from "./pages/VARKQuiz";
import OnboardingWorkflow from "./pages/OnboardingWorkflow";
import LearningPathModules from "./pages/LearningPathModules";
import ModuleChapters from "./pages/ModuleChapters";
import QuizInterface from "./pages/QuizInterface";
import AdminRecommendationsManager from "./pages/AdminRecommendationsManager";
import UserDetailView from "./pages/UserDetailView";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/get-started" element={<GetStarted />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/onboarding-workflow" element={<OnboardingWorkflow />} />
          <Route path="/vark-quiz" element={<VARKQuiz />} />
          <Route path="/manager" element={<ManagerView />} />
          <Route path="/manager/user/:userId" element={<UserDetailView />} />
          <Route path="/hiring-manager" element={<HiringManagerView />} />
          <Route path="/admin" element={<AdminView />} />
          <Route path="/learning-path/:pathId/modules" element={<LearningPathModules />} />
          <Route path="/learning-path/:pathId" element={<LearningPathModules />} />
          <Route path="/learning-path/:pathId/module/:moduleId" element={<ModuleChapters />} />
          <Route path="/quiz/:quizId" element={<QuizInterface />} />
          <Route path="/admin/recommendations" element={<AdminRecommendationsManager />} />
          <Route path="/user-detail" element={<UserDetailView />} />
          {/* Role-based views are now only accessible after sign-in/onboarding */}
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
