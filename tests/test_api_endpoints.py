import pytest
from flask import Flask
from flask.testing import FlaskClient

# Import your app factory or app object here
from backend.unified_server import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_health(client: FlaskClient):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json.get('status') == 'ok'

def test_admin_learning_paths(client: FlaskClient):
    resp = client.get('/api/admin/learning-paths')
    assert resp.status_code == 200
    assert isinstance(resp.json, list)

def test_onboarding_departments(client: FlaskClient):
    resp = client.get('/api/onboarding/departments')
    assert resp.status_code == 200
    assert resp.json.get('success') is True
    assert isinstance(resp.json.get('data'), list)

# Add more tests for each endpoint as needed
