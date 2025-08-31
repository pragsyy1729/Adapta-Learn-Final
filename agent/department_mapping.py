"""
Department Learning Path Mapping System
Maps departments to mandatory learning paths for onboarding
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class DepartmentLearningPath:
    department: str
    learning_path_id: str
    is_mandatory: bool = True
    priority: int = 1  # 1 = highest priority
    estimated_duration_weeks: Optional[int] = None
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []

@dataclass
class DepartmentConfig:
    department_id: str
    department_name: str
    learning_paths: List[DepartmentLearningPath]
    onboarding_duration_weeks: int = 8
    default_manager: Optional[str] = None
    description: str = ""
    
class DepartmentLearningPathManager:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.data_dir = data_dir
        self.dept_mapping_file = os.path.join(data_dir, 'department_learning_paths.json')
        self.departments_file = os.path.join(data_dir, 'department.json')
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize data files with default structure"""
        if not os.path.exists(self.dept_mapping_file):
            default_mappings = {
                "departments": {}
            }
            self._save_mappings(default_mappings)
        
        if not os.path.exists(self.departments_file):
            default_departments = {
                "departments": [
                    {
                        "id": "engineering",
                        "name": "Engineering",
                        "description": "Software development and technical teams",
                        "onboarding_duration_weeks": 8
                    },
                    {
                        "id": "data_science", 
                        "name": "Data Science",
                        "description": "Data analysis, machine learning, and analytics teams",
                        "onboarding_duration_weeks": 10
                    },
                    {
                        "id": "product",
                        "name": "Product Management",
                        "description": "Product strategy and management teams",
                        "onboarding_duration_weeks": 6
                    },
                    {
                        "id": "design",
                        "name": "Design",
                        "description": "UX/UI design and creative teams",
                        "onboarding_duration_weeks": 6
                    },
                    {
                        "id": "marketing",
                        "name": "Marketing",
                        "description": "Marketing and growth teams",
                        "onboarding_duration_weeks": 4
                    }
                ]
            }
            with open(self.departments_file, 'w') as f:
                json.dump(default_departments, f, indent=2)
    
    def _load_mappings(self) -> Dict:
        """Load department learning path mappings"""
        try:
            with open(self.dept_mapping_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading department mappings: {e}")
            return {"departments": {}}
    
    def _save_mappings(self, mappings: Dict):
        """Save department learning path mappings"""
        with open(self.dept_mapping_file, 'w') as f:
            json.dump(mappings, f, indent=2)
    
    def _load_departments(self) -> Dict:
        """Load department configurations"""
        try:
            with open(self.departments_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading departments: {e}")
            return {"departments": []}
    
    def add_department_learning_path(self, department_id: str, learning_path_id: str, 
                                   is_mandatory: bool = True, priority: int = 1,
                                   estimated_duration_weeks: Optional[int] = None,
                                   prerequisites: List[str] = None) -> bool:
        """
        Add a learning path to a department's onboarding requirements
        
        Args:
            department_id: ID of the department
            learning_path_id: ID of the learning path
            is_mandatory: Whether this path is mandatory for all department joiners
            priority: Priority level (1 = highest)
            estimated_duration_weeks: Expected completion time
            prerequisites: List of prerequisite learning path IDs
        
        Returns:
            True if successful, False otherwise
        """
        try:
            mappings = self._load_mappings()
            
            if department_id not in mappings["departments"]:
                mappings["departments"][department_id] = []
            
            # Check if this learning path already exists for the department
            existing = next((lp for lp in mappings["departments"][department_id] 
                           if lp["learning_path_id"] == learning_path_id), None)
            
            if existing:
                # Update existing mapping
                existing.update({
                    "is_mandatory": is_mandatory,
                    "priority": priority,
                    "estimated_duration_weeks": estimated_duration_weeks,
                    "prerequisites": prerequisites or []
                })
            else:
                # Add new mapping
                new_mapping = DepartmentLearningPath(
                    department=department_id,
                    learning_path_id=learning_path_id,
                    is_mandatory=is_mandatory,
                    priority=priority,
                    estimated_duration_weeks=estimated_duration_weeks,
                    prerequisites=prerequisites or []
                )
                mappings["departments"][department_id].append(asdict(new_mapping))
            
            # Sort by priority
            mappings["departments"][department_id].sort(key=lambda x: x["priority"])
            
            self._save_mappings(mappings)
            return True
            
        except Exception as e:
            print(f"Error adding department learning path: {e}")
            return False
    
    def remove_department_learning_path(self, department_id: str, learning_path_id: str) -> bool:
        """Remove a learning path from a department"""
        try:
            mappings = self._load_mappings()
            
            if department_id in mappings["departments"]:
                mappings["departments"][department_id] = [
                    lp for lp in mappings["departments"][department_id]
                    if lp["learning_path_id"] != learning_path_id
                ]
                self._save_mappings(mappings)
                return True
            return False
            
        except Exception as e:
            print(f"Error removing department learning path: {e}")
            return False
    
    def get_department_learning_paths(self, department_id: str) -> List[Dict]:
        """Get all learning paths for a department"""
        mappings = self._load_mappings()
        return mappings["departments"].get(department_id, [])
    
    def get_mandatory_paths_for_department(self, department_id: str) -> List[Dict]:
        """Get only mandatory learning paths for a department"""
        all_paths = self.get_department_learning_paths(department_id)
        return [lp for lp in all_paths if lp.get("is_mandatory", True)]
    
    def get_all_departments(self) -> List[Dict]:
        """Get all department configurations"""
        departments_data = self._load_departments()
        return departments_data.get("departments", [])
    
    def get_onboarding_plan_for_user(self, department_id: str, user_role: str = None) -> Dict:
        """
        Generate complete onboarding plan for a user joining a department
        
        Args:
            department_id: Department the user is joining
            user_role: Specific role within department (optional)
        
        Returns:
            Dictionary with onboarding plan details
        """
        try:
            # Get department info
            departments = self.get_all_departments()
            dept_info = next((d for d in departments if d["id"] == department_id), None)
            
            if not dept_info:
                return {"error": f"Department {department_id} not found"}
            
            # Get learning paths for department
            learning_paths = self.get_department_learning_paths(department_id)
            mandatory_paths = [lp for lp in learning_paths if lp.get("is_mandatory", True)]
            optional_paths = [lp for lp in learning_paths if not lp.get("is_mandatory", True)]
            
            # Calculate total estimated duration
            total_weeks = 0
            for path in mandatory_paths:
                if path.get("estimated_duration_weeks"):
                    total_weeks += path["estimated_duration_weeks"]
            
            # If no specific durations, use department default
            if total_weeks == 0:
                total_weeks = dept_info.get("onboarding_duration_weeks", 8)
            
            return {
                "department": dept_info,
                "mandatory_learning_paths": mandatory_paths,
                "optional_learning_paths": optional_paths,
                "estimated_total_weeks": total_weeks,
                "onboarding_phases": self._create_onboarding_phases(mandatory_paths),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error generating onboarding plan: {str(e)}"}
    
    def _create_onboarding_phases(self, learning_paths: List[Dict]) -> List[Dict]:
        """Create phased onboarding plan from learning paths"""
        phases = []
        current_phase = 1
        
        # Group by priority
        priority_groups = {}
        for lp in learning_paths:
            priority = lp.get("priority", 1)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(lp)
        
        # Create phases
        for priority in sorted(priority_groups.keys()):
            paths_in_phase = priority_groups[priority]
            
            phase_duration = sum(
                lp.get("estimated_duration_weeks", 2) 
                for lp in paths_in_phase
            )
            
            phases.append({
                "phase": current_phase,
                "name": f"Phase {current_phase}",
                "learning_paths": paths_in_phase,
                "estimated_weeks": phase_duration,
                "description": f"Priority {priority} onboarding components"
            })
            
            current_phase += 1
        
        return phases
    
    def bulk_setup_department_paths(self, department_mappings: Dict[str, List[Dict]]):
        """
        Bulk setup of department learning path mappings
        
        Args:
            department_mappings: Dict mapping department_id to list of learning path configs
        """
        for dept_id, path_configs in department_mappings.items():
            for config in path_configs:
                self.add_department_learning_path(
                    department_id=dept_id,
                    learning_path_id=config["learning_path_id"],
                    is_mandatory=config.get("is_mandatory", True),
                    priority=config.get("priority", 1),
                    estimated_duration_weeks=config.get("estimated_duration_weeks"),
                    prerequisites=config.get("prerequisites", [])
                )

# Integration function for the existing system
def get_onboarding_learning_paths_for_user(department_id: str, user_profile: Dict = None) -> List[str]:
    """
    Get recommended learning paths for user onboarding based on department
    
    Args:
        department_id: Department the user is joining
        user_profile: User profile information (optional, for future role-specific recommendations)
    
    Returns:
        List of learning path IDs recommended for onboarding
    """
    manager = DepartmentLearningPathManager()
    
    # Get mandatory learning paths for department
    mandatory_paths = manager.get_mandatory_paths_for_department(department_id)
    
    # Extract just the learning path IDs
    path_ids = [lp["learning_path_id"] for lp in mandatory_paths]
    
    return path_ids

# Default department-learning path mappings for initial setup
DEFAULT_DEPARTMENT_MAPPINGS = {
    "engineering": [
        {
            "learning_path_id": "0b8de18342454b2ca062f0a4b4c86956",  # React Development Track
            "is_mandatory": True,
            "priority": 1,
            "estimated_duration_weeks": 8
        }
    ],
    "data_science": [
        {
            "learning_path_id": "python_fundamentals",
            "is_mandatory": True,
            "priority": 1,
            "estimated_duration_weeks": 6
        },
        {
            "learning_path_id": "ml_basics",
            "is_mandatory": True,
            "priority": 2,
            "estimated_duration_weeks": 8
        }
    ]
}

if __name__ == "__main__":
    # Test the system
    manager = DepartmentLearningPathManager()
    
    # Setup default mappings
    manager.bulk_setup_department_paths(DEFAULT_DEPARTMENT_MAPPINGS)
    
    # Test getting onboarding plan
    plan = manager.get_onboarding_plan_for_user("engineering")
    print("Engineering Onboarding Plan:")
    print(json.dumps(plan, indent=2))
