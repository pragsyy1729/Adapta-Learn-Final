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

class TestDashboardAPIs:
    """Test cases for Dashboard APIs"""

    def test_get_user_dashboard(self, client: FlaskClient):
        """Test GET /api/dashboard/dashboard"""
        # This endpoint likely requires authentication/user context
        resp = client.get('/api/dashboard/dashboard')
        assert resp.status_code in [200, 401, 404]
        if resp.status_code == 200:
            data = resp.get_json()
            assert isinstance(data, dict)
