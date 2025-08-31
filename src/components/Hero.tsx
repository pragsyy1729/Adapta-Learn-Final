import { Button } from "@/components/ui/button";
import { Brain, Target, TrendingUp, Users } from "lucide-react";
import heroImage from "@/assets/hero-learning.jpg";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background with gradient overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${heroImage})` }}
      />
      <div className="absolute inset-0 bg-gradient-hero opacity-90" />
      
      {/* Floating elements */}
      <div className="absolute top-20 left-10 w-16 h-16 bg-white/10 rounded-full animate-float" />
      <div className="absolute top-40 right-20 w-12 h-12 bg-white/20 rounded-lg animate-float" style={{ animationDelay: '1s' }} />
      <div className="absolute bottom-32 left-20 w-8 h-8 bg-white/15 rounded-full animate-float" style={{ animationDelay: '2s' }} />
      
      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
        <div className="mb-8 inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 text-white/90 text-sm font-medium">
          <Brain className="w-4 h-4" />
          AI-Powered Learning Platform
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Personalized Learning
          <span className="block bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
            for Every New Hire
          </span>
        </h1>
        
        <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto leading-relaxed">
          Intelligent AI teaching assistant that adapts to each employee's learning style, 
          domain expertise, and progress to accelerate onboarding success.
        </p>
        
  {/* Removed Start Learning Journey and View Demo buttons as requested */}
        
        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <Target className="w-8 h-8 text-white mb-4 mx-auto" />
            <h3 className="text-lg font-semibold text-white mb-2">Role-Specific Content</h3>
            <p className="text-white/80 text-sm">Tailored curriculum based on department and position requirements</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <TrendingUp className="w-8 h-8 text-white mb-4 mx-auto" />
            <h3 className="text-lg font-semibold text-white mb-2">Adaptive Pacing</h3>
            <p className="text-white/80 text-sm">AI adjusts learning speed based on comprehension and progress</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;