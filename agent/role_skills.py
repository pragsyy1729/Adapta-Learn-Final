"""
Role Skills Mapping System
Enhanced system for defining role requirements with detailed skill proficiency levels
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class SkillRequirement:
    skill_name: str
    required_level: float  # 1.0 to 5.0
    importance: int  # 1 to 5, where 5 is critical
    category: str  # e.g., "technical", "soft", "domain"
    description: str = ""
    assessment_required: bool = False
    learning_resources: List[str] = None
    
    def __post_init__(self):
        if self.learning_resources is None:
            self.learning_resources = []

@dataclass 
class RoleProfile:
    role_id: str
    role_name: str
    department: str
    level: str  # e.g., "junior", "mid", "senior", "lead"
    skills: List[SkillRequirement]
    description: str = ""
    responsibilities: List[str] = None
    min_experience_years: int = 0
    preferred_experience_years: int = 0
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.responsibilities is None:
            self.responsibilities = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

class RoleSkillsManager:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.data_dir = data_dir
        self.roles_file = os.path.join(data_dir, 'role_profiles.json')
        self.skill_catalog_file = os.path.join(data_dir, 'skill_catalog.json')
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize data files with default structure"""
        if not os.path.exists(self.roles_file):
            default_roles = {
                "roles": {},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.roles_file, 'w') as f:
                json.dump(default_roles, f, indent=2)
        
        if not os.path.exists(self.skill_catalog_file):
            # Create a comprehensive skill catalog
            default_catalog = self._create_default_skill_catalog()
            with open(self.skill_catalog_file, 'w') as f:
                json.dump(default_catalog, f, indent=2)
    
    def _create_default_skill_catalog(self) -> Dict:
        """Create default skill catalog with common skills"""
        return {
            "skills": {
                # Programming Languages
                "Python": {
                    "category": "technical",
                    "description": "Python programming language proficiency",
                    "levels": {
                        1: "Basic syntax and concepts",
                        2: "Can write simple scripts and functions", 
                        3: "Proficient with frameworks and libraries",
                        4: "Advanced features, optimization, architecture",
                        5: "Expert level, can mentor others"
                    }
                },
                "JavaScript": {
                    "category": "technical",
                    "description": "JavaScript programming proficiency",
                    "levels": {
                        1: "Basic syntax and DOM manipulation",
                        2: "ES6+ features, async programming",
                        3: "Frameworks (React/Vue/Angular), Node.js",
                        4: "Advanced patterns, performance optimization",
                        5: "Expert level, framework architecture"
                    }
                },
                "SQL": {
                    "category": "technical", 
                    "description": "Database querying and design skills",
                    "levels": {
                        1: "Basic SELECT queries",
                        2: "JOINs, GROUP BY, basic optimization",
                        3: "Complex queries, stored procedures",
                        4: "Database design, advanced optimization",
                        5: "Expert level, database architecture"
                    }
                },
                
                # Frameworks & Tools
                "React": {
                    "category": "technical",
                    "description": "React.js framework proficiency",
                    "levels": {
                        1: "Basic components and JSX",
                        2: "State management, hooks",
                        3: "Advanced patterns, context, routing",
                        4: "Performance optimization, testing",
                        5: "Architecture decisions, custom hooks"
                    }
                },
                "Docker": {
                    "category": "technical",
                    "description": "Containerization with Docker",
                    "levels": {
                        1: "Basic container concepts",
                        2: "Create and run containers",
                        3: "Docker Compose, networking",
                        4: "Multi-stage builds, optimization",
                        5: "Container orchestration, security"
                    }
                },
                "Git": {
                    "category": "technical",
                    "description": "Version control with Git",
                    "levels": {
                        1: "Basic add, commit, push",
                        2: "Branching, merging, pull requests",
                        3: "Advanced workflows, rebase",
                        4: "Git internals, complex merge conflicts", 
                        5: "Git administration, custom workflows"
                    }
                },
                
                # Data & Analytics
                "Machine Learning": {
                    "category": "technical",
                    "description": "Machine learning concepts and implementation",
                    "levels": {
                        1: "Basic ML concepts",
                        2: "Supervised learning algorithms",
                        3: "Feature engineering, model evaluation",
                        4: "Deep learning, advanced techniques",
                        5: "ML system design, research"
                    }
                },
                "Data Analysis": {
                    "category": "technical",
                    "description": "Data analysis and visualization skills",
                    "levels": {
                        1: "Basic statistics, Excel",
                        2: "Python/R for analysis, basic visualization",
                        3: "Advanced analysis, dashboard creation",
                        4: "Statistical modeling, A/B testing",
                        5: "Advanced analytics, predictive modeling"
                    }
                },
                
                # Soft Skills
                "Communication": {
                    "category": "soft",
                    "description": "Verbal and written communication skills",
                    "levels": {
                        1: "Can communicate basic ideas",
                        2: "Clear written and verbal communication",
                        3: "Effective presentations, documentation",
                        4: "Stakeholder communication, negotiation",
                        5: "Executive communication, thought leadership"
                    }
                },
                "Leadership": {
                    "category": "soft", 
                    "description": "Leadership and people management skills",
                    "levels": {
                        1: "Self-management, takes initiative",
                        2: "Mentors junior members",
                        3: "Leads small teams, project leadership",
                        4: "Department leadership, strategy",
                        5: "Organizational leadership, vision setting"
                    }
                },
                "Problem Solving": {
                    "category": "soft",
                    "description": "Analytical and creative problem solving",
                    "levels": {
                        1: "Solves routine problems",
                        2: "Breaks down complex problems",
                        3: "Creative solutions, systematic approach", 
                        4: "Complex system problems, innovation",
                        5: "Strategic problem solving, frameworks"
                    }
                },
                "Project Management": {
                    "category": "soft",
                    "description": "Project planning and execution skills",
                    "levels": {
                        1: "Task management, basic planning",
                        2: "Small project coordination",
                        3: "Full project lifecycle management",
                        4: "Multi-project coordination, stakeholder management",
                        5: "Program management, strategic planning"
                    }
                }
            },
            "categories": {
                "technical": "Technical and programming skills",
                "soft": "Interpersonal and leadership skills", 
                "domain": "Industry or domain-specific knowledge"
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_roles(self) -> Dict:
        """Load role profiles"""
        try:
            with open(self.roles_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading roles: {e}")
            return {"roles": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_roles(self, roles_data: Dict):
        """Save role profiles"""
        roles_data["last_updated"] = datetime.now().isoformat()
        with open(self.roles_file, 'w') as f:
            json.dump(roles_data, f, indent=2)
    
    def _load_skill_catalog(self) -> Dict:
        """Load skill catalog"""
        try:
            with open(self.skill_catalog_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading skill catalog: {e}")
            return self._create_default_skill_catalog()
    
    def create_role_profile(self, role_name: str, department: str, level: str,
                          skills: List[Dict], description: str = "",
                          responsibilities: List[str] = None,
                          min_experience: int = 0, preferred_experience: int = 0) -> str:
        """
        Create a new role profile
        
        Args:
            role_name: Name of the role
            department: Department this role belongs to
            level: Seniority level (junior, mid, senior, lead)
            skills: List of skill requirements with format:
                   [{"skill_name": str, "required_level": float, "importance": int, "category": str}]
            description: Role description
            responsibilities: List of key responsibilities
            min_experience: Minimum years of experience
            preferred_experience: Preferred years of experience
        
        Returns:
            Role ID of created profile
        """
        role_id = str(uuid.uuid4())
        
        # Convert skills to SkillRequirement objects
        skill_requirements = []
        for skill_dict in skills:
            req = SkillRequirement(
                skill_name=skill_dict["skill_name"],
                required_level=skill_dict.get("required_level", 3.0),
                importance=skill_dict.get("importance", 3),
                category=skill_dict.get("category", "technical"),
                description=skill_dict.get("description", ""),
                assessment_required=skill_dict.get("assessment_required", False)
            )
            skill_requirements.append(req)
        
        # Create role profile
        role_profile = RoleProfile(
            role_id=role_id,
            role_name=role_name,
            department=department,
            level=level,
            skills=skill_requirements,
            description=description,
            responsibilities=responsibilities or [],
            min_experience_years=min_experience,
            preferred_experience_years=preferred_experience
        )
        
        # Save to file
        roles_data = self._load_roles()
        roles_data["roles"][role_id] = asdict(role_profile)
        self._save_roles(roles_data)
        
        return role_id
    
    def get_role_profile(self, role_id: str) -> Optional[Dict]:
        """Get role profile by ID"""
        roles_data = self._load_roles()
        return roles_data["roles"].get(role_id)
    
    def get_role_by_name(self, role_name: str, department: str = None) -> Optional[Dict]:
        """Get role profile by name and optionally department"""
        roles_data = self._load_roles()
        
        for role_id, role_data in roles_data["roles"].items():
            if role_data["role_name"] == role_name:
                if department is None or role_data["department"] == department:
                    return role_data
        return None
    
    def get_skills_for_role(self, role_id: str) -> List[Dict]:
        """Get skill requirements for a role"""
        role_profile = self.get_role_profile(role_id)
        if not role_profile:
            return []
        return role_profile.get("skills", [])
    
    def analyze_skill_gap(self, role_id: str, user_skills: Dict[str, Dict]) -> Dict:
        """
        Analyze skill gap between user and role requirements
        
        Args:
            role_id: Target role ID
            user_skills: User's current skills in format {skill_name: {"level": float, "confidence": float}}
        
        Returns:
            Gap analysis with recommendations
        """
        role_profile = self.get_role_profile(role_id)
        if not role_profile:
            return {"error": "Role not found"}
        
        required_skills = role_profile["skills"]
        gaps = []
        strengths = []
        recommendations = []
        
        for skill_req in required_skills:
            skill_name = skill_req["skill_name"]
            required_level = skill_req["required_level"]
            importance = skill_req["importance"]
            
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
                    "category": skill_req["category"]
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
            "role_name": role_profile["role_name"],
            "department": role_profile["department"],
            "total_gaps": len(gaps),
            "high_priority_gaps": len([g for g in gaps if g["priority"] == "high"]),
            "strengths": strengths,
            "skill_gaps": gaps,
            "recommendations": recommendations,
            "overall_readiness": self._calculate_readiness_score(gaps, required_skills)
        }
    
    def _calculate_readiness_score(self, gaps: List[Dict], required_skills: List[Dict]) -> Dict:
        """Calculate overall readiness score for the role"""
        if not required_skills:
            return {"score": 0, "level": "not_ready"}
        
        total_importance = sum(skill["importance"] for skill in required_skills)
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
    
    def _get_readiness_description(self, level: str) -> str:
        """Get description for readiness level"""
        descriptions = {
            "excellent": "Candidate exceeds role requirements and is ready to start immediately",
            "good": "Candidate meets most requirements with minor gaps that can be addressed quickly",
            "fair": "Candidate has foundational skills but needs focused development in key areas",
            "needs_improvement": "Candidate needs significant skill development before being ready for this role",
            "not_ready": "Candidate lacks fundamental skills required for this role"
        }
        return descriptions.get(level, "Assessment unavailable")
    
    def get_all_roles_by_department(self, department: str) -> List[Dict]:
        """Get all roles for a specific department"""
        roles_data = self._load_roles()
        department_roles = []
        
        for role_id, role_data in roles_data["roles"].items():
            if role_data["department"] == department:
                department_roles.append(role_data)
        
        return department_roles
    
    def update_role_skills(self, role_id: str, updated_skills: List[Dict]) -> bool:
        """Update skills for an existing role"""
        try:
            roles_data = self._load_roles()
            if role_id not in roles_data["roles"]:
                return False
            
            # Convert to SkillRequirement format
            skill_requirements = []
            for skill_dict in updated_skills:
                req = SkillRequirement(
                    skill_name=skill_dict["skill_name"],
                    required_level=skill_dict.get("required_level", 3.0),
                    importance=skill_dict.get("importance", 3),
                    category=skill_dict.get("category", "technical"),
                    description=skill_dict.get("description", ""),
                    assessment_required=skill_dict.get("assessment_required", False)
                )
                skill_requirements.append(asdict(req))
            
            roles_data["roles"][role_id]["skills"] = skill_requirements
            roles_data["roles"][role_id]["updated_at"] = datetime.now().isoformat()
            
            self._save_roles(roles_data)
            return True
            
        except Exception as e:
            print(f"Error updating role skills: {e}")
            return False

# Integration with existing JD system
def migrate_existing_jd_to_role_profiles():
    """Migrate existing JD data to new role profile system"""
    manager = RoleSkillsManager()
    
    # Load existing JD data
    jd_file = os.path.join(manager.data_dir, 'jd.json')
    if os.path.exists(jd_file):
        with open(jd_file, 'r') as f:
            jd_data = json.load(f)
        
        for role_name, jd_info in jd_data.items():
            skills = []
            for skill_name, skill_info in jd_info.get("skills", {}).items():
                skills.append({
                    "skill_name": skill_name,
                    "required_level": skill_info.get("required_level", 3.0),
                    "importance": skill_info.get("importance", 3),
                    "category": "technical"  # Default category
                })
            
            # Determine department and level from role name
            department = "engineering"  # Default
            level = "mid"  # Default
            
            if "jr" in role_name.lower() or "junior" in role_name.lower():
                level = "junior"
            elif "sr" in role_name.lower() or "senior" in role_name.lower():
                level = "senior"
            
            manager.create_role_profile(
                role_name=role_name.replace("_", " ").title(),
                department=department,
                level=level,
                skills=skills,
                description=f"Migrated from JD system: {role_name}"
            )

# Default role profiles for common positions
DEFAULT_ROLE_PROFILES = {
    "frontend_developer": {
        "role_name": "Frontend Developer",
        "department": "engineering", 
        "level": "mid",
        "skills": [
            {"skill_name": "JavaScript", "required_level": 4.0, "importance": 5, "category": "technical"},
            {"skill_name": "React", "required_level": 4.0, "importance": 5, "category": "technical"},
            {"skill_name": "HTML", "required_level": 3.0, "importance": 4, "category": "technical"},
            {"skill_name": "CSS", "required_level": 3.0, "importance": 4, "category": "technical"},
            {"skill_name": "Git", "required_level": 3.0, "importance": 3, "category": "technical"},
            {"skill_name": "Communication", "required_level": 3.0, "importance": 4, "category": "soft"},
            {"skill_name": "Problem Solving", "required_level": 4.0, "importance": 5, "category": "soft"}
        ]
    },
    "data_scientist": {
        "role_name": "Data Scientist",
        "department": "data_science",
        "level": "mid", 
        "skills": [
            {"skill_name": "Python", "required_level": 4.0, "importance": 5, "category": "technical"},
            {"skill_name": "Machine Learning", "required_level": 4.0, "importance": 5, "category": "technical"},
            {"skill_name": "Data Analysis", "required_level": 4.0, "importance": 5, "category": "technical"},
            {"skill_name": "SQL", "required_level": 3.0, "importance": 4, "category": "technical"},
            {"skill_name": "Communication", "required_level": 4.0, "importance": 5, "category": "soft"},
            {"skill_name": "Problem Solving", "required_level": 5.0, "importance": 5, "category": "soft"}
        ]
    }
}

if __name__ == "__main__":
    # Test the system
    manager = RoleSkillsManager()
    
    # Create sample role profiles
    for role_key, role_config in DEFAULT_ROLE_PROFILES.items():
        role_id = manager.create_role_profile(**role_config)
        print(f"Created role profile {role_key}: {role_id}")
    
    # Test skill gap analysis
    sample_user_skills = {
        "JavaScript": {"level": 3.5, "confidence": 0.8},
        "React": {"level": 3.0, "confidence": 0.7},
        "Python": {"level": 2.0, "confidence": 0.6},
        "Communication": {"level": 3.5, "confidence": 0.8}
    }
    
    # Find frontend developer role
    frontend_role = manager.get_role_by_name("Frontend Developer", "engineering")
    if frontend_role:
        gap_analysis = manager.analyze_skill_gap(frontend_role["role_id"], sample_user_skills)
        print("\nSkill Gap Analysis:")
        print(json.dumps(gap_analysis, indent=2))
