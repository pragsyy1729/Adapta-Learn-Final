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

class TestRecommendationAPIs:
    """Test cases for Recommendation APIs"""

    def test_get_recommendations(self, client: FlaskClient):
        """Test GET /api/recommendations"""
        resp = client.get('/api/recommendations')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_dismiss_recommendation(self, client: FlaskClient):
        """Test POST /api/recommendations/<rec_id>/dismiss"""
        rec_id = "rec_001"
        payload = {"user_id": "test_user", "reason": "not_interested"}
        resp = client.post(f'/api/recommendations/{rec_id}/dismiss',
                          data=json.dumps(payload),
                          content_type='application/json')
        assert resp.status_code in [200, 404]
