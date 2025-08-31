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

class TestSessionAPIs:
    """Test cases for Session Management APIs"""

    def test_start_session(self, client: FlaskClient):
        """Test POST /api/sessions/start"""
        payload = {
            "user_id": "test_user",
            "module_id": "MOD2024001",
            "learning_path_id": "LP2024ENG001"
        }
        resp = client.post('/api/sessions/start',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_end_session(self, client: FlaskClient):
        """Test POST /api/sessions/end"""
        # First start a session
        start_payload = {"user_id": "test_user"}
        start_resp = client.post('/api/sessions/start',
                                data=json.dumps(start_payload),
                                content_type='application/json')
        assert start_resp.status_code == 200
        session_data = start_resp.get_json()
        session_id = session_data['session_id']
        
        # Now end the session
        payload = {
            "session_id": session_id,
            "user_id": "test_user"
        }
        resp = client.post('/api/sessions/end',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 400]

    def test_update_session_activity(self, client: FlaskClient):
        """Test POST /api/sessions/update-activity"""
        payload = {
            "session_id": "session_001",
            "activity_type": "reading",
            "content_id": "content_001",
            "time_spent_minutes": 10
        }
        resp = client.post('/api/sessions/update-activity',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 400]

    def test_end_session_activity(self, client: FlaskClient):
        """Test POST /api/sessions/end-activity"""
        payload = {
            "session_id": "session_001",
            "activity_id": "activity_001"
        }
        resp = client.post('/api/sessions/end-activity',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 400]

    def test_log_session_activity(self, client: FlaskClient):
        """Test POST /api/sessions/activity"""
        # First start a session
        start_payload = {"user_id": "test_user"}
        start_resp = client.post('/api/sessions/start',
                                data=json.dumps(start_payload),
                                content_type='application/json')
        assert start_resp.status_code == 200
        session_data = start_resp.get_json()
        session_id = session_data['session_id']
        
        # Now log activity
        payload = {
            "user_id": "test_user",
            "session_id": session_id,
            "activity_type": "quiz",
            "content_id": "quiz_001",
            "start_time": "2024-01-01T10:00:00Z",
            "end_time": "2024-01-01T10:15:00Z"
        }
        resp = client.post('/api/sessions/activity',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 201, 400]

    def test_get_user_session_stats(self, client: FlaskClient):
        """Test GET /api/sessions/stats/<user_id>"""
        user_id = "test_user"
        resp = client.get(f'/api/sessions/stats/{user_id}')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)
