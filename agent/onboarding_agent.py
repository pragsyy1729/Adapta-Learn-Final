"""
AI Agent for User Onboarding
Orchestrates the complete onboarding process including resume analysis, 
role matching, and learning path recommendations
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Import our custom modules
try:
    # Try relative imports first (when imported as part of package)
    from .resume_analyzer import ResumeAnalyzer, analyze_resume_for_role
    from .department_mapping import DepartmentLearningPathManager, get_onboarding_learning_paths_for_user
    from .role_skills import RoleSkillsManager
    from .dynamic_role_manager import DynamicRoleManager
    from . import persistence
except ImportError:
    # Fall back to absolute imports (when imported standalone)
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from resume_analyzer import ResumeAnalyzer, analyze_resume_for_role
    from department_mapping import DepartmentLearningPathManager, get_onboarding_learning_paths_for_user
    from role_skills import RoleSkillsManager
    from dynamic_role_manager import DynamicRoleManager
    import persistence

@dataclass
class OnboardingRecommendation:
    user_id: str
    department: str
    role: str
    recommended_learning_paths: List[str]
    skill_gaps: List[Dict]
    estimated_completion_weeks: int
    priority_skills: List[str]
    resume_analysis_summary: Dict
    created_at: str
    
class OnboardingAIAgent:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        self.data_dir = data_dir
        self.onboarding_file = os.path.join(data_dir, 'onboarding_recommendations.json')
        
        # Initialize component managers
        self.resume_analyzer = ResumeAnalyzer()
        self.dept_manager = DepartmentLearningPathManager(data_dir)
        self.role_manager = RoleSkillsManager(data_dir)
        self.dynamic_role_manager = DynamicRoleManager(data_dir)
        
        # Ensure files exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize onboarding data files"""
        if not os.path.exists(self.onboarding_file):
            default_data = {
                "recommendations": {},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.onboarding_file, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def _load_recommendations(self) -> Dict:
        """Load onboarding recommendations"""
        try:
            with open(self.onboarding_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading recommendations: {e}")
            return {"recommendations": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_recommendations(self, data: Dict):
        """Save onboarding recommendations"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.onboarding_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def analyze_user_for_onboarding(self, user_id: str, resume_file_path: str, 
                                   target_role: str, department: str) -> Dict:
        """
        Complete onboarding analysis for a new user
        
        Args:
            user_id: Unique user identifier
            resume_file_path: Path to user's resume PDF/DOCX
            target_role: Role the user will be filling
            department: Department the user is joining
            
        Returns:
            Complete onboarding analysis with recommendations
        """
        try:
            print(f"🤖 Starting onboarding analysis for user {user_id}")
            
            # Step 1: Get role profile and required skills
            # First try to get from dynamic role manager
            dynamic_role = self.dynamic_role_manager.get_role_by_name(target_role, department)
            if dynamic_role:
                role_profile = {
                    "role_id": dynamic_role.role_id,
                    "role_name": dynamic_role.role_name,
                    "department": dynamic_role.department,
                    "level": dynamic_role.level,
                    "skills": [{"skill_name": s.skill_name, "required_level": s.required_level,
                               "importance": s.importance, "category": s.category}
                              for s in dynamic_role.skills],
                    "description": dynamic_role.description,
                    "responsibilities": dynamic_role.responsibilities
                }
                print(f"📋 Found dynamic role profile with {len(role_profile['skills'])} required skills")
            else:
                # Fall back to static role manager
                role_profile = self.role_manager.get_role_by_name(target_role, department)
                if not role_profile:
                    return {"error": f"Role '{target_role}' not found in department '{department}'"}
                print(f"📋 Found static role profile with {len(role_profile['skills'])} required skills")
            
            required_skills = [skill["skill_name"] for skill in role_profile["skills"]]
            print(f"📋 Required skills for role: {required_skills}")
            
            # Step 2: Analyze resume for skills and proficiency
            resume_analysis = analyze_resume_for_role(resume_file_path, required_skills, target_role, department)
            print(f"📄 Resume analysis complete. Found {resume_analysis['summary']['total_skills_found']} skills")
            
            # Step 3: Perform skill gap analysis
            user_skills = resume_analysis["skills"]
            
            # Use dynamic role manager for gap analysis if available
            if dynamic_role:
                gap_analysis = self._analyze_skill_gap_dynamic(dynamic_role, user_skills)
            else:
                gap_analysis = self.role_manager.analyze_skill_gap(role_profile["role_id"], user_skills)
            
            print(f"📊 Skill gap analysis complete. {gap_analysis['total_gaps']} gaps identified")
            
            # Step 4: Get department-based learning paths
            dept_learning_paths = get_onboarding_learning_paths_for_user(department)
            dept_onboarding_plan = self.dept_manager.get_onboarding_plan_for_user(department, target_role)
            print(f"🎯 Found {len(dept_learning_paths)} department learning paths")
            
            # Step 5: Get skill-specific learning path recommendations
            skill_based_paths = self._recommend_skill_based_learning_paths(gap_analysis["skill_gaps"])
            print(f"📚 Recommended {len(skill_based_paths)} skill-based learning paths")
            
            # Step 6: Combine and prioritize all recommendations
            combined_recommendations = self._combine_learning_path_recommendations(
                dept_learning_paths, skill_based_paths, gap_analysis
            )
            
            # Step 7: Calculate estimated timeline
            estimated_weeks = self._calculate_onboarding_timeline(
                combined_recommendations, gap_analysis, dept_onboarding_plan
            )
            
            # Step 8: Generate priority skills list
            priority_skills = self._get_priority_skills(gap_analysis)
            
            # Step 9: Create onboarding recommendation
            recommendation = OnboardingRecommendation(
                user_id=user_id,
                department=department,
                role=target_role,
                recommended_learning_paths=combined_recommendations,
                skill_gaps=gap_analysis["skill_gaps"][:10],  # Top 10 gaps
                estimated_completion_weeks=estimated_weeks,
                priority_skills=priority_skills,
                resume_analysis_summary=resume_analysis["summary"],
                created_at=datetime.now().isoformat()
            )
            
            # Step 10: Save recommendation
            self._save_onboarding_recommendation(recommendation)
            
            # Step 11: Auto-assign recommended learning paths to user
            try:
                self._auto_assign_recommended_paths(user_id, combined_recommendations)
                print(f"✅ Auto-assigned {len(combined_recommendations)} learning paths to user {user_id}")
            except Exception as e:
                print(f"⚠️ Failed to auto-assign learning paths to user {user_id}: {e}")
            
            # Step 12: Generate detailed report
            detailed_report = self._generate_onboarding_report(recommendation, gap_analysis, 
                                                             role_profile, dept_onboarding_plan)
            
            print(f"✅ Onboarding analysis complete for {user_id}")
            return detailed_report
            
        except Exception as e:
            print(f"❌ Error in onboarding analysis: {e}")
            return {"error": f"Failed to analyze user for onboarding: {str(e)}"}
    
    def _recommend_skill_based_learning_paths(self, skill_gaps: List[Dict]) -> List[str]:
        """
        Recommend learning paths based on skill gaps
        
        This would ideally query a learning path database to find paths
        that address specific skill gaps. For now, we'll use a simple mapping.
        """
        # Load existing learning paths
        learning_paths_file = os.path.join(self.data_dir, 'learning_paths.json')
        if not os.path.exists(learning_paths_file):
            return []
        
        with open(learning_paths_file, 'r') as f:
            learning_paths_data = json.load(f)
        
        # Simple skill to learning path mapping
        skill_to_path_mapping = {
            "Python": ["python_fundamentals", "python_advanced"],
            "JavaScript": ["javascript_basics", "js_advanced"],
            "React": ["0b8de18342454b2ca062f0a4b4c86956"],  # React Development Track
            "Machine Learning": ["ml_basics", "ml_advanced"],
            "SQL": ["database_fundamentals"],
            "Communication": ["soft_skills_fundamentals"],
            "Leadership": ["leadership_development"],
            "Project Management": ["pm_fundamentals"]
        }
        
        recommended_paths = []
        high_priority_gaps = [gap for gap in skill_gaps if gap.get("priority") == "high"][:5]
        
        for gap in high_priority_gaps:
            skill = gap["skill"]
            if skill in skill_to_path_mapping:
                paths = skill_to_path_mapping[skill]
                for path in paths:
                    if path not in recommended_paths:
                        # Check if path exists in our learning paths
                        if path in learning_paths_data:
                            recommended_paths.append(path)
        
        return recommended_paths[:5]  # Return top 5 recommendations
    
    def _combine_learning_path_recommendations(self, dept_paths: List[str], 
                                             skill_paths: List[str], gap_analysis: Dict) -> List[str]:
        """Combine department and skill-based learning path recommendations"""
        combined = []
        
        # Add department paths first (mandatory)
        combined.extend(dept_paths)
        
        # Add skill-based paths that aren't already included
        for path in skill_paths:
            if path not in combined:
                combined.append(path)
        
        # Limit total recommendations to avoid overwhelming user
        return combined[:8]
    
    def _calculate_onboarding_timeline(self, learning_paths: List[str], 
                                     gap_analysis: Dict, dept_plan: Dict) -> int:
        """Calculate estimated onboarding timeline in weeks"""
        base_weeks = dept_plan.get("estimated_total_weeks", 8)
        
        # Add time based on skill gaps
        high_priority_gaps = len([g for g in gap_analysis.get("skill_gaps", []) if g.get("priority") == "high"])
        medium_priority_gaps = len([g for g in gap_analysis.get("skill_gaps", []) if g.get("priority") == "medium"])
        
        # Rough estimate: 2 weeks per high priority gap, 1 week per medium
        additional_weeks = (high_priority_gaps * 2) + (medium_priority_gaps * 1)
        
        total_weeks = base_weeks + additional_weeks
        
        # Cap at reasonable maximum
        return min(total_weeks, 20)
    
    def _get_priority_skills(self, gap_analysis: Dict) -> List[str]:
        """Get list of priority skills to focus on"""
        skill_gaps = gap_analysis.get("skill_gaps", [])
        
        # Get high priority skills
        high_priority = [gap["skill"] for gap in skill_gaps if gap.get("priority") == "high"]
        
        # If less than 5 high priority, add some medium priority
        if len(high_priority) < 5:
            medium_priority = [gap["skill"] for gap in skill_gaps if gap.get("priority") == "medium"]
            high_priority.extend(medium_priority[:5-len(high_priority)])
        
        return high_priority[:5]
    
    def _save_onboarding_recommendation(self, recommendation: OnboardingRecommendation):
        """Save onboarding recommendation to file"""
        data = self._load_recommendations()
        data["recommendations"][recommendation.user_id] = asdict(recommendation)
        self._save_recommendations(data)
    
    def _auto_assign_recommended_paths(self, user_id: str, recommended_paths: List[str]) -> None:
        """Auto-assign recommended learning paths to user's enrollments"""
        try:
            # Import necessary functions directly to avoid relative import issues
            import sys
            import os
            import json
            import uuid
            from datetime import datetime
            
            # Add the backend services path to sys.path
            backend_services_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'services')
            sys.path.append(backend_services_path)
            
            # Import data access functions directly
            from data_access import _read_json, _write_json, get_data_file_path
            
            # Define helper function for ISO timestamp
            def now_iso() -> str:
                return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
            
            # Load onboarding recommendations
            onboarding_file = os.path.join(self.data_dir, 'onboarding_recommendations.json')
            onboarding_data = _read_json(onboarding_file, {})
            
            # Get user's recommendations
            user_recommendations = onboarding_data.get('recommendations', {}).get(user_id)
            if not user_recommendations:
                print(f"No onboarding recommendations found for user {user_id}")
                return
            
            paths_to_assign = user_recommendations.get('recommended_learning_paths', [])
            if not paths_to_assign:
                print(f"No recommended learning paths found for user {user_id}")
                return
            
            # Load users to update enrollments
            users_file = os.path.join(self.data_dir, 'users.json')
            users = _read_json(users_file, {})
            
            # Find user and add resume-based enrollments
            user_found = False
            for email, user_data in users.items():
                if user_data.get('user_id') == user_id:
                    if 'profile' not in user_data:
                        user_data['profile'] = {}
                    
                    if 'enrollments' not in user_data['profile']:
                        user_data['profile']['enrollments'] = []
                    
                    # Add resume-based learning paths to enrollments
                    for path_id in paths_to_assign:
                        # Check if already enrolled
                        existing_enrollment = next(
                            (e for e in user_data['profile']['enrollments'] 
                             if e.get('learning_path_id') == path_id),
                            None
                        )
                        
                        if not existing_enrollment:
                            enrollment = {
                                'learning_path_id': path_id,
                                'enrolled_at': now_iso(),
                                'status': 'enrolled',
                                'source': 'resume_analysis'
                            }
                            user_data['profile']['enrollments'].append(enrollment)
                    
                    user_found = True
                    break
            
            if not user_found:
                print(f"User {user_id} not found for resume-based enrollment assignment")
                return
            
            # Save updated users
            _write_json(users_file, users)

            # Load learning path progress data
            progress_file = os.path.join(self.data_dir, 'LearningPathProgress.json')
            progress_data = _read_json(progress_file, [])

            # Create progress entries for resume-based learning paths
            assigned_resume_paths = []
            for path_id in paths_to_assign:
                # Check if user already has this learning path progress entry
                existing_progress = next(
                    (p for p in progress_data if p.get('attributes', {}).get('user_id') == user_id and
                     p.get('attributes', {}).get('learning_path_id') == path_id),
                    None
                )

                if not existing_progress:
                    # Create new progress entry for this learning path
                    new_progress = {
                        "attributes": {
                            "id": f"lpp_{user_id}_{path_id}_{str(uuid.uuid4())[:8]}",
                            "user_id": user_id,
                            "learning_path_id": path_id,
                            "status": "not_started",
                            "progress_percent": 0.0,
                            "modules_completed_count": 0,
                            "modules_total_count": 0,  # Will be updated when learning path data is available
                            "time_invested_minutes": 0,
                            "last_accessed_at": None,
                            "started_at": None,
                            "completed_at": None,
                            "current_module_id": None,
                            "enrolled_at": now_iso(),
                            "is_resume_based": True
                        }
                    }
                    progress_data.append(new_progress)
                    assigned_resume_paths.append(path_id)

            # Save updated progress data
            if assigned_resume_paths:
                _write_json(progress_file, progress_data)
                print(f"✅ Successfully auto-assigned {len(assigned_resume_paths)} resume-based learning paths to user {user_id}: {assigned_resume_paths}")
            else:
                print(f"ℹ️ All recommended learning paths were already assigned to user {user_id}")

        except ImportError as e:
            print(f"❌ Import error in auto-assigning recommended paths for user {user_id}: {e}")
            print("This may be due to incorrect path resolution. Please check the import path.")
        except Exception as e:
            print(f"❌ Error in auto-assigning recommended paths for user {user_id}: {e}")
            print(f"Recommended paths were: {recommended_paths}")
            # Don't raise exception to avoid breaking the onboarding flow
    
    def _generate_onboarding_report(self, recommendation: OnboardingRecommendation, 
                                  gap_analysis: Dict, role_profile: Dict, 
                                  dept_plan: Dict) -> Dict:
        """Generate comprehensive onboarding report"""
        return {
            "user_id": recommendation.user_id,
            "analysis_date": recommendation.created_at,
            "role_information": {
                "role": recommendation.role,
                "department": recommendation.department,
                "role_description": role_profile.get("description", ""),
                "required_skills_count": len(role_profile.get("skills", []))
            },
            "skill_assessment": {
                "total_skills_analyzed": len(gap_analysis.get("skill_gaps", [])) + len(gap_analysis.get("strengths", [])),
                "skills_with_gaps": len(gap_analysis.get("skill_gaps", [])),
                "strengths": gap_analysis.get("strengths", []),
                "high_priority_gaps": len([g for g in gap_analysis.get("skill_gaps", []) if g.get("priority") == "high"]),
                "readiness_score": gap_analysis.get("overall_readiness", {}),
                "priority_skills": recommendation.priority_skills
            },
            "learning_plan": {
                "recommended_learning_paths": recommendation.recommended_learning_paths,
                "estimated_completion_weeks": recommendation.estimated_completion_weeks,
                "department_mandatory_paths": dept_plan.get("mandatory_learning_paths", []),
                "onboarding_phases": dept_plan.get("onboarding_phases", [])
            },
            "resume_insights": {
                "summary": recommendation.resume_analysis_summary,
                "skills_found_in_resume": recommendation.resume_analysis_summary.get("total_skills_found", 0)
            },
            "recommendations": gap_analysis.get("recommendations", []),
            "next_steps": self._generate_next_steps(recommendation, gap_analysis)
        }
    
    def _generate_next_steps(self, recommendation: OnboardingRecommendation, 
                           gap_analysis: Dict) -> List[Dict]:
        """Generate actionable next steps for the user"""
        next_steps = []
        
        # Step 1: Start with department onboarding
        if recommendation.recommended_learning_paths:
            next_steps.append({
                "step": 1,
                "title": "Begin Department Onboarding",
                "description": f"Start with mandatory learning paths for {recommendation.department} department",
                "action": f"Enroll in learning path: {recommendation.recommended_learning_paths[0]}",
                "estimated_time": "Week 1-2",
                "priority": "high"
            })
        
        # Step 2: Address critical skill gaps
        high_priority_gaps = [g for g in gap_analysis.get("skill_gaps", []) if g.get("priority") == "high"]
        if high_priority_gaps:
            critical_skill = high_priority_gaps[0]["skill"]
            next_steps.append({
                "step": 2,
                "title": "Address Critical Skill Gap",
                "description": f"Focus on improving {critical_skill} - highest priority gap identified",
                "action": f"Complete focused training in {critical_skill}",
                "estimated_time": "Week 2-4",
                "priority": "high"
            })
        
        # Step 3: Complete assessments
        next_steps.append({
            "step": 3,
            "title": "Complete Skill Assessments", 
            "description": "Take assessments to validate skill improvements",
            "action": "Schedule and complete role-specific assessments",
            "estimated_time": "Week 4-6",
            "priority": "medium"
        })
        
        # Step 4: Project application
        next_steps.append({
            "step": 4,
            "title": "Apply Skills in Project",
            "description": "Work on a real project to demonstrate competency",
            "action": "Join a mentored project team or work on practice project",
            "estimated_time": "Week 6-8",
            "priority": "medium"
        })
        
        return next_steps
    
    def _analyze_skill_gap_dynamic(self, dynamic_role, user_skills: Dict[str, Dict]) -> Dict:
        """
        Analyze skill gap using dynamic role manager
        
        Args:
            dynamic_role: DynamicRole object from DynamicRoleManager
            user_skills: User's current skills in format {skill_name: {"level": float, "confidence": float}}
        
        Returns:
            Gap analysis with recommendations
        """
        required_skills = dynamic_role.skills
        gaps = []
        strengths = []
        recommendations = []
        
        for skill_req in required_skills:
            skill_name = skill_req.skill_name
            required_level = skill_req.required_level
            importance = skill_req.importance
            
            current_skill = user_skills.get(skill_name, {"level": 1.0, "confidence": 0.1})
            current_level = current_skill["level"]
            confidence = current_skill.get("confidence", 0.5)
            
            gap = required_level - current_level
            
            if gap > 0.5:  # Significant gap
                priority = "high" if importance >= 4 else "medium" if importance >= 3 else "low"
                gaps.append({
                    "skill": skill_name,
                    "current_level": current_level,
                    "required_level": required_level,
                    "gap": gap,
                    "importance": importance,
                    "priority": priority,
                    "confidence": confidence,
                    "category": skill_req.category
                })
            elif gap < -0.5:  # User exceeds requirement
                strengths.append({
                    "skill": skill_name,
                    "current_level": current_level,
                    "required_level": required_level,
                    "excess": abs(gap),
                    "confidence": confidence
                })
        
        # Sort gaps by priority and gap size
        gaps.sort(key=lambda x: (-x["importance"], -x["gap"]))
        
        # Generate recommendations
        high_priority_gaps = [g for g in gaps if g["priority"] == "high"][:3]
        for gap in high_priority_gaps:
            recommendations.append({
                "skill": gap["skill"],
                "current_level": gap["current_level"],
                "target_level": gap["required_level"],
                "recommendation": f"Focus on improving {gap['skill']} from level {gap['current_level']:.1f} to {gap['required_level']:.1f}",
                "priority": gap["priority"]
            })
        
        return {
            "role_name": dynamic_role.role_name,
            "department": dynamic_role.department,
            "total_gaps": len(gaps),
            "high_priority_gaps": len([g for g in gaps if g["priority"] == "high"]),
            "strengths": strengths,
            "skill_gaps": gaps,
            "recommendations": recommendations,
            "overall_readiness": self._calculate_readiness_score_dynamic(gaps, required_skills)
        }
    
    def _calculate_readiness_score_dynamic(self, gaps: List[Dict], required_skills) -> Dict:
        """Calculate overall readiness score for the role using dynamic skills"""
        if not required_skills:
            return {"score": 0, "level": "not_ready"}
        
        total_importance = sum(skill.importance for skill in required_skills)
        gap_penalty = 0
        
        for gap in gaps:
            # Penalty based on gap size and importance
            penalty = (gap["gap"] / 5.0) * (gap["importance"] / 5.0)
            gap_penalty += penalty
        
        # Normalize score (0-100)
        max_possible_penalty = len(required_skills) * 1.0  # Max gap is 4.0 (5-1), max importance is 5
        score = max(0, 100 - (gap_penalty / max_possible_penalty * 100))
        
        if score >= 90:
            level = "excellent"
        elif score >= 75:
            level = "good"
        elif score >= 60:
            level = "fair"
        elif score >= 40:
            level = "needs_improvement"
        else:
            level = "not_ready"
        
        return {
            "score": round(score, 1),
            "level": level,
            "description": self._get_readiness_description(level)
        }
    
    def get_onboarding_recommendation(self, user_id: str) -> Optional[Dict]:
        """Get stored onboarding recommendation for a user"""
        data = self._load_recommendations()
        return data["recommendations"].get(user_id)
    
    def update_onboarding_progress(self, user_id: str, completed_paths: List[str], 
                                 skill_updates: Dict[str, Dict]) -> Dict:
        """
        Update user's onboarding progress
        
        Args:
            user_id: User identifier
            completed_paths: List of completed learning path IDs
            skill_updates: Updated skill levels {skill_name: {"level": float, "confidence": float}}
        """
        recommendation = self.get_onboarding_recommendation(user_id)
        if not recommendation:
            return {"error": "No onboarding recommendation found for user"}
        
        # Calculate progress
        total_paths = len(recommendation["recommended_learning_paths"])
        completed_count = len(completed_paths)
        progress_percentage = (completed_count / total_paths * 100) if total_paths > 0 else 0
        
        # Re-analyze skill gaps with updated skills
        # Try dynamic role manager first
        dynamic_role = self.dynamic_role_manager.get_role_by_name(recommendation["role"], recommendation["department"])
        if dynamic_role:
            updated_gap_analysis = self._analyze_skill_gap_dynamic(dynamic_role, skill_updates)
        else:
            role_profile = self.role_manager.get_role_by_name(recommendation["role"], recommendation["department"])
            if role_profile:
                updated_gap_analysis = self.role_manager.analyze_skill_gap(role_profile["role_id"], skill_updates)
            else:
                updated_gap_analysis = {"error": "Could not find role for gap analysis"}
            
            # Update recommendation
            data = self._load_recommendations()
            data["recommendations"][user_id]["skill_gaps"] = updated_gap_analysis["skill_gaps"]
            data["recommendations"][user_id]["last_updated"] = datetime.now().isoformat()
            self._save_recommendations(data)
        
        return {
            "user_id": user_id,
            "progress_percentage": round(progress_percentage, 1),
            "completed_paths": completed_paths,
            "remaining_paths": [p for p in recommendation["recommended_learning_paths"] if p not in completed_paths],
            "updated_readiness": updated_gap_analysis.get("overall_readiness", {}) if 'updated_gap_analysis' in locals() else {},
            "updated_at": datetime.now().isoformat()
        }

# Integration function for existing system
def bootstrap_user_onboarding(user_id: str, resume_file_path: str, role_id: str) -> Dict:
    """
    Integration function for existing bootstrap system
    
    Args:
        user_id: User identifier
        resume_file_path: Path to resume file
        role_id: Role ID from existing system
    
    Returns:
        Onboarding analysis results
    """
    agent = OnboardingAIAgent()
    
    # Try to map role_id to role name and department
    # This would need to be customized based on your existing role system
    role_mapping = {
        "jr_data_eng": ("Data Engineer", "engineering"),
        "python_dev": ("Python Developer", "engineering"),
        "data_scientist": ("Data Scientist", "data_science")
    }
    
    if role_id in role_mapping:
        role_name, department = role_mapping[role_id]
        return agent.analyze_user_for_onboarding(user_id, resume_file_path, role_name, department)
    else:
        return {"error": f"Unknown role_id: {role_id}"}

def get_user_onboarding_status(user_id: str) -> Dict:
    """Get current onboarding status for a user"""
    agent = OnboardingAIAgent()
    recommendation = agent.get_onboarding_recommendation(user_id)
    
    if not recommendation:
        return {"error": "No onboarding plan found for user"}
    
    # Calculate time since onboarding started
    created_at = datetime.fromisoformat(recommendation["created_at"])
    days_since_start = (datetime.now() - created_at).days
    weeks_since_start = days_since_start // 7
    
    return {
        "user_id": user_id,
        "onboarding_start_date": recommendation["created_at"],
        "weeks_since_start": weeks_since_start,
        "estimated_total_weeks": recommendation["estimated_completion_weeks"],
        "progress_percentage": min(100, (weeks_since_start / recommendation["estimated_completion_weeks"]) * 100),
        "recommended_paths": recommendation["recommended_learning_paths"],
        "priority_skills": recommendation["priority_skills"],
        "current_phase": "active" if weeks_since_start < recommendation["estimated_completion_weeks"] else "completed"
    }

if __name__ == "__main__":
    # Test the onboarding agent
    agent = OnboardingAIAgent()
    
    print("🚀 Testing Onboarding AI Agent")
    
    # This would normally use a real resume file
    # For testing, we'll simulate the process
    test_resume_path = "/path/to/test/resume.pdf"  # This would be a real file path
    
    try:
        # Test the analysis (this will fail without a real resume file, but shows the flow)
        result = agent.analyze_user_for_onboarding(
            user_id="test_user_001",
            resume_file_path=test_resume_path,
            target_role="Frontend Developer",
            department="engineering"
        )
        
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Test completed with expected error: {e}")
        print("This is normal when testing without real resume files")
