import os
import tempfile
import shutil
import uuid
import json
import pytest
from agent.orchestrator import Supervisor
from agent.persistence import load_user_profile, load_audit, load_focus

def test_python_skill_progression_and_idempotency():
    # Setup: use a temp state dir
    state_dir = os.path.join(os.path.dirname(__file__), '../data/state')
    shutil.rmtree(state_dir, ignore_errors=True)
    os.makedirs(state_dir, exist_ok=True)
    supervisor = Supervisor()
    user_id = f"testuser_{uuid.uuid4().hex[:8]}"
    role_id = "jr_data_eng"
    resume_text = "Python, SQL, Git experience."
    # 1. user_created event
    event1 = {
        "type": "user_created",
        "user_id": user_id,
        "role_id": role_id,
        "resume_text": resume_text,
        "idempotency_key": "create-1"
    }
    result1 = supervisor.handle_event(event1)
    assert "profile" in result1
    # 2. Three module_completed events (simulate progression)
    module_events = [
        {"module_id": "python_basics", "score": 0.85, "idempotency_key": "mod1"},
        {"module_id": "python_intermediate", "score": 0.90, "idempotency_key": "mod2"},
        {"module_id": "python_project_1", "score": 0.92, "idempotency_key": "mod3"}
    ]
    for mevt in module_events:
        event = {
            "type": "module_completed",
            "user_id": user_id,
            "skill": "Python",
            "module_id": mevt["module_id"],
            "target_level": 4,
            "completion_type": "passed",
            "score": mevt["score"],
            "has_assessment": True,
            "pass_threshold": 0.7,
            "idempotency_key": mevt["idempotency_key"]
        }
        result = supervisor.handle_event(event)
        assert "profile" in result
    # Assert Python level >= 3.0
    profile = load_user_profile(user_id)
    assert profile["skills"]["Python"]["level"] >= 3.0
    # Assert Python not in focus
    focus = load_focus(user_id)
    focus_skills = [f["skill"] for f in focus["focus"]]
    assert "Python" not in focus_skills
    # 3. Re-send third module_completed with same idempotency_key
    event_dup = {
        "type": "module_completed",
        "user_id": user_id,
        "skill": "Python",
        "module_id": "python_project_1",
        "target_level": 4,
        "completion_type": "passed",
        "score": 0.92,
        "has_assessment": True,
        "pass_threshold": 0.7,
        "idempotency_key": "mod3"
    }
    profile_before = json.dumps(load_user_profile(user_id), sort_keys=True)
    result_dup = supervisor.handle_event(event_dup)
    profile_after = json.dumps(load_user_profile(user_id), sort_keys=True)
    assert result_dup == result  # Should be identical to previous
    assert profile_before == profile_after  # No change
    # 4. Audit log includes event_type, payload, received_at, deltas
    audit = load_audit(user_id)
    found = False
    for entry in audit:
        if entry["event_type"] == "module_completed" and "deltas" in entry["payload"]:
            found = True
            assert "received_at" in entry["payload"]
            assert isinstance(entry["payload"].get("payload"), dict)
            assert isinstance(entry["payload"].get("deltas"), list)
    assert found, "Audit log should include deltas for module_completed."
