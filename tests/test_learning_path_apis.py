import os
import sys
import pytest
from flask import Flask
from flask.testing import Flask
import os
import sys
import pytest
import json
from flask import Flask
from flask.testing import FlaskClient

# Ensure project root is in sys.path for backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.unified_server import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

class TestLearningPathAPIs:
    """Test cases for Learning Path Management APIs"""

    def test_get_learning_paths(self, client: FlaskClient):
        """Test GET /api/learning-paths"""
        resp = client.get('/api/learning-paths')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_get_learning_path_by_id(self, client: FlaskClient):
        """Test GET /api/learning-paths/<path_id>"""
        path_id = "LP2024DS001"
        resp = client.get(f'/api/learning-paths/{path_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_get_learning_path_modules(self, client: FlaskClient):
        """Test GET /api/learning-paths/<path_id>/modules"""
        path_id = "LP2024DS001"
        resp = client.get(f'/api/learning-paths/{path_id}/modules')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)  # API returns dict with modules and total_count
            assert 'modules' in data
            assert 'total_count' in data
            assert isinstance(data['modules'], list)

    def test_start_module(self, client: FlaskClient):
        """Test POST /api/modules/<module_id>/start"""
        module_id = "MOD2024001"
        payload = {"user_id": "user_001"}
        resp = client.post(f'/api/modules/{module_id}/start',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 404]

    def test_update_module_progress(self, client: FlaskClient):
        """Test PATCH /api/modules/<module_id>/progress"""
        module_id = "MOD2024001"
        payload = {
            "user_id": "user_001",
            "progress_percentage": 50,
            "time_spent_minutes": 30
        }
        resp = client.patch(f'/api/modules/{module_id}/progress',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_update_learning_path_progress(self, client: FlaskClient):
        """Test PATCH /api/learning-path-progress/<progress_id>"""
        progress_id = "progress_001"
        payload = {"status": "completed"}
        resp = client.patch(f'/api/learning-path-progress/{progress_id}',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_get_user_learning_path_progress(self, client: FlaskClient):
        """Test GET /api/learning-path-progress/<user_id>"""
        user_id = "user_001"
        resp = client.get(f'/api/learning-path-progress/{user_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, list)

    def test_get_learning_path_analytics(self, client: FlaskClient):
        """Test GET /api/learning-paths/<path_id>/analytics"""
        path_id = "LP2024DS001"
        user_id = "user_001"  # Add required user_id parameter
        resp = client.get(f'/api/learning-paths/{path_id}/analytics?user_id={user_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

# Ensure project root is in sys.path for backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.unified_server import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

class TestLearningPathAPIs:
    """Test cases for Learning Path Management APIs"""

    def test_get_learning_paths(self, client: FlaskClient):
        """Test GET /api/learning-paths"""
        resp = client.get('/api/learning-paths')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)
        assert 'results' in data
        assert 'total' in data

    def test_get_learning_path_by_id(self, client: FlaskClient):
        """Test GET /api/learning-paths/<path_id>"""
        path_id = "LP2024ENG001"
        resp = client.get(f'/api/learning-paths/{path_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_get_learning_path_modules(self, client: FlaskClient):
        """Test GET /api/learning-paths/<path_id>/modules"""
        path_id = "LP2024ENG001"
        resp = client.get(f'/api/learning-paths/{path_id}/modules')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)  # API returns dict with modules and total_count
            assert 'modules' in data
            assert 'total_count' in data
            assert isinstance(data['modules'], list)

    def test_start_module(self, client: FlaskClient):
        """Test POST /api/modules/<module_id>/start"""
        module_id = "MOD2024001"
        payload = {"user_id": "test_user"}
        resp = client.post(f'/api/modules/{module_id}/start',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 404]

    def test_update_module_progress(self, client: FlaskClient):
        """Test PATCH /api/modules/<module_id>/progress"""
        module_id = "MOD2024001"
        payload = {
            "user_id": "test_user",
            "progress_percentage": 50,
            "time_spent_minutes": 30
        }
        resp = client.patch(f'/api/modules/{module_id}/progress',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_update_learning_path_progress(self, client: FlaskClient):
        """Test PATCH /api/learning-path-progress/<progress_id>"""
        progress_id = "progress_001"
        payload = {"status": "completed"}
        resp = client.patch(f'/api/learning-path-progress/{progress_id}',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code in [200, 404]

    def test_get_user_learning_path_progress(self, client: FlaskClient):
        """Test GET /api/learning-path-progress/<user_id>"""
        user_id = "test_user"
        resp = client.get(f'/api/learning-path-progress/{user_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, list)

    def test_get_learning_path_analytics(self, client: FlaskClient):
        """Test GET /api/learning-paths/<path_id>/analytics"""
        path_id = "LP2024ENG001"
        resp = client.get(f'/api/learning-paths/{path_id}/analytics')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)
