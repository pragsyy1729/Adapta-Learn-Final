"""
Dynamic Role Management System
API-based role and skill management without JSON file dependencies
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
from flask import Blueprint, request, jsonify

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

class DynamicRoleManager:
    """
    Dynamic role management system that can be managed via API
    No more manual JSON file editing!
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.data_dir = data_dir
        self.roles_file = os.path.join(data_dir, 'dynamic_roles.json')

        # In-memory cache for better performance
        self._roles_cache = None
        self._last_cache_update = None

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize with default roles if file doesn't exist
        self._initialize_default_roles()

    def _initialize_default_roles(self):
        """Initialize with common role profiles"""
        if not os.path.exists(self.roles_file):
            default_roles = self._get_default_roles()
            self._save_roles_to_file(default_roles)

    def _get_default_roles(self) -> Dict[str, RoleProfile]:
        """Get default role profiles for common positions"""
        return {
            "frontend_dev_mid": RoleProfile(
                role_id="frontend_dev_mid",
                role_name="Frontend Developer",
                department="engineering",
                level="mid",
                skills=[
                    SkillRequirement("JavaScript", 4.0, 5, "technical", "Modern JavaScript (ES6+)"),
                    SkillRequirement("React", 4.0, 5, "technical", "React.js framework"),
                    SkillRequirement("HTML", 3.0, 4, "technical", "HTML5 and semantic markup"),
                    SkillRequirement("CSS", 3.0, 4, "technical", "CSS3 and responsive design"),
                    SkillRequirement("Git", 3.0, 3, "technical", "Version control"),
                    SkillRequirement("Communication", 3.0, 4, "soft", "Team communication"),
                    SkillRequirement("Problem Solving", 4.0, 5, "soft", "Technical problem solving")
                ],
                description="Mid-level frontend developer role",
                responsibilities=[
                    "Develop responsive web applications",
                    "Collaborate with design and backend teams",
                    "Write clean, maintainable code",
                    "Participate in code reviews"
                ]
            ),

            "data_scientist_mid": RoleProfile(
                role_id="data_scientist_mid",
                role_name="Data Scientist",
                department="data_science",
                level="mid",
                skills=[
                    SkillRequirement("Python", 4.0, 5, "technical", "Python for data science"),
                    SkillRequirement("Machine Learning", 4.0, 5, "technical", "ML algorithms and models"),
                    SkillRequirement("Data Analysis", 4.0, 5, "technical", "Statistical analysis"),
                    SkillRequirement("SQL", 3.0, 4, "technical", "Database querying"),
                    SkillRequirement("Communication", 4.0, 5, "soft", "Presenting insights"),
                    SkillRequirement("Problem Solving", 5.0, 5, "soft", "Analytical thinking")
                ],
                description="Mid-level data scientist role",
                responsibilities=[
                    "Build and deploy ML models",
                    "Analyze large datasets",
                    "Create data visualizations",
                    "Present findings to stakeholders"
                ]
            ),

            "python_dev_mid": RoleProfile(
                role_id="python_dev_mid",
                role_name="Python Developer",
                department="engineering",
                level="mid",
                skills=[
                    SkillRequirement("Python", 4.0, 5, "technical", "Python programming"),
                    SkillRequirement("Flask", 3.0, 4, "technical", "Flask web framework"),
                    SkillRequirement("SQL", 3.0, 4, "technical", "Database operations"),
                    SkillRequirement("Git", 3.0, 3, "technical", "Version control"),
                    SkillRequirement("Docker", 2.0, 2, "technical", "Containerization"),
                    SkillRequirement("Communication", 3.0, 4, "soft", "Team collaboration")
                ],
                description="Mid-level Python developer role",
                responsibilities=[
                    "Develop Python applications",
                    "Design and implement APIs",
                    "Write unit tests",
                    "Debug and optimize code"
                ]
            )
        }

    def _load_roles_from_file(self) -> Dict[str, RoleProfile]:
        """Load roles from JSON file"""
        try:
            with open(self.roles_file, 'r') as f:
                data = json.load(f)

            # Convert dict back to RoleProfile objects
            roles = {}
            for role_id, role_dict in data.get("roles", {}).items():
                # Convert skill dicts back to SkillRequirement objects
                skills = []
                for skill_dict in role_dict.get("skills", []):
                    skills.append(SkillRequirement(**skill_dict))

                role_dict["skills"] = skills
                roles[role_id] = RoleProfile(**role_dict)

            return roles
        except Exception as e:
            print(f"Error loading roles: {e}")
            return self._get_default_roles()

    def _save_roles_to_file(self, roles: Dict[str, RoleProfile]):
        """Save roles to JSON file"""
        try:
            # Convert RoleProfile objects to dicts for JSON serialization
            data = {
                "roles": {role_id: asdict(role) for role_id, role in roles.items()},
                "last_updated": datetime.now().isoformat()
            }

            with open(self.roles_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving roles: {e}")

    def get_role_by_name(self, role_name: str, department: str = None) -> Optional[RoleProfile]:
        """Get role profile by name and optionally department"""
        roles = self._load_roles_from_file()

        for role in roles.values():
            if role.role_name == role_name:
                if department is None or role.department == department:
                    return role
        return None

    def get_role_by_id(self, role_id: str) -> Optional[RoleProfile]:
        """Get role profile by ID"""
        roles = self._load_roles_from_file()
        return roles.get(role_id)

    def get_all_roles(self) -> List[RoleProfile]:
        """Get all role profiles"""
        roles = self._load_roles_from_file()
        return list(roles.values())

    def get_roles_by_department(self, department: str) -> List[RoleProfile]:
        """Get all roles for a department"""
        roles = self._load_roles_from_file()
        return [role for role in roles.values() if role.department == department]

    def create_role(self, role_name: str, department: str, level: str,
                   skills: List[Dict], description: str = "",
                   responsibilities: List[str] = None) -> str:
        """Create a new role profile"""
        role_id = f"{role_name.lower().replace(' ', '_')}_{level}"

        # Convert skill dicts to SkillRequirement objects
        skill_requirements = []
        for skill_dict in skills:
            skill_requirements.append(SkillRequirement(**skill_dict))

        # Create role profile
        role = RoleProfile(
            role_id=role_id,
            role_name=role_name,
            department=department,
            level=level,
            skills=skill_requirements,
            description=description,
            responsibilities=responsibilities or []
        )

        # Save to file
        roles = self._load_roles_from_file()
        roles[role_id] = role
        self._save_roles_to_file(roles)

        return role_id

    def update_role(self, role_id: str, updates: Dict) -> bool:
        """Update an existing role"""
        try:
            roles = self._load_roles_from_file()
            if role_id not in roles:
                return False

            role = roles[role_id]

            # Update fields
            for key, value in updates.items():
                if hasattr(role, key):
                    setattr(role, key, value)

            role.updated_at = datetime.now().isoformat()

            # Save updated roles
            self._save_roles_to_file(roles)
            return True
        except Exception as e:
            print(f"Error updating role: {e}")
            return False

    def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        try:
            roles = self._load_roles_from_file()
            if role_id not in roles:
                return False

            del roles[role_id]
            self._save_roles_to_file(roles)
            return True
        except Exception as e:
            print(f"Error deleting role: {e}")
            return False

    def get_skills_for_role(self, role_id: str) -> List[str]:
        """Get skill names for a role (for backward compatibility)"""
        role = self.get_role_by_id(role_id)
        if not role:
            return []
        return [skill.skill_name for skill in role.skills]

    def add_skill_to_role(self, role_id: str, skill: Dict) -> bool:
        """Add a skill to an existing role"""
        try:
            roles = self._load_roles_from_file()
            if role_id not in roles:
                return False

            role = roles[role_id]
            new_skill = SkillRequirement(**skill)
            role.skills.append(new_skill)
            role.updated_at = datetime.now().isoformat()

            self._save_roles_to_file(roles)
            return True
        except Exception as e:
            print(f"Error adding skill: {e}")
            return False

# Flask Blueprint for API endpoints
role_api = Blueprint('role_management', __name__)
role_manager = DynamicRoleManager()

@role_api.route('/roles', methods=['GET'])
def get_roles():
    """Get all roles"""
    try:
        roles = role_manager.get_all_roles()
        return jsonify({
            "success": True,
            "data": [asdict(role) for role in roles]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@role_api.route('/roles/<role_id>', methods=['GET'])
def get_role(role_id):
    """Get specific role"""
    try:
        role = role_manager.get_role_by_id(role_id)
        if not role:
            return jsonify({"success": False, "error": "Role not found"}), 404

        return jsonify({
            "success": True,
            "data": asdict(role)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@role_api.route('/roles', methods=['POST'])
def create_role():
    """Create new role"""
    try:
        data = request.get_json() or {}

        required_fields = ['role_name', 'department', 'level', 'skills']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        role_id = role_manager.create_role(
            role_name=data['role_name'],
            department=data['department'],
            level=data['level'],
            skills=data['skills'],
            description=data.get('description', ''),
            responsibilities=data.get('responsibilities', [])
        )

        # Return the created role data
        created_role = role_manager.get_role_by_id(role_id)
        if created_role:
            return jsonify({
                "success": True,
                "message": "Role created successfully",
                "data": asdict(created_role)
            }), 201
        else:
            return jsonify({"success": False, "error": "Failed to retrieve created role"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@role_api.route('/roles/<role_id>', methods=['PUT'])
def update_role(role_id):
    """Update existing role"""
    try:
        data = request.get_json() or {}
        success = role_manager.update_role(role_id, data)

        if not success:
            return jsonify({"success": False, "error": "Role not found or update failed"}), 404

        # Return the updated role data
        updated_role = role_manager.get_role_by_id(role_id)
        if updated_role:
            return jsonify({
                "success": True,
                "message": "Role updated successfully",
                "data": asdict(updated_role)
            })
        else:
            return jsonify({"success": False, "error": "Failed to retrieve updated role"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@role_api.route('/roles/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    """Delete role"""
    try:
        success = role_manager.delete_role(role_id)
        if not success:
            return jsonify({"success": False, "error": "Role not found"}), 404

        return jsonify({
            "success": True,
            "message": "Role deleted successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@role_api.route('/departments/<department>/roles', methods=['GET'])
def get_department_roles(department):
    """Get roles for a department"""
    try:
        roles = role_manager.get_roles_by_department(department)
        return jsonify({
            "success": True,
            "data": [asdict(role) for role in roles]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@role_api.route('/roles/<role_id>/skills', methods=['POST'])
def add_skill_to_role(role_id):
    """Add skill to role"""
    try:
        data = request.get_json() or {}
        success = role_manager.add_skill_to_role(role_id, data)

        if not success:
            return jsonify({"success": False, "error": "Role not found or skill addition failed"}), 404

        return jsonify({
            "success": True,
            "message": "Skill added successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Integration function for existing systems
def get_target_skills_for_role(role_name: str, department: str = None) -> List[str]:
    """
    Get target skills for a role - replacement for old JSON-based approach
    """
    role = role_manager.get_role_by_name(role_name, department)
    if not role:
        return []
    return [skill.skill_name for skill in role.skills]

def get_role_profile_for_analysis(role_name: str, department: str = None) -> Optional[Dict]:
    """
    Get complete role profile for analysis - replacement for old system
    """
    role = role_manager.get_role_by_name(role_name, department)
    if not role:
        return None
    return asdict(role)

if __name__ == "__main__":
    # Test the dynamic role manager
    manager = DynamicRoleManager()

    # Test creating a new role
    new_role_id = manager.create_role(
        role_name="Backend Developer",
        department="engineering",
        level="senior",
        skills=[
            {"skill_name": "Python", "required_level": 5.0, "importance": 5, "category": "technical"},
            {"skill_name": "Django", "required_level": 4.0, "importance": 4, "category": "technical"},
            {"skill_name": "PostgreSQL", "required_level": 4.0, "importance": 4, "category": "technical"}
        ],
        description="Senior backend developer role"
    )

    print(f"Created new role: {new_role_id}")

    # Test getting roles
    roles = manager.get_all_roles()
    print(f"Total roles: {len(roles)}")

    for role in roles:
        print(f"- {role.role_name} ({role.department}) - {len(role.skills)} skills")
