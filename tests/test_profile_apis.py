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

class TestProfileAPIs:
    """Test cases for User Profile APIs"""

    def test_bootstrap_user_profile(self, client: FlaskClient):
        """Test POST /api/profiles/bootstrap"""
        payload = {
            "user_id": "test_user",
            "department": "ENG2024001",
            "role": "Software Engineer"
        }
        resp = client.post('/api/profiles/bootstrap',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_get_user_profile(self, client: FlaskClient):
        """Test GET /api/users/<user_id>/profile"""
        user_id = "test_user"
        resp = client.get(f'/api/users/{user_id}/profile')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_get_user_focus(self, client: FlaskClient):
        """Test GET /api/profile/users/<user_id>/focus"""
        user_id = "test_user"
        resp = client.get(f'/api/users/{user_id}/focus')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)
