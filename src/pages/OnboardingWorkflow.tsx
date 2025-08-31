import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  CheckCircle, 
  ArrowRight, 
  Upload, 
  FileText, 
  Target, 
  BookOpen, 
  Brain, 
  Users,
  AlertCircle,
  Loader2,
  TrendingUp,
  Award,
  MessageCircle
} from "lucide-react";
import ConversationAgent from "@/components/ConversationAgent";

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'skipped';
  required: boolean;
}

interface SkillGap {
  skill_name: string;
  current_level: number;
  required_level: number;
  gap: number;
  priority: 'high' | 'medium' | 'low';
}

interface LearningPath {
  id: string;
  title: string;
  description: string;
  estimated_duration: string;
  priority: number;
  is_mandatory: boolean;
}

const OnboardingWorkflow: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [user, setUser] = useState<any>(null);
  const [userDepartment, setUserDepartment] = useState<string>('');
  const [userRole, setUserRole] = useState<string>('');
  const [showRoleSelection, setShowRoleSelection] = useState(false);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [skillGaps, setSkillGaps] = useState<SkillGap[]>([]);
  const [recommendedPaths, setRecommendedPaths] = useState<LearningPath[]>([]);
  const [onboardingResult, setOnboardingResult] = useState<any>(null);
  
  const navigate = useNavigate();

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome & Overview',
      description: 'Introduction to the onboarding process',
      status: 'completed',
      required: true
    },
    {
      id: 'resume-upload',
      title: 'Resume Analysis',
      description: 'Upload your resume for skill assessment',
      status: 'in-progress',
      required: true
    },
    {
      id: 'skill-gap',
      title: 'Skill Gap Analysis',
      description: 'Identify your strengths and areas for growth',
      status: 'pending',
      required: true
    },
    {
      id: 'learning-paths',
      title: 'Learning Path Assignment',
      description: 'Auto-enroll in personalized learning paths',
      status: 'pending',
      required: true
    },
    {
      id: 'vark-quiz',
      title: 'Learning Style Assessment',
      description: 'Discover your optimal learning preferences',
      status: 'pending',
      required: true
    },
    {
      id: 'completion',
      title: 'Onboarding Complete',
      description: 'Ready to start your learning journey',
      status: 'pending',
      required: true
    }
  ];

  useEffect(() => {
    // Get user info from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      
      // Check if we have role and department info
      const existingRole = parsedUser.role || parsedUser.profile?.role;
      const existingDepartment = parsedUser.department || parsedUser.profile?.department;
      
      // Only use values if they're meaningful job functions, not just levels like "Associate"
      const isValidRole = existingRole && !['Associate', 'Senior', 'Lead', 'Manager', 'VP'].includes(existingRole);
      const isValidDepartment = existingDepartment && existingDepartment.trim().length > 0;
      
      if (isValidRole) {
        setUserRole(existingRole);
      }
      if (isValidDepartment) {
        setUserDepartment(existingDepartment);
      }
      
      // Show role selection if we don't have valid role/department
      if (!isValidRole || !isValidDepartment) {
        setShowRoleSelection(true);
      }
    }
  }, []);

  const handleResumeUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file
      const maxSize = 5 * 1024 * 1024; // 5MB
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      
      if (file.size > maxSize) {
        setError('File size must be less than 5MB');
        return;
      }
      
      if (!allowedTypes.includes(file.type)) {
        setError('Only PDF and Word documents are allowed. Your file type: ' + file.type);
        return;
      }
      
      // Additional check for file extension
      const fileExtension = file.name.toLowerCase().split('.').pop();
      if (!['pdf', 'doc', 'docx'].includes(fileExtension || '')) {
        setError('File must have a .pdf, .doc, or .docx extension');
        return;
      }
      
      setResumeFile(file);
      setError('');
      console.log('Resume file selected:', file.name, 'Type:', file.type, 'Size:', file.size);
    }
  };

  const processOnboarding = async () => {
    if (!resumeFile || !user) {
      setError('Resume file and user information are required');
      return;
    }

    // Validate that we have department and role
    if (!userDepartment || !userRole) {
      setError('Please select your department and role before proceeding');
      setShowRoleSelection(true);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Step 1: Upload and analyze resume
      setCurrentStep(2); // Move to skill gap analysis
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('user_id', user.user_id);
      formData.append('target_role', userRole);
      formData.append('department', userDepartment);

      // Debug: Log all FormData entries
      console.log('FormData contents:');
      for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`${key}:`, {
            name: value.name,
            size: value.size,
            type: value.type,
            lastModified: value.lastModified
          });
        } else {
          console.log(`${key}:`, value);
        }
      }

      console.log('Sending onboarding request with:', {
        user_id: user.user_id,
        target_role: userRole,
        department: userDepartment,
        resume_file: resumeFile.name,
        resume_type: resumeFile.type,
        resume_size: resumeFile.size
      });

      const analyzeResponse = await fetch('/api/onboarding/analyze', {
        method: 'POST',
        body: formData
      });

      console.log('Response status:', analyzeResponse.status);
      console.log('Response headers:', Object.fromEntries(analyzeResponse.headers.entries()));

      const responseData = await analyzeResponse.json();
      console.log('Response data:', responseData);

      if (!analyzeResponse.ok) {
        console.error('API Error:', responseData);
        throw new Error(responseData.error || `HTTP ${analyzeResponse.status}: Resume analysis failed`);
      }

      // Use responseData directly instead of calling json() again
      setOnboardingResult(responseData.data);
      
      if (responseData.data?.skill_gap_analysis) {
        setSkillGaps(responseData.data.skill_gap_analysis.gaps || []);
      }

      // Step 2: Auto-enroll user in recommended learning paths
      console.log('🎯 Starting auto-enrollment in recommended learning paths...');
      const userData = localStorage.getItem('user');
      if (userData) {
        const user = JSON.parse(userData);
        if (user.user_id) {
          const enrollmentResult = await autoEnrollInRecommendedPaths(user.user_id);
          if (enrollmentResult.success) {
            console.log('✅ Auto-enrollment completed successfully');
          } else {
            console.warn('⚠️ Auto-enrollment failed:', enrollmentResult.error);
            // Don't fail the entire process, just log the warning
          }
        } else {
          console.warn('⚠️ No user_id found for auto-enrollment');
        }
      } else {
        console.warn('⚠️ No user data found for auto-enrollment');
      }

      // Step 3: Get learning path recommendations for display
      setCurrentStep(3); // Move to learning paths
      await new Promise(resolve => setTimeout(resolve, 1000)); // Brief pause for UX

      if (responseData.data?.learning_path_recommendations) {
        setRecommendedPaths(responseData.data.learning_path_recommendations);
      }

      // Step 4: Complete analysis and prepare for VARK quiz
      setCurrentStep(4); // Move to VARK quiz
      await new Promise(resolve => setTimeout(resolve, 1000)); // Brief pause for UX

      // Save department and role to user profile in localStorage
      const currentUserData = localStorage.getItem('user');
      if (currentUserData) {
        const user = JSON.parse(currentUserData);
        user.profile = user.profile || {};
        user.profile.department = userDepartment;
        user.profile.role = userRole;
        localStorage.setItem('user', JSON.stringify(user));
        console.log('✅ Department and role saved to user profile:', { department: userDepartment, role: userRole });
      }

    } catch (error) {
      console.error('Onboarding processing error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred during onboarding');
    } finally {
      setIsLoading(false);
    }
  };

  const autoEnrollInRecommendedPaths = async (userId: string) => {
    try {
      console.log('Auto-enrolling user in recommended learning paths:', userId);
      const response = await fetch('/api/auto-enroll-from-onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId
        })
      });

      if (response.ok) {
        const enrollmentResult = await response.json();
        console.log('Auto-enrollment successful:', enrollmentResult);
        
        if (enrollmentResult.enrolled_paths && enrollmentResult.enrolled_paths.length > 0) {
          console.log(`✅ Enrolled user ${userId} in ${enrollmentResult.enrolled_paths.length} learning paths:`, 
            enrollmentResult.enrolled_paths.map(p => p.learning_path_title).join(', '));
          return { success: true, enrolledPaths: enrollmentResult.enrolled_paths };
        } else {
          console.warn('⚠️ No learning paths were enrolled');
          return { success: false, error: 'No learning paths available for enrollment' };
        }
      } else {
        const errorData = await response.json();
        console.warn('Auto-enrollment failed:', errorData);
        return { success: false, error: errorData.error || 'Enrollment failed' };
      }
    } catch (error) {
      console.warn('Auto-enrollment error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Network error during enrollment' };
    }
  };

  const goToVARKQuiz = () => {
    // Auto-enrollment already happened after skill gap analysis
    navigate('/vark-quiz');
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Users className="w-6 h-6 text-primary" />
                <CardTitle>Welcome to Your Onboarding Journey!</CardTitle>
              </div>
              <CardDescription>
                We'll guide you through a personalized onboarding experience tailored to your role and skills.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h3 className="font-semibold">What We'll Do:</h3>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                      <span className="text-sm">Analyze your resume and skills</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                      <span className="text-sm">Identify skill gaps and strengths</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                      <span className="text-sm">Recommend personalized learning paths</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                      <span className="text-sm">Assess your learning preferences</span>
                    </li>
                  </ul>
                </div>
                <div className="space-y-3">
                  <h3 className="font-semibold">Your Profile:</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Name:</span>
                      <span className="text-sm font-medium">{user?.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Role:</span>
                      <span className="text-sm font-medium">
                        {userRole || user?.role || user?.profile?.role || user?.roleType || 'Not specified'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Department:</span>
                      <span className="text-sm font-medium">
                        {userDepartment || user?.department || user?.profile?.department || 'Not specified'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <Button onClick={() => setCurrentStep(1)} className="w-full" size="lg">
                Get Started
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        );

      case 1:
        return (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Upload className="w-6 h-6 text-primary" />
                <CardTitle>Upload Your Resume</CardTitle>
              </div>
              <CardDescription>
                Upload your resume so we can analyze your current skills and experience.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Role Selection Section */}
              {showRoleSelection && (
                <div className="p-4 border-2 border-orange-200 bg-orange-50 dark:bg-orange-900/20 rounded-lg space-y-4">
                  <div className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-orange-600" />
                    <h3 className="font-semibold text-orange-800 dark:text-orange-200">Complete Your Profile</h3>
                  </div>
                  <p className="text-sm text-orange-700 dark:text-orange-300">
                    We need your department and role information to provide personalized recommendations.
                  </p>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Department</label>
                      <select
                        value={userDepartment}
                        onChange={(e) => setUserDepartment(e.target.value)}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">Select Department</option>
                        <option value="KYC">KYC</option>
                        <option value="Engineering">Engineering</option>
                        <option value="Data Science">Data Science</option>
                        <option value="Operations">Operations</option>
                        <option value="Finance">Finance</option>
                        <option value="HR">HR</option>
                        <option value="Legal">Legal</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Role</label>
                      <select
                        value={userRole}
                        onChange={(e) => setUserRole(e.target.value)}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">Select Role</option>
                        <option value="Data Analyst">Data Analyst</option>
                        <option value="Data Scientist">Data Scientist</option>
                        <option value="Frontend Developer">Frontend Developer</option>
                        <option value="Backend Developer">Backend Developer</option>
                        <option value="Full Stack Developer">Full Stack Developer</option>
                        <option value="DevOps Engineer">DevOps Engineer</option>
                        <option value="QA Engineer">QA Engineer</option>
                        <option value="Business Analyst">Business Analyst</option>
                        <option value="Product Manager">Product Manager</option>
                        <option value="UX Designer">UX Designer</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>
                  
                  {userDepartment && userRole && (
                    <div className="flex items-center gap-2 p-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span className="text-sm text-green-700 dark:text-green-300">
                        ✅ Profile complete: {userRole} in {userDepartment}
                      </span>
                    </div>
                  )}
                </div>
              )}

              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleResumeUpload}
                  className="hidden"
                  id="resume-upload"
                />
                <label htmlFor="resume-upload" className="cursor-pointer">
                  <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <div className="space-y-2">
                    <p className="text-lg font-medium">
                      {resumeFile ? resumeFile.name : 'Choose your resume file'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Supported formats: PDF, DOC, DOCX (max 5MB)
                    </p>
                  </div>
                </label>
              </div>
              
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button 
                onClick={processOnboarding} 
                disabled={!resumeFile || isLoading || !userDepartment || !userRole}
                className="w-full mb-4" 
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing Resume...
                  </>
                ) : (
                  <>
                    Analyze Resume
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
              
              {/* Skip option for testing */}
              <Button 
                variant="outline"
                onClick={() => setCurrentStep(4)} 
                disabled={isLoading}
                className="w-full" 
              >
                Skip Resume Analysis (Go to VARK Quiz)
              </Button>
            </CardContent>
          </Card>
        );

      case 2:
        return (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-primary" />
                <CardTitle>Skill Gap Analysis</CardTitle>
              </div>
              <CardDescription>
                We've analyzed your resume and identified your skill profile.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {skillGaps.length > 0 ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-3">Areas for Development:</h3>
                    <div className="space-y-3">
                      {skillGaps.slice(0, 5).map((gap, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            <Badge 
                              variant={gap.priority === 'high' ? 'destructive' : gap.priority === 'medium' ? 'default' : 'secondary'}
                            >
                              {gap.priority}
                            </Badge>
                            <div>
                              <div className="font-medium">{gap.skill_name}</div>
                              <div className="text-sm text-muted-foreground">
                                Current: Level {gap.current_level} → Target: Level {gap.required_level}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium">Gap: {gap.gap}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {isLoading && (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="w-6 h-6 animate-spin mr-2" />
                      <span>Generating learning recommendations...</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span>Analyzing your skills...</span>
                </div>
              )}
            </CardContent>
          </Card>
        );

      case 3:
        return (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <BookOpen className="w-6 h-6 text-primary" />
                <CardTitle>Learning Path Recommendations</CardTitle>
              </div>
              <CardDescription>
                Based on your skill analysis, here are your personalized learning paths.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {recommendedPaths.length > 0 ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-green-700 dark:text-green-300">
                      ✅ Successfully enrolled in your personalized learning paths
                    </span>
                  </div>
                  
                  {recommendedPaths.map((path, index) => (
                    <div key={path.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant={path.is_mandatory ? "default" : "secondary"}>
                            {path.is_mandatory ? "Mandatory" : "Recommended"}
                          </Badge>
                          <span className="font-medium">{path.title}</span>
                        </div>
                        <Badge variant="outline">Priority {path.priority}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{path.description}</p>
                      <div className="text-sm">
                        <span className="text-muted-foreground">Estimated Duration: </span>
                        <span className="font-medium">{path.estimated_duration}</span>
                      </div>
                    </div>
                  ))}
                  
                  {isLoading && (
                    <div className="flex items-center justify-center py-4">
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      <span>Preparing learning style assessment...</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span>Generating and enrolling in learning paths...</span>
                </div>
              )}
            </CardContent>
          </Card>
        );

      case 4:
        return (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Brain className="w-6 h-6 text-primary" />
                <CardTitle>Learning Style Assessment</CardTitle>
              </div>
              <CardDescription>
                Complete the VARK assessment to discover your optimal learning preferences.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <Brain className="h-4 w-4" />
                <AlertTitle>Final Step</AlertTitle>
                <AlertDescription>
                  Take our comprehensive learning style assessment to personalize your learning experience. 
                  This will help us recommend the most effective learning materials and methods for you.
                </AlertDescription>
              </Alert>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h3 className="font-semibold">What You'll Discover:</h3>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                      <span className="text-sm">Your primary learning style</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                      <span className="text-sm">Personalized learning tips</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1" />
                      <span className="text-sm">Customized content delivery</span>
                    </li>
                  </ul>
                </div>
                <div className="space-y-3">
                  <h3 className="font-semibold">Assessment Details:</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Questions:</span>
                      <span className="text-sm font-medium">12 questions</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Time:</span>
                      <span className="text-sm font-medium">~5 minutes</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Style:</span>
                      <span className="text-sm font-medium">Interactive & Visual</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <Button onClick={goToVARKQuiz} className="w-full" size="lg">
                Start Learning Style Assessment
                <Brain className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/30 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress Header */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold">AI-Powered Onboarding</h1>
                <p className="text-muted-foreground">Personalized learning journey for {user?.name}</p>
              </div>
              <Badge variant="secondary">
                Step {currentStep + 1} of {steps.length}
              </Badge>
            </div>
            
            <Progress value={(currentStep + 1) / steps.length * 100} className="mb-4" />
            
            <div className="grid grid-cols-6 gap-2">
              {steps.map((step, index) => (
                <div key={step.id} className="text-center">
                  <div 
                    className={`w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center text-xs font-medium ${
                      index <= currentStep 
                        ? 'bg-primary text-white' 
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {index < currentStep ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  <div className="text-xs font-medium truncate">{step.title}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Current Step Content */}
        {renderCurrentStep()}
      </div>

      {/* Conversation Agent - Available throughout onboarding */}
      {userDepartment && userRole && (
        <ConversationAgent
          departmentId={userDepartment === 'KYC' ? 'KYC2024001' : 
                      userDepartment === 'Engineering' ? 'ENG2024001' : 
                      userDepartment === 'Data Science' ? 'DS2024001' : 
                      userDepartment}
          departmentName={userDepartment}
          userId={user?.user_id}
        />
      )}
    </div>
  );
};

export default OnboardingWorkflow;
