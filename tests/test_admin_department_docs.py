
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

def test_get_departments(client: FlaskClient):
    resp = client.get('/api/admin/departments')
    assert resp.status_code == 200
    depts = resp.get_json()
    assert isinstance(depts, list)
    assert any('documentation' in d for d in depts)

def test_add_and_get_department_documentation(client: FlaskClient):
    # Pick a department ID from the fixture data
    dept_id = 'ENG2024001'
    doc_payload = {"name": "Onboarding Guide", "document_content": "Welcome to Engineering!"}  # Use correct field name
    # Add documentation
    resp = client.post(f'/api/admin/departments/{dept_id}/documentation',
                      data=json.dumps(doc_payload),
                      content_type='application/json')
    assert resp.status_code == 200
    assert resp.get_json().get('success') is True
    # Get documentation
    resp = client.get(f'/api/admin/departments/{dept_id}/documentation')
    assert resp.status_code == 200
    docs = resp.get_json()
    assert isinstance(docs, list)
    assert any(doc['name'] == 'Onboarding Guide' and doc['document_content'] == 'Welcome to Engineering!' for doc in docs)

def test_update_department_documentation(client: FlaskClient):
    dept_id = 'ENG2024001'
    doc_payload = {"name": "Onboarding Guide", "document_content": "Updated content!"}  # Use correct field name
    # Update documentation
    resp = client.put(f'/api/admin/departments/{dept_id}/documentation',
                     data=json.dumps(doc_payload),
                     content_type='application/json')
    assert resp.status_code == 200
    # Get documentation and check update
    resp = client.get(f'/api/admin/departments/{dept_id}/documentation')
    docs = resp.get_json()
    assert any(doc['name'] == 'Onboarding Guide' and doc['document_content'] == 'Updated content!' for doc in docs)

def test_add_documentation_missing_fields(client: FlaskClient):
    dept_id = 'ENG2024001'
    # Missing content
    resp = client.post(f'/api/admin/departments/{dept_id}/documentation',
                      data=json.dumps({"name": "Doc Only"}),
                      content_type='application/json')
    assert resp.status_code == 400
    # Missing name
    resp = client.post(f'/api/admin/departments/{dept_id}/documentation',
                      data=json.dumps({"content": "No name"}),
                      content_type='application/json')
    assert resp.status_code == 400

def test_get_documentation_invalid_department(client: FlaskClient):
    resp = client.get('/api/admin/departments/INVALID_ID/documentation')
    assert resp.status_code == 200
    assert resp.get_json() == []
