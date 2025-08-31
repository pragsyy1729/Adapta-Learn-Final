#!/usr/bin/env python3
"""
Initialization script for the AI Agent Onboarding System
Sets up default departments, roles, and learning path mappings
"""

import os
import sys

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.department_mapping import DepartmentLearningPathManager, DEFAULT_DEPARTMENT_MAPPINGS
from agent.role_skills import RoleSkillsManager, DEFAULT_ROLE_PROFILES
import json

def initialize_onboarding_system():
    """Initialize the onboarding system with default data"""
    print("🚀 Initializing AI Agent Onboarding System...")
    
    # Initialize managers
    dept_manager = DepartmentLearningPathManager()
    role_manager = RoleSkillsManager()
    
    # 1. Setup default department learning path mappings
    print("📚 Setting up department learning path mappings...")
    try:
        dept_manager.bulk_setup_department_paths(DEFAULT_DEPARTMENT_MAPPINGS)
        print("✅ Department mappings initialized successfully")
    except Exception as e:
        print(f"❌ Error setting up department mappings: {e}")
    
    # 2. Create default role profiles
    print("👥 Creating default role profiles...")
    try:
        for role_key, role_config in DEFAULT_ROLE_PROFILES.items():
            role_id = role_manager.create_role_profile(**role_config)
            print(f"   ✓ Created role profile: {role_config['role_name']} ({role_id})")
        print("✅ Role profiles created successfully")
    except Exception as e:
        print(f"❌ Error creating role profiles: {e}")
    
    # 3. Display setup summary
    print("\n📊 Setup Summary:")
    
    # Show departments and their learning paths
    departments = dept_manager.get_all_departments()
    print(f"   • {len(departments)} departments configured")
    
    for dept in departments:
        paths = dept_manager.get_department_learning_paths(dept['id'])
        mandatory_count = len([p for p in paths if p.get('is_mandatory', True)])
        print(f"     - {dept['name']}: {len(paths)} learning paths ({mandatory_count} mandatory)")
    
    # Show role profiles
    roles_data = role_manager._load_roles()
    print(f"   • {len(roles_data['roles'])} role profiles created")
    
    for role_data in roles_data['roles'].values():
        skills_count = len(role_data.get('skills', []))
        print(f"     - {role_data['role_name']} ({role_data['department']}): {skills_count} required skills")
    
    print("\n🎉 Onboarding system initialization complete!")
    print("\nNext steps:")
    print("1. Start the backend server to access the API endpoints")
    print("2. Use the Admin UI to configure additional departments and roles")
    print("3. Upload resumes and test the onboarding analysis")

def create_sample_learning_paths():
    """Create some sample learning paths for testing"""
    print("\n📖 Creating sample learning paths...")
    
    sample_paths = {
        "python_fundamentals": {
            "id": "python_fundamentals",
            "title": "Python Fundamentals",
            "description": "Learn the basics of Python programming",
            "department": "engineering",
            "difficulty": "Beginner",
            "duration": "4 weeks",
            "modules": ["python_basics", "python_data_types", "python_control_flow"]
        },
        "ml_basics": {
            "id": "ml_basics", 
            "title": "Machine Learning Basics",
            "description": "Introduction to machine learning concepts and algorithms",
            "department": "data_science",
            "difficulty": "Intermediate",
            "duration": "6 weeks",
            "modules": ["ml_intro", "supervised_learning", "unsupervised_learning"]
        },
        "soft_skills_fundamentals": {
            "id": "soft_skills_fundamentals",
            "title": "Professional Soft Skills",
            "description": "Essential communication and collaboration skills",
            "department": "all",
            "difficulty": "Beginner", 
            "duration": "3 weeks",
            "modules": ["communication_basics", "teamwork", "time_management"]
        },
        "leadership_development": {
            "id": "leadership_development",
            "title": "Leadership Development",
            "description": "Develop leadership and people management skills",
            "department": "all",
            "difficulty": "Advanced",
            "duration": "8 weeks", 
            "modules": ["leadership_principles", "team_management", "strategic_thinking"]
        }
    }
    
    # Save to learning paths file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    learning_paths_file = os.path.join(data_dir, 'learning_paths.json')
    
    try:
        # Load existing learning paths if any
        if os.path.exists(learning_paths_file):
            with open(learning_paths_file, 'r') as f:
                existing_paths = json.load(f)
        else:
            existing_paths = {}
        
        # Add sample paths
        existing_paths.update(sample_paths)
        
        # Save updated paths
        with open(learning_paths_file, 'w') as f:
            json.dump(existing_paths, f, indent=2)
        
        print(f"✅ Created {len(sample_paths)} sample learning paths")
        for path_id, path_info in sample_paths.items():
            print(f"   ✓ {path_info['title']} ({path_id})")
            
    except Exception as e:
        print(f"❌ Error creating sample learning paths: {e}")

def test_onboarding_flow():
    """Test the complete onboarding flow"""
    print("\n🧪 Testing onboarding flow...")
    
    try:
        from agent.onboarding_agent import OnboardingAIAgent
        
        agent = OnboardingAIAgent()
        
        # Test getting onboarding plan for engineering department
        dept_manager = DepartmentLearningPathManager()
        plan = dept_manager.get_onboarding_plan_for_user("engineering")
        
        if "error" not in plan:
            print("✅ Successfully generated onboarding plan for engineering department")
            print(f"   • {len(plan.get('mandatory_learning_paths', []))} mandatory learning paths")
            print(f"   • {len(plan.get('onboarding_phases', []))} onboarding phases")
            print(f"   • Estimated duration: {plan.get('estimated_total_weeks', 'N/A')} weeks")
        else:
            print(f"❌ Error generating onboarding plan: {plan['error']}")
            
        # Test role skill gap analysis
        role_manager = RoleSkillsManager()
        frontend_role = role_manager.get_role_by_name("Frontend Developer", "engineering")
        
        if frontend_role:
            sample_user_skills = {
                "JavaScript": {"level": 3.0, "confidence": 0.8},
                "React": {"level": 2.5, "confidence": 0.7},
                "HTML": {"level": 3.5, "confidence": 0.9},
                "CSS": {"level": 3.0, "confidence": 0.8}
            }
            
            gap_analysis = role_manager.analyze_skill_gap(frontend_role["role_id"], sample_user_skills)
            
            if "error" not in gap_analysis:
                print("✅ Successfully performed skill gap analysis")
                print(f"   • Readiness score: {gap_analysis.get('overall_readiness', {}).get('score', 'N/A')}%")
                print(f"   • High priority gaps: {gap_analysis.get('high_priority_gaps', 0)}")
            else:
                print(f"❌ Error in skill gap analysis: {gap_analysis['error']}")
        
        print("✅ Onboarding flow test completed")
        
    except ImportError:
        print("⚠️  Enhanced onboarding modules not available - basic system ready")
    except Exception as e:
        print(f"❌ Error testing onboarding flow: {e}")

if __name__ == "__main__":
    print("AI Agent Onboarding System - Initialization Script")
    print("=" * 55)
    
    # Run initialization
    initialize_onboarding_system()
    
    # Create sample learning paths
    create_sample_learning_paths()
    
    # Test the system
    test_onboarding_flow()
    
    print("\n" + "=" * 55)
    print("Initialization complete! You can now:")
    print("• Access the admin UI at /admin to manage onboarding settings")  
    print("• Use the API endpoints to analyze user resumes and skills")
    print("• View onboarding recommendations and progress tracking")
    print("\nAPI Endpoints:")
    print("• POST /api/onboarding/analyze - Analyze user for onboarding")
    print("• GET /api/onboarding/departments - Manage department mappings")
    print("• GET /api/onboarding/roles - Manage role skill requirements")
    print("• GET /api/onboarding/status/<user_id> - Check onboarding status")
