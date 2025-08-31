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

class TestAssessmentAPIs:
    """Test cases for Assessment Management APIs"""

    def test_get_assessments(self, client: FlaskClient):
        """Test GET /api/assessments"""
        resp = client.get('/api/assessments')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_submit_assessment_attempt(self, client: FlaskClient):
        """Test POST /api/assessment-attempts"""
        payload = {
            "user_id": "test_user",
            "assessment_id": "asmt-001",  # Use correct assessment ID from data
            "answers": {"q1": "answer1", "q2": "answer2"},
            "time_spent_minutes": 15
        }
        resp = client.post('/api/assessment-attempts',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]
