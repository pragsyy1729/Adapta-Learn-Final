import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import Dashboard from "@/components/Dashboard";

import { useEffect, useState } from "react";

const Index = () => {
  const [showDashboard, setShowDashboard] = useState(false);
  useEffect(() => {
    // Example: set newJoiner flag in localStorage after sign-in or onboarding
    // Here, we just read it for demo. Replace with real user/session logic.
    const isNewJoiner = localStorage.getItem("newJoiner");
    setShowDashboard(isNewJoiner === "true" || isNewJoiner === "1" || isNewJoiner === "yes");
  }, []);
  return (
    <div className="min-h-screen">
      <Navigation />
      <Hero />
      {showDashboard && <Dashboard />}
    </div>
  );
};

export default Index;
