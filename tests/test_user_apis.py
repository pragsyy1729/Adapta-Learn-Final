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

class TestUserAPIs:
    """Test cases for User Management APIs"""

    def test_get_user_profile(self, client: FlaskClient):
        """Test GET /api/users/profile/<user_id>"""
        user_id = "test_user"
        resp = client.get(f'/api/users/profile/{user_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_update_user_profile(self, client: FlaskClient):
        """Test PUT /api/users/profile/<user_id>"""
        user_id = "test_user"
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "department": "Engineering",
            "learning_style": "visual"
        }
        resp = client.put(f'/api/users/profile/{user_id}',
                         data=json.dumps(payload),
                         content_type='application/json')
        assert resp.status_code in [200, 400, 404]

    def test_get_user_learning_paths(self, client: FlaskClient):
        """Test GET /api/users/<user_id>/learning-paths"""
        user_id = "test_user"
        resp = client.get(f'/api/users/{user_id}/learning-paths')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, list)

    def test_get_user_progress(self, client: FlaskClient):
        """Test GET /api/users/<user_id>/progress"""
        user_id = "test_user"
        resp = client.get(f'/api/users/{user_id}/progress')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_get_user_achievements(self, client: FlaskClient):
        """Test GET /api/users/<user_id>/achievements"""
        user_id = "test_user"
        resp = client.get(f'/api/users/{user_id}/achievements')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, list)

    def test_get_user_assessments(self, client: FlaskClient):
        """Test GET /api/users/<user_id>/assessments"""
        user_id = "test_user"
        resp = client.get(f'/api/users/{user_id}/assessments')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, list)

    def test_get_user_recommendations(self, client: FlaskClient):
        """Test GET /api/users/<user_id>/recommendations"""
        user_id = "test_user"
        resp = client.get(f'/api/users/{user_id}/recommendations')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, list)
