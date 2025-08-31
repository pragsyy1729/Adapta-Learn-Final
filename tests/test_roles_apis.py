import os
import sys
import pytest
from flask import Flask
from flask.testing import FlaskClient
import json

# Ensure project root is in sys.path for backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.unified_server import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

class TestRolesAPIs:
    """Test cases for Role Management APIs"""

    def test_get_all_roles(self, client: FlaskClient):
        """Test GET /api/roles"""
        resp = client.get('/api/roles')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_get_role_by_id(self, client: FlaskClient):
        """Test GET /api/roles/<role_id>"""
        role_id = "role_001"
        resp = client.get(f'/api/roles/{role_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_create_role(self, client: FlaskClient):
        """Test POST /api/roles"""
        payload = {
            "name": "Test Role",
            "department": "ENG2024001",
            "description": "Test role description",
            "required_skills": ["Python", "JavaScript"]
        }
        resp = client.post('/api/roles',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_update_role(self, client: FlaskClient):
        """Test PUT /api/roles/<role_id>"""
        role_id = "role_001"
        payload = {"description": "Updated description"}
        resp = client.put(f'/api/roles/{role_id}',
                         data=json.dumps(payload),
                         content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_delete_role(self, client: FlaskClient):
        """Test DELETE /api/roles/<role_id>"""
        role_id = "role_001"
        resp = client.delete(f'/api/roles/{role_id}')
        assert resp.status_code in [200, 404]

    def test_add_skill_to_role(self, client: FlaskClient):
        """Test POST /api/roles/<role_id>/skills"""
        role_id = "1"  # Use correct role ID from data
        payload = {"name": "Python", "proficiency": 3}  # Use correct field names
        resp = client.post(f'/api/roles/{role_id}/skills',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_remove_skill_from_role(self, client: FlaskClient):
        """Test DELETE /api/roles/<role_id>/skills/<skill_name>"""
        role_id = "role_001"
        skill_name = "React"
        resp = client.delete(f'/api/roles/{role_id}/skills/{skill_name}')
        assert resp.status_code in [200, 404]
