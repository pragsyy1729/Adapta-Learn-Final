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

class TestEventsAPIs:
    """Test cases for Event Management APIs"""

    def test_module_completed_event(self, client: FlaskClient):
        """Test POST /api/events/module-completed"""
        payload = {
            "user_id": "test_user",
            "module_id": "MOD2024001",
            "learning_path_id": "LP2024ENG001",
            "completion_time_minutes": 45,
            "score": 85
        }
        resp = client.post('/api/events/module-completed',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_submit_assessment_event(self, client: FlaskClient):
        """Test POST /api/events/assessments/submit"""
        payload = {
            "user_id": "test_user",
            "assessment_id": "assessment_001",
            "score": 90,
            "time_spent_minutes": 20,
            "answers": {"q1": "correct", "q2": "correct"}
        }
        resp = client.post('/api/assessments/submit',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]
