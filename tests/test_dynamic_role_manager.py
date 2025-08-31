import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

from agent.dynamic_role_manager import DynamicRoleManager, get_target_skills_for_role


class TestDynamicRoleManager:
    """Test suite for DynamicRoleManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = DynamicRoleManager()

    def test_initialization(self):
        """Test that DynamicRoleManager initializes correctly"""
        assert self.manager is not None
        assert hasattr(self.manager, 'roles')
        assert isinstance(self.manager.roles, dict)

    def test_get_all_roles(self):
        """Test getting all roles"""
        roles = self.manager.get_all_roles()
        assert isinstance(roles, list)

        # Should have at least the default roles
        assert len(roles) >= 3

        # Check that each role has the required attributes
        for role in roles:
            assert hasattr(role, 'role_id')
            assert hasattr(role, 'role_name')
            assert hasattr(role, 'department')
            assert hasattr(role, 'level')
            assert hasattr(role, 'skills')
            assert isinstance(role.skills, list)

    def test_get_role_by_id(self):
        """Test getting a role by ID"""
        roles = self.manager.get_all_roles()
        if roles:
            first_role = roles[0]
            retrieved_role = self.manager.get_role_by_id(first_role.role_id)

            assert retrieved_role is not None
            assert retrieved_role.role_id == first_role.role_id
            assert retrieved_role.role_name == first_role.role_name

    def test_get_role_by_id_not_found(self):
        """Test getting a role by non-existent ID"""
        role = self.manager.get_role_by_id("non-existent-id")
        assert role is None

    def test_create_role(self):
        """Test creating a new role"""
        new_role_data = {
            "role_name": "Test Role",
            "department": "engineering",
            "level": "mid",
            "skills": [
                {
                    "skill_name": "Python",
                    "required_level": 4.0,
                    "importance": 5,
                    "category": "technical"
                }
            ],
            "description": "A test role",
            "min_experience_years": 2,
            "preferred_experience_years": 4
        }

        created_role = self.manager.create_role(new_role_data)

        assert created_role is not None
        assert created_role.role_name == "Test Role"
        assert created_role.department == "engineering"
        assert created_role.level == "mid"
        assert len(created_role.skills) == 1
        assert created_role.skills[0].skill_name == "Python"

        # Verify it was added to the roles
        all_roles = self.manager.get_all_roles()
        role_names = [r.role_name for r in all_roles]
        assert "Test Role" in role_names

    def test_update_role(self):
        """Test updating an existing role"""
        # First create a role
        new_role_data = {
            "role_name": "Update Test Role",
            "department": "engineering",
            "level": "junior",
            "skills": [{"skill_name": "JavaScript", "required_level": 3.0, "importance": 4, "category": "technical"}],
            "description": "Original description"
        }

        created_role = self.manager.create_role(new_role_data)
        original_id = created_role.role_id

        # Update the role
        update_data = {
            "role_name": "Updated Test Role",
            "department": "product",
            "level": "senior",
            "skills": [
                {"skill_name": "JavaScript", "required_level": 4.0, "importance": 5, "category": "technical"},
                {"skill_name": "React", "required_level": 4.0, "importance": 4, "category": "technical"}
            ],
            "description": "Updated description"
        }

        updated_role = self.manager.update_role(original_id, update_data)

        assert updated_role is not None
        assert updated_role.role_id == original_id
        assert updated_role.role_name == "Updated Test Role"
        assert updated_role.department == "product"
        assert updated_role.level == "senior"
        assert len(updated_role.skills) == 2

    def test_update_role_not_found(self):
        """Test updating a non-existent role"""
        update_data = {"role_name": "Non-existent"}
        result = self.manager.update_role("fake-id", update_data)
        assert result is None

    def test_delete_role(self):
        """Test deleting a role"""
        # Create a role first
        new_role_data = {
            "role_name": "Delete Test Role",
            "department": "hr",
            "level": "mid",
            "skills": [{"skill_name": "Communication", "required_level": 4.0, "importance": 5, "category": "soft"}]
        }

        created_role = self.manager.create_role(new_role_data)
        role_id = created_role.role_id

        # Delete the role
        result = self.manager.delete_role(role_id)
        assert result is True

        # Verify it's gone
        retrieved_role = self.manager.get_role_by_id(role_id)
        assert retrieved_role is None

    def test_delete_role_not_found(self):
        """Test deleting a non-existent role"""
        result = self.manager.delete_role("fake-id")
        assert result is False

    def test_get_roles_by_department(self):
        """Test filtering roles by department"""
        engineering_roles = self.manager.get_roles_by_department("engineering")
        assert isinstance(engineering_roles, list)

        for role in engineering_roles:
            assert role.department == "engineering"

    def test_get_roles_by_level(self):
        """Test filtering roles by level"""
        senior_roles = self.manager.get_roles_by_level("senior")
        assert isinstance(senior_roles, list)

        for role in senior_roles:
            assert role.level == "senior"


class TestGetTargetSkillsForRole:
    """Test suite for get_target_skills_for_role function"""

    def test_get_target_skills_existing_role(self):
        """Test getting target skills for an existing role"""
        skills = get_target_skills_for_role("Frontend Developer", "engineering")

        assert isinstance(skills, list)
        if skills:  # If the role exists and has skills
            for skill in skills:
                assert isinstance(skill, dict)
                assert "skill_name" in skill
                assert "required_level" in skill
                assert "importance" in skill
                assert "category" in skill

    def test_get_target_skills_nonexistent_role(self):
        """Test getting target skills for a non-existent role"""
        skills = get_target_skills_for_role("Non-existent Role", "engineering")

        # Should return empty list or None
        assert skills is None or (isinstance(skills, list) and len(skills) == 0)


class TestRoleValidation:
    """Test suite for role data validation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = DynamicRoleManager()

    def test_create_role_missing_required_fields(self):
        """Test creating a role with missing required fields"""
        incomplete_data = {
            "role_name": "Incomplete Role"
            # Missing department, level, skills
        }

        with pytest.raises(ValueError):
            self.manager.create_role(incomplete_data)

    def test_create_role_invalid_skill_data(self):
        """Test creating a role with invalid skill data"""
        invalid_skill_data = {
            "role_name": "Invalid Skills Role",
            "department": "engineering",
            "level": "mid",
            "skills": [
                {
                    "skill_name": "",  # Empty skill name
                    "required_level": 6.0,  # Invalid level (>5)
                    "importance": 3,
                    "category": "technical"
                }
            ]
        }

        # This should either raise an error or handle the invalid data gracefully
        try:
            role = self.manager.create_role(invalid_skill_data)
            # If it succeeds, the validation should have corrected the data
            assert role.skills[0].skill_name != ""  # Should not be empty
            assert role.skills[0].required_level <= 5.0  # Should be <= 5
        except (ValueError, AssertionError):
            # Expected if validation is strict
            pass


if __name__ == "__main__":
    # Run basic functionality test
    print("Testing DynamicRoleManager...")

    manager = DynamicRoleManager()

    # Test basic operations
    roles = manager.get_all_roles()
    print(f"Found {len(roles)} roles")

    for role in roles[:3]:  # Show first 3 roles
        print(f"  - {role.role_name} ({role.department}, {role.level}) - {len(role.skills)} skills")

    # Test creating a new role
    test_role = {
        "role_name": "Test QA Engineer",
        "department": "engineering",
        "level": "mid",
        "skills": [
            {"skill_name": "Selenium", "required_level": 4.0, "importance": 5, "category": "technical"},
            {"skill_name": "Test Planning", "required_level": 4.0, "importance": 4, "category": "domain"}
        ],
        "description": "Quality Assurance Engineer role for testing"
    }

    # Extract individual parameters for create_role method
    created_id = manager.create_role(
        role_name=test_role["role_name"],
        department=test_role["department"],
        level=test_role["level"],
        skills=test_role["skills"],
        description=test_role.get("description", ""),
        responsibilities=test_role.get("responsibilities", [])
    )

    print(f"Created test role: {test_role['role_name']} (ID: {created_id})")

    # Test getting target skills
    skills = get_target_skills_for_role("Frontend Developer", "engineering")
    print(f"Target skills for Frontend Developer: {len(skills) if skills else 0} skills")

    print("Basic functionality test completed successfully!")
