from flask import Blueprint, jsonify, request, abort
import os
import sys

# Add the project root to sys.path to import agent module
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import agent.supervisor as supervisor
from agent.orchestrator import Supervisor
from ..services.data_access import _read_json
from backend.app.services.skill_utils import top_focus_areas

profile_bp = Blueprint('profile', __name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
PROFILES_FILE = os.path.join(DATA_DIR, 'profiles.json')
JD_FILE = os.path.join(DATA_DIR, 'jd.json')

@profile_bp.route('/profiles/bootstrap', methods=['POST'])
def bootstrap_profile():
    data = request.get_json(force=True)
    event = {
        "type": "user_created",
        "user_id": data.get("user_id"),
        "role_id": data.get("role_id"),
        "resume_text": data.get("resume_text"),
        "idempotency_key": data.get("idempotency_key")
    }
    result = supervisor.handle_event(event)
    if "error" in result:
        code = result["error"].get("code")
        if code == "MISSING_FIELD":
            return jsonify(result), 400
        elif code == "NOT_FOUND":
            return jsonify(result), 404
        elif code == "DUPLICATE":
            return jsonify(result), 409
        else:
            return jsonify(result), 400
    return jsonify(result)

@profile_bp.route('/users/<user_id>/profile', methods=['GET'])
def get_profile(user_id):
    profiles = _read_json(PROFILES_FILE, {})
    profile = profiles.get(user_id)
    if not profile:
        abort(404, 'User not found')
    return jsonify(profile)

@profile_bp.route('/users/<user_id>/focus', methods=['GET'])
def get_focus(user_id):
    profiles = _read_json(PROFILES_FILE, {})
    profile = profiles.get(user_id)
    if not profile:
        abort(404, 'User not found')
    role_id = profile['role_id']
    jd = _read_json(JD_FILE, {}).get(role_id)
    focus = top_focus_areas(profile, jd)
    return jsonify({'focus': focus})
