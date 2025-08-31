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

class TestOnboardingAPIs:
    """Test cases for Onboarding Management APIs"""

    def test_analyze_user_onboarding(self, client: FlaskClient):
        """Test POST /api/onboarding/analyze"""
        payload = {
            "user_id": "test_user",
            "department": "ENG2024001",
            "role": "Software Engineer"
        }
        resp = client.post('/api/onboarding/analyze',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_get_user_onboarding_status(self, client: FlaskClient):
        """Test GET /api/onboarding/status/<user_id>"""
        user_id = "test_user"
        resp = client.get(f'/api/onboarding/status/{user_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)

    def test_get_onboarding_departments(self, client: FlaskClient):
        """Test GET /api/onboarding/departments"""
        resp = client.get('/api/onboarding/departments')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') is True
        assert isinstance(data.get('data'), list)

    def test_unified_onboarding_analyze(self, client: FlaskClient):
        """Test POST /api/onboarding/analyze (unified server)"""
        payload = {
            "user_id": "test_user",
            "department": "ENG2024001",
            "role": "Software Engineer"
        }
        resp = client.post('/api/onboarding/analyze',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]
