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

class TestEnrollmentAPIs:
    """Test cases for Enrollment Management APIs"""

    def test_enroll_user(self, client: FlaskClient):
        """Test POST /api/enroll"""
        payload = {
            "user_id": "user_001",  # Use existing user ID from data
            "learning_path_id": "LP2024DS001",  # Use correct learning path ID from data
            "department": "DS2024001"
        }
        resp = client.post('/api/enroll',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_auto_enroll_from_onboarding(self, client: FlaskClient):
        """Test POST /api/auto-enroll-from-onboarding"""
        payload = {
            "user_id": "test_user",
            "onboarding_analysis": {
                "recommended_paths": ["LP2024ENG001"],
                "department": "ENG2024001"
            }
        }
        resp = client.post('/api/auto-enroll-from-onboarding',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_get_user_enrolled_paths(self, client: FlaskClient):
        """Test GET /api/user/<user_id>/enrolled-paths"""
        user_id = "user_001"  # Use existing user ID from data
        resp = client.get(f'/api/user/{user_id}/enrolled-paths')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)  # API returns dict with user_id, enrolled_paths, total_enrolled
            assert 'enrolled_paths' in data
            assert 'user_id' in data
            assert 'total_enrolled' in data
