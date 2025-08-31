"""
AdaptaLearn AI Agent Package
Contains AI-powered components for learning path recommendations and user onboarding
"""

# Make this a proper Python package
__version__ = "1.0.0"

# Import key classes to make them available at package level
try:
    from .dynamic_role_manager import DynamicRoleManager, get_target_skills_for_role, get_role_profile_for_analysis
    from .onboarding_agent import OnboardingAIAgent, bootstrap_user_onboarding, get_user_onboarding_status
    from .resume_analyzer import ResumeAnalyzer, analyze_resume_for_role
    from .department_mapping import DepartmentLearningPathManager, get_onboarding_learning_paths_for_user
    from .role_skills import RoleSkillsManager
    from .persistence import *
    print("✅ Agent package imports successful")
except ImportError as e:
    print(f"⚠️ Warning: Could not import agent modules: {e}")
    # Don't override successful imports with None
    pass