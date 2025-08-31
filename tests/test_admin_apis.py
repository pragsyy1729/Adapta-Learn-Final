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

class TestAdminAPIs:
    """Test cases for Admin Management APIs"""

    def test_get_admin_stats_new_joiners(self, client: FlaskClient):
        """Test GET /api/admin/stats/new-joiners"""
        resp = client.get('/api/admin/stats/new-joiners')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_get_admin_stats_active_enrollments(self, client: FlaskClient):
        """Test GET /api/admin/stats/active-enrollments"""
        resp = client.get('/api/admin/stats/active-enrollments')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_get_admin_learning_paths(self, client: FlaskClient):
        """Test GET /api/admin/learning-paths"""
        resp = client.get('/api/admin/learning-paths')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_create_admin_learning_path(self, client: FlaskClient):
        """Test POST /api/admin/learning-paths"""
        payload = {
            "title": "Test Learning Path",
            "description": "Test description",
            "department": "ENG2024001",
            "difficulty": "Beginner",
            "duration": "4 weeks"
        }
        resp = client.post('/api/admin/learning-paths',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201]

    def test_update_admin_learning_path(self, client: FlaskClient):
        """Test PUT /api/admin/learning-paths/<path_id>"""
        path_id = "LP2024ENG001"
        payload = {"title": "Updated Title"}
        resp = client.put(f'/api/admin/learning-paths/{path_id}',
                         data=json.dumps(payload),
                         content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_delete_admin_learning_path(self, client: FlaskClient):
        """Test DELETE /api/admin/learning-paths/<path_id>"""
        path_id = "LP2024ENG001"
        resp = client.delete(f'/api/admin/learning-paths/{path_id}')
        assert resp.status_code in [200, 404]

    def test_get_admin_users(self, client: FlaskClient):
        """Test GET /api/admin/users"""
        resp = client.get('/api/admin/users')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_create_admin_user(self, client: FlaskClient):
        """Test POST /api/admin/users"""
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "department": "ENG2024001"
        }
        resp = client.post('/api/admin/users',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201]

    def test_update_admin_user(self, client: FlaskClient):
        """Test PUT /api/admin/users/<email>"""
        email = "test@example.com"
        payload = {"name": "Updated Name"}
        resp = client.put(f'/api/admin/users/{email}',
                         data=json.dumps(payload),
                         content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_delete_admin_user(self, client: FlaskClient):
        """Test DELETE /api/admin/users/<email>"""
        email = "test@example.com"
        resp = client.delete(f'/api/admin/users/{email}')
        assert resp.status_code in [200, 404]

    def test_get_admin_modules(self, client: FlaskClient):
        """Test GET /api/admin/modules"""
        resp = client.get('/api/admin/modules')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_create_admin_module(self, client: FlaskClient):
        """Test POST /api/admin/modules"""
        payload = {
            "title": "Test Module",
            "description": "Test module description",
            "learning_path_id": "LP2024ENG001"
        }
        resp = client.post('/api/admin/modules',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201]

    def test_update_admin_module(self, client: FlaskClient):
        """Test PUT /api/admin/modules/<module_id>"""
        module_id = "MOD2024001"
        payload = {"title": "Updated Module"}
        resp = client.put(f'/api/admin/modules/{module_id}',
                         data=json.dumps(payload),
                         content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_delete_admin_module(self, client: FlaskClient):
        """Test DELETE /api/admin/modules/<module_id>"""
        module_id = "MOD2024001"
        resp = client.delete(f'/api/admin/modules/{module_id}')
        assert resp.status_code in [200, 404]

    def test_get_admin_departments(self, client: FlaskClient):
        """Test GET /api/admin/departments"""
        resp = client.get('/api/admin/departments')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_add_department_documentation(self, client: FlaskClient):
        """Test POST /api/admin/departments/<dept_id>/documentation"""
        dept_id = "ENG2024001"
        payload = {
            "name": "Onboarding Guide",
            "document_content": "Welcome to Engineering department"
        }
        resp = client.post(f'/api/admin/departments/{dept_id}/documentation',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_get_department_documentation(self, client: FlaskClient):
        """Test GET /api/admin/departments/<dept_id>/documentation"""
        dept_id = "ENG2024001"
        resp = client.get(f'/api/admin/departments/{dept_id}/documentation')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_sync_module_counts(self, client: FlaskClient):
        """Test POST /api/admin/sync-module-counts"""
        resp = client.post('/api/admin/sync-module-counts')
        assert resp.status_code in [200, 404]
