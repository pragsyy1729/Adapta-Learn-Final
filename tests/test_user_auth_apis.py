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

class TestUserAuthAPIs:
    """Test cases for User Authentication APIs"""

    def test_user_sign_in(self, client: FlaskClient):
        """Test POST /api/sign-in"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        resp = client.post('/api/sign-in',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 401, 400]

    def test_user_get_started(self, client: FlaskClient):
        """Test POST /api/get-started"""
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "department": "ENG2024001"
        }
        resp = client.post('/api/get-started',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_get_current_user(self, client: FlaskClient):
        """Test GET /api/me"""
        resp = client.get('/api/me')
        assert resp.status_code in [200, 401]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_update_learning_style(self, client: FlaskClient):
        """Test POST /api/learning-style"""
        payload = {
            "user_id": "user_001",  # Use existing user ID from data
            "learning_style": "visual",
            "preferences": ["videos", "diagrams"]
        }
        resp = client.post('/api/learning-style',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_user_sign_out(self, client: FlaskClient):
        """Test POST /api/sign-out"""
        payload = {"user_id": "test_user"}
        resp = client.post('/api/sign-out',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 400]
