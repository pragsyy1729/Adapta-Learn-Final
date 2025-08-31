import { Button } from "@/components/ui/button";
import { Brain, Menu, X } from "lucide-react";
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import Notifications from "./Notifications";

const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [signedIn, setSignedIn] = useState(false);
  const [user, setUser] = useState<any>(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    setSignedIn(!!localStorage.getItem("token"));
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
    // Listen for storage changes (sign out in other tabs)
    const handler = () => {
      setSignedIn(!!localStorage.getItem("token"));
      const userData = localStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    };
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, []);

  const handleSignOut = async () => {
    try {
      const token = localStorage.getItem("token");
      if (token) {
        // Call the backend sign-out endpoint
        await fetch("/api/sign-out", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });
      }
    } catch (error) {
      console.error("Error signing out:", error);
    } finally {
      // Clear local storage and update state regardless of API success
      localStorage.clear();
      setSignedIn(false);
      toast({
        title: "Signed out successfully",
        description: "You have been signed out of your account.",
      });
      navigate("/");
    }
  };

  const navItems = [];

  // Add role-based navigation items
  if (user?.roleType === 'Manager') {
    navItems.push({ label: 'Manager Dashboard', href: '/manager' });
  } else if (user?.roleType === 'Hiring Manager' || user?.roleType === 'hiring_manager' || user?.roleType === 'Director') {
    navItems.push({ label: 'Hiring Manager Dashboard', href: '/hiring-manager' });
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-border/50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              LearnAI
            </span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item, index) => (
              <Link
                key={index}
                to={item.href}
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-smooth"
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-4">
            {signedIn ? (
              <>
                <Notifications userId={user?.user_id || ''} />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleSignOut}
                >
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Link to="/signin">
                  <Button variant="ghost" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Link to="/get-started">
                  <Button variant="hero" size="sm">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-border/50">
            <div className="flex flex-col gap-4">
              {navItems.map((item, index) => (
                <Link
                  key={index}
                  to={item.href}
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-smooth"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
              <div className="flex flex-col gap-2 pt-4 border-t border-border/50">
                {signedIn ? (
                  <>
                    <div className="px-2 py-1">
                      <Notifications userId={user?.user_id || ''} />
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="justify-start"
                      onClick={handleSignOut}
                    >
                      Sign Out
                    </Button>
                  </>
                ) : (
                  <>
                    <Link to="/signin">
                      <Button variant="ghost" size="sm" className="justify-start">
                        Sign In
                      </Button>
                    </Link>
                    <Link to="/get-started">
                      <Button variant="hero" size="sm" className="justify-start">
                        Get Started
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;