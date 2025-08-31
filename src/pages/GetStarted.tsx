import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { validatePassword, validateEmail } from "@/utils/validation";
import PasswordStrength from "@/components/PasswordStrength";
import ProgressIndicator from "@/components/ProgressIndicator";
import { Loader2, ArrowLeft, ArrowRight } from "lucide-react";

const GetStarted = () => {
  const [form, setForm] = useState({
    name: "",
    employeeId: "",
    role: "",
    customRole: "",
    roleType: "",
    department: "",
    manager: "",
    dateOfJoining: "",
    email: "",
    password: "",
    gender: "",
    disabilities: "",
    college: "",
    latestDegree: "",
    cgpa: "",
    newJoiner: "",
    country: "",
    city: "",
    profilePicture: null,
  });
  const [managers, setManagers] = useState<{ name: string; email: string }[]>([]);
  const [availableRoles, setAvailableRoles] = useState<{ id?: string; role_id?: string; name?: string; role_name?: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingManagers, setLoadingManagers] = useState(false);
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [currentStep, setCurrentStep] = useState(1);

  const steps = [
    {
      id: 1,
      title: "Personal",
      description: "Basic info",
      fields: ["name", "employeeId", "email", "password", "gender", "dateOfJoining", "profilePicture"]
    },
    {
      id: 2,
      title: "Work",
      description: "Role details",
      fields: ["role", "roleType", "department", "manager", "newJoiner"]
    },
    {
      id: 3,
      title: "Education",
      description: "Background",
      fields: ["college", "latestDegree", "cgpa", "disabilities"]
    },
    {
      id: 4,
      title: "Location",
      description: "Address",
      fields: ["country", "city"]
    }
  ];

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    
    // Clear previous error for this field
    setFormErrors(prev => ({ ...prev, [name]: '' }));
    
    if (type === "file" && "files" in e.target) {
      const fileList = (e.target as HTMLInputElement).files;
      const file = fileList?.[0] || null;
      
      // Validate file for profile picture
      if (file && name === "profilePicture") {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        
        if (file.size > maxSize) {
          setFormErrors(prev => ({ ...prev, [name]: 'File size must be less than 5MB' }));
          return;
        }
        
        if (!allowedTypes.includes(file.type)) {
          setFormErrors(prev => ({ ...prev, [name]: 'Only JPEG, PNG, and GIF images are allowed' }));
          return;
        }
      }
      
      setForm((prev) => ({
        ...prev,
        [name]: file,
      }));
    } else {
      // Real-time validation
      if (name === 'email') {
        const emailValidation = validateEmail(value);
        if (!emailValidation.isValid && value) {
          setFormErrors(prev => ({ ...prev, [name]: emailValidation.error || '' }));
        }
      }
      
      if (name === 'password') {
        const passwordValidation = validatePassword(value);
        if (!passwordValidation.isValid && value) {
          setFormErrors(prev => ({ ...prev, [name]: 'Password does not meet requirements' }));
        }
      }
      
      setForm((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
    
    if (name === "department" && value) {
      // Fetch managers for selected department
      setLoadingManagers(true);
      (async () => {
        try {
          const res = await fetch(`/api/user/managers/list?department=${encodeURIComponent(value)}`);
          const data = await res.json();
          // Expect envelope { success: true, data: [...] }
          if (data && data.success && Array.isArray(data.data)) {
            setManagers(data.data);
          } else {
            setManagers([]);
          }
        } catch {
          setManagers([]);
        } finally {
          setLoadingManagers(false);
        }
      })();
      
      setForm((prev) => ({ ...prev, manager: "" }));
    }
  };  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Fetch all available roles when component mounts
  useEffect(() => {
    const fetchRoles = async () => {
      setLoadingRoles(true);
      try {
        // Try the simple roles API first
        const res = await fetch('/api/roles');
        if (res.ok) {
          const roles = await res.json();
          setAvailableRoles(roles || []);
        } else {
          // Fallback to the onboarding API
          const fallbackRes = await fetch('/api/onboarding/roles');
          const fallbackData = await fallbackRes.json();
          if (fallbackData.success) {
            setAvailableRoles(fallbackData.data || []);
          }
        }
      } catch (error) {
        console.error('Failed to fetch roles:', error);
        setAvailableRoles([]);
      } finally {
        setLoadingRoles(false);
      }
    };

    fetchRoles();
  }, []);

  const validateCurrentStep = (): boolean => {
    const currentStepFields = steps[currentStep - 1].fields;
    const errors: Record<string, string> = {};

    currentStepFields.forEach(field => {
      if (field === 'email') {
        const emailValidation = validateEmail(form.email);
        if (!emailValidation.isValid && form.email) {
          errors.email = emailValidation.error || 'Invalid email';
        }
      } else if (field === 'password') {
        const passwordValidation = validatePassword(form.password);
        if (!passwordValidation.isValid && form.password) {
          errors.password = 'Password does not meet requirements';
        }
      } else if (!form[field as keyof typeof form] && field !== 'disabilities' && field !== 'profilePicture') {
        errors[field] = 'This field is required';
      }
    });

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // After signup: call onboarding analyze then auto-enroll endpoints (best-effort)
  const performAnalyzeAndAutoEnroll = async (userId: string) => {
    try {
      if (!userId) return;

      const targetRole = form.role === 'Other' ? (form.customRole || form.role) : (form.role || form.customRole);

      const analyzePayload = {
        user_id: userId,
        department: form.department,
        target_role: targetRole
      };

      console.log('Calling /api/onboarding/analyze with', analyzePayload);
      const analyzeRes = await fetch('/api/onboarding/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analyzePayload)
      });
      const analyzeData = await analyzeRes.json().catch(() => ({}));
      console.log('onboarding/analyze ->', analyzeRes.status, analyzeData);

      if (!analyzeRes.ok) {
        // Don't block the user if analyze fails; just log and continue
        console.warn('onboarding analyze failed:', analyzeData);
      }

      // After analyze (or attempt), call auto-enroll in onboarding namespace
      console.log('Calling /api/onboarding/auto-enroll-from-onboarding for', userId);
      const enrollRes = await fetch('/api/onboarding/auto-enroll-from-onboarding', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      const enrollData = await enrollRes.json().catch(() => ({}));
      console.log('onboarding/auto-enroll ->', enrollRes.status, enrollData);

      if (!enrollRes.ok) {
        console.warn('auto-enroll failed:', enrollData);
      }
    } catch (e) {
      console.warn('performAnalyzeAndAutoEnroll error', e);
    }
  };

  const handleNext = () => {
    if (validateCurrentStep() && currentStep < steps.length) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
      setFormErrors({});
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <input 
              name="name" 
              type="text" 
              placeholder="Full Name" 
              value={form.name} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.name ? 'border-red-500' : ''
              }`}
            />
            {formErrors.name && <div className="text-red-500 text-sm mt-1">{formErrors.name}</div>}
            
            <input 
              name="employeeId" 
              type="text" 
              placeholder="Employee ID" 
              value={form.employeeId} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.employeeId ? 'border-red-500' : ''
              }`}
            />
            {formErrors.employeeId && <div className="text-red-500 text-sm mt-1">{formErrors.employeeId}</div>}
            
            <div>
              <input 
                name="email" 
                type="email" 
                placeholder="Email ID" 
                value={form.email} 
                onChange={handleChange} 
                required 
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  formErrors.email ? 'border-red-500' : ''
                }`}
              />
              {formErrors.email && <div className="text-red-500 text-sm mt-1">{formErrors.email}</div>}
            </div>
            
            <div>
              <input 
                name="password" 
                type="password" 
                placeholder="Password" 
                value={form.password} 
                onChange={handleChange} 
                required 
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  formErrors.password ? 'border-red-500' : ''
                }`}
              />
              {formErrors.password && <div className="text-red-500 text-sm mt-1">{formErrors.password}</div>}
              <PasswordStrength password={form.password} />
            </div>
            
            <select 
              name="gender" 
              value={form.gender} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.gender ? 'border-red-500' : ''
              }`}
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
              <option value="Prefer not to say">Prefer not to say</option>
            </select>
            {formErrors.gender && <div className="text-red-500 text-sm mt-1">{formErrors.gender}</div>}
            
            <input 
              name="dateOfJoining" 
              type="date" 
              placeholder="Date of Joining" 
              value={form.dateOfJoining} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.dateOfJoining ? 'border-red-500' : ''
              }`}
            />
            {formErrors.dateOfJoining && <div className="text-red-500 text-sm mt-1">{formErrors.dateOfJoining}</div>}
            
            <div>
              <label className="block mb-1 text-sm font-medium">Profile Picture (Optional)</label>
              <input 
                name="profilePicture" 
                type="file" 
                accept=".jpg,.jpeg,.png,.gif" 
                onChange={handleChange} 
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  formErrors.profilePicture ? 'border-red-500' : ''
                }`}
              />
              {formErrors.profilePicture && <div className="text-red-500 text-sm mt-1">{formErrors.profilePicture}</div>}
              <div className="text-xs text-muted-foreground mt-1">
                Supported formats: JPEG, PNG, GIF (max 5MB)
              </div>
            </div>
          </div>
        );
      
      case 2:
        return (
          <div className="space-y-4">
            <input 
              name="department" 
              type="text" 
              placeholder="Department" 
              value={form.department} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.department ? 'border-red-500' : ''
              }`}
            />
            {formErrors.department && <div className="text-red-500 text-sm mt-1">{formErrors.department}</div>}
            
            <div>
              <select 
                name="role" 
                value={form.role} 
                onChange={handleChange} 
                required 
                disabled={loadingRoles}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  formErrors.role ? 'border-red-500' : ''
                }`}
              >
                <option value="">
                  {loadingRoles ? "Loading roles..." : "Select Role"}
                </option>
                {availableRoles.map((role) => (
                  <option key={role.id || role.role_id} value={role.name || role.role_name}>
                    {role.name || role.role_name}
                  </option>
                ))}
                <option value="Other">Other (specify below)</option>
              </select>
              {formErrors.role && <div className="text-red-500 text-sm mt-1">{formErrors.role}</div>}
            </div>
            
            {form.role === "Other" && (
              <input 
                name="customRole" 
                type="text" 
                placeholder="Please specify your role" 
                value={form.customRole || ''} 
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            )}
            
            <select 
              name="roleType" 
              value={form.roleType} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.roleType ? 'border-red-500' : ''
              }`}
            >
              <option value="">Select Role Type</option>
              <option value="Associate">Associate</option>
              <option value="Lead">Lead</option>
              <option value="Specialist">Specialist</option>
              <option value="Senior">Senior</option>
              <option value="VP">VP</option>
              <option value="Manager">Manager</option>
              <option value="Hiring Manager">Hiring Manager</option>
              <option value="Admin">Admin</option>
            </select>
            {formErrors.roleType && <div className="text-red-500 text-sm mt-1">{formErrors.roleType}</div>}
            
            <select
              name="manager"
              value={form.manager}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={!form.department || loadingManagers}
            >
              <option value="">
                {loadingManagers ? "Loading managers..." : "Select Manager"}
              </option>
              <option value="Other">Other</option>
              {managers.map((m) => (
                <option key={m.email} value={m.name}>{m.name}</option>
              ))}
            </select>
            {formErrors.manager && <div className="text-red-500 text-sm mt-1">{formErrors.manager}</div>}
            
            <div>
              <label className="block mb-1 text-sm font-medium">Are you a New Joiner?</label>
              <select 
                name="newJoiner" 
                value={form.newJoiner} 
                onChange={handleChange} 
                required 
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                  formErrors.newJoiner ? 'border-red-500' : ''
                }`}
              >
                <option value="">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
              {formErrors.newJoiner && <div className="text-red-500 text-sm mt-1">{formErrors.newJoiner}</div>}
            </div>
          </div>
        );
      
      case 3:
        return (
          <div className="space-y-4">
            <input 
              name="college" 
              type="text" 
              placeholder="College/University" 
              value={form.college} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.college ? 'border-red-500' : ''
              }`}
            />
            {formErrors.college && <div className="text-red-500 text-sm mt-1">{formErrors.college}</div>}
            
            <input 
              name="latestDegree" 
              type="text" 
              placeholder="Latest Degree" 
              value={form.latestDegree} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.latestDegree ? 'border-red-500' : ''
              }`}
            />
            {formErrors.latestDegree && <div className="text-red-500 text-sm mt-1">{formErrors.latestDegree}</div>}
            
            <input 
              name="cgpa" 
              type="text" 
              placeholder="CGPA/GPA" 
              value={form.cgpa} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.cgpa ? 'border-red-500' : ''
              }`}
            />
            {formErrors.cgpa && <div className="text-red-500 text-sm mt-1">{formErrors.cgpa}</div>}
            
            <input 
              name="disabilities" 
              type="text" 
              placeholder="Disabilities or Special Needs (Optional)" 
              value={form.disabilities} 
              onChange={handleChange} 
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        );
      
      case 4:
        return (
          <div className="space-y-4">
            <select 
              name="country" 
              value={form.country} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.country ? 'border-red-500' : ''
              }`}
            >
              <option value="">Select Country</option>
              <option value="India">India</option>
              <option value="USA">USA</option>
              <option value="France">France</option>
            </select>
            {formErrors.country && <div className="text-red-500 text-sm mt-1">{formErrors.country}</div>}
            
            <select 
              name="city" 
              value={form.city} 
              onChange={handleChange} 
              required 
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
                formErrors.city ? 'border-red-500' : ''
              }`}
            >
              <option value="">Select City</option>
              {form.country === "India" && (
                <>
                  <option value="Chennai">Chennai</option>
                  <option value="Bengaluru">Bengaluru</option>
                </>
              )}
              {form.country === "USA" && (
                <>
                  <option value="New York">New York</option>
                  <option value="San Francisco">San Francisco</option>
                </>
              )}
              {form.country === "France" && (
                <>
                  <option value="Paris">Paris</option>
                  <option value="Lyon">Lyon</option>
                </>
              )}
            </select>
            {formErrors.city && <div className="text-red-500 text-sm mt-1">{formErrors.city}</div>}
          </div>
        );
      
      default:
        return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (currentStep < steps.length) {
      handleNext();
      return;
    }
    
    // Final validation before submission
    setError("");
    setFormErrors({});
    
    // Client-side validation
    const errors: Record<string, string> = {};
    
    // Email validation
    const emailValidation = validateEmail(form.email);
    if (!emailValidation.isValid) {
      errors.email = emailValidation.error || 'Invalid email';
    }
    
    // Password validation
    const passwordValidation = validatePassword(form.password);
    if (!passwordValidation.isValid) {
      errors.password = 'Password does not meet requirements';
    }
    
    // Required field validation
    const requiredFields = ['name', 'employeeId', 'role', 'roleType', 'department', 'dateOfJoining', 'gender', 'college', 'latestDegree', 'cgpa', 'country', 'city', 'newJoiner'];
    
    requiredFields.forEach(field => {
      if (!form[field as keyof typeof form]) {
        errors[field] = 'This field is required';
      }
    });
    
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      // Go back to the step with errors
      for (let i = 0; i < steps.length; i++) {
        const stepFields = steps[i].fields;
        const hasErrorInStep = stepFields.some(field => errors[field]);
        if (hasErrorInStep) {
          setCurrentStep(i + 1);
          break;
        }
      }
      return;
    }
    
    try {
      setIsLoading(true);
      // Prepare form data (excluding profile picture for now)
      const payload = { ...form };
      delete payload.profilePicture;
      const res = await fetch("/api/get-started", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Registration failed");
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      // Best-effort: analyze onboarding and auto-enroll recommended learning paths
      try {
        performAnalyzeAndAutoEnroll(data.user?.user_id);
      } catch (e) {
        console.warn('Post-signup onboarding analyze/enroll failed', e);
      }
      // Redirect based on newJoiner and roleType
      const roleType = form.roleType;
      const newJoiner = form.newJoiner === "Yes";
      if (newJoiner) {
        navigate("/onboarding-workflow");
      } else if (roleType === "Manager") {
        navigate("/manager");
      } else if (roleType === "Hiring Manager") {
        navigate("/hiring-manager");
      } else if (roleType === "Admin") {
        navigate("/admin");
      } else {
        navigate("/dashboard");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err || 'Registration failed');
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-background to-muted/30">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl">
        <h2 className="text-3xl font-bold mb-6 text-center">Get Started</h2>
        
        <ProgressIndicator 
          currentStep={currentStep}
          totalSteps={steps.length}
          steps={steps}
        />
        
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="min-h-96">
            <h3 className="text-xl font-semibold mb-4">
              {steps[currentStep - 1].title} Information
            </h3>
            <p className="text-muted-foreground mb-6">
              {steps[currentStep - 1].description}
            </p>
            
            {renderStepContent()}
          </div>
          
          {error && <div className="text-red-500 text-sm bg-red-50 p-3 rounded-lg">{error}</div>}
          
          <div className="flex justify-between space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Previous</span>
            </Button>
            
            <Button 
              variant="hero" 
              size="lg" 
              type="submit"
              disabled={isLoading}
              className="flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creating Account...</span>
                </>
              ) : currentStep === steps.length ? (
                <span>Submit</span>
              ) : (
                <>
                  <span>Next</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default GetStarted;
