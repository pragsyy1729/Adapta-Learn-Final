import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { validateEmail } from "@/utils/validation";
import { Loader2 } from "lucide-react";

const SignIn = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const navigate = useNavigate();

  const handleEmailChange = (value: string) => {
    setEmail(value);
    setFieldErrors(prev => ({ ...prev, email: '' }));
    
    if (value) {
      const emailValidation = validateEmail(value);
      if (!emailValidation.isValid) {
        setFieldErrors(prev => ({ ...prev, email: emailValidation.error || '' }));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setFieldErrors({});
    
    // Client-side validation
    const errors: Record<string, string> = {};
    
    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) {
      errors.email = emailValidation.error || 'Invalid email';
    }
    
    if (!password) {
      errors.password = 'Password is required';
    }
    
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }
    
    try {
      setIsLoading(true);
      const res = await fetch("/api/sign-in", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Sign in failed");
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      // Redirect based on newJoiner and roleType in user profile
      const roleType = data.user?.roleType;
      const newJoiner = data.user?.newJoiner === "Yes";
      if (newJoiner) {
        navigate("/dashboard");
      } else if (roleType === "Manager") {
        navigate("/manager");
      } else if (roleType === "Hiring Manager" || roleType === "Director") {
        navigate("/hiring-manager");
      } else if (roleType === "Admin") {
        navigate("/admin");
      } else {
        navigate("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Sign in failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-background to-muted/30">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h2 className="text-3xl font-bold mb-6 text-center">Sign In</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={e => handleEmailChange(e.target.value)}
              required
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                fieldErrors.email ? 'border-red-500' : ''
              }`}
            />
            {fieldErrors.email && <div className="text-red-500 text-sm mt-1">{fieldErrors.email}</div>}
          </div>
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => {
                setPassword(e.target.value);
                setFieldErrors(prev => ({ ...prev, password: '' }));
              }}
              required
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                fieldErrors.password ? 'border-red-500' : ''
              }`}
            />
            {fieldErrors.password && <div className="text-red-500 text-sm mt-1">{fieldErrors.password}</div>}
          </div>
          {error && <div className="text-red-500 text-sm bg-red-50 p-3 rounded-lg">{error}</div>}
          <Button 
            variant="hero" 
            size="lg" 
            className="w-full" 
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </Button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <button
              onClick={() => navigate('/get-started')}
              className="text-primary hover:underline font-medium"
            >
              Get Started
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
