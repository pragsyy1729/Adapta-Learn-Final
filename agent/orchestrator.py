

from . import bootstrap, supervisor, persistence
from .models import EVENT_USER_CREATED, EVENT_ASSESSMENT_SUBMITTED, EVENT_MODULE_COMPLETED
from datetime import datetime

class Supervisor:
    def handle_event(self, event: dict) -> dict:
        """Dispatches event to handlers, manages idempotency & audit. Returns {profile, focus} or {ok:true} or {error:{...}}."""
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        import copy
        event_type = event.get("type")
        user_id = event.get("user_id")
        idempotency_key = event.get("idempotency_key")
        payload = dict(event)
        # Validation: required fields per event type
        required_fields = {
            EVENT_USER_CREATED: ["user_id", "role_id", "resume_text"],
            EVENT_MODULE_COMPLETED: ["user_id", "skill", "target_level", "completion_type"],
            EVENT_ASSESSMENT_SUBMITTED: ["user_id", "assessment_id", "score"],
        }
        missing = []
        if event_type in required_fields:
            for field in required_fields[event_type]:
                if event.get(field) is None:
                    missing.append(field)
        if missing:
            error = {
                "error": {
                    "code": "MISSING_FIELD",
                    "message": f"Missing required fields: {', '.join(missing)}",
                    "details": {"missing": missing}
                }
            }
            # Audit even on error
            audit_payload = dict(payload)
            audit_payload["received_at"] = now_iso
            audit_payload["idempotency_key"] = idempotency_key
            persistence.append_audit(user_id, {
                "event_type": event_type,
                "payload": audit_payload
            })
            return error
        # Audit every event
        if event_type == EVENT_MODULE_COMPLETED:
            event_fields = copy.deepcopy(event)
            for k in ["deltas", "received_at", "idempotency_key"]:
                if k in event_fields:
                    event_fields.pop(k)
            deltas = None
            if "deltas" in payload and isinstance(payload["deltas"], list):
                deltas = payload["deltas"]
            if deltas is None:
                deltas = []
            audit_payload = {
                "payload": event_fields,
                "deltas": deltas,
                "received_at": now_iso,
                "idempotency_key": idempotency_key
            }
            persistence.append_audit(user_id, {
                "event_type": event_type,
                "payload": audit_payload
            })
        else:
            audit_payload = dict(payload)
            audit_payload = {
                "payload": audit_payload,
                "received_at": now_iso,
                "idempotency_key": idempotency_key
            }
            persistence.append_audit(user_id, {
                "event_type": event_type,
                "payload": audit_payload
            })

        # Idempotency enforcement for write events (not for read-only events)
        import os, json, hashlib
        idempotency_events = {EVENT_USER_CREATED, EVENT_MODULE_COMPLETED, EVENT_ASSESSMENT_SUBMITTED}
        idemp_state = None
        state_file = None
        payload_hash = None
        if idempotency_key and event_type in idempotency_events:
            state_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'state')
            os.makedirs(state_dir, exist_ok=True)
            state_file = os.path.join(state_dir, f"{user_id}_idempotency.json")
            # Load state
            if os.path.exists(state_file):
                with open(state_file, 'r', encoding='utf-8') as f:
                    idemp_state = json.load(f)
            else:
                idemp_state = {}
            # Hash the payload (excluding idempotency_key)
            payload_for_hash = dict(payload)
            payload_for_hash.pop('idempotency_key', None)
            payload_bytes = json.dumps(payload_for_hash, sort_keys=True).encode('utf-8')
            payload_hash = hashlib.sha256(payload_bytes).hexdigest()
            entry = idemp_state.get(idempotency_key)
            if entry and entry.get('payload_hash') == payload_hash:
                # Always append audit for idempotent replay
                cached_result = entry['result']
                if event_type == EVENT_MODULE_COMPLETED:
                    # Try to find deltas from previous audit entry for this idempotency_key
                    from agent.persistence import load_audit
                    deltas = None
                    try:
                        audit_log = load_audit(user_id)
                        for prev_audit_entry in audit_log:
                            if prev_audit_entry.get("event_type") == event_type and prev_audit_entry.get("payload", {}).get("idempotency_key") == idempotency_key:
                                # Check both locations for deltas
                                deltas = None
                                if "deltas" in prev_audit_entry:
                                    deltas = prev_audit_entry["deltas"]
                                elif "payload" in prev_audit_entry and isinstance(prev_audit_entry["payload"], dict):
                                    deltas = prev_audit_entry["payload"].get("deltas")
                                if deltas is not None:
                                    break
                    except Exception:
                        deltas = None
                    event_fields = copy.deepcopy(event)
                    for k in ["deltas", "received_at", "idempotency_key"]:
                        if k in event_fields:
                            event_fields.pop(k)
                    audit_payload = {
                        "payload": event_fields,
                        "deltas": deltas if deltas is not None else [],
                        "received_at": now_iso,
                        "idempotency_key": idempotency_key
                    }
                    audit_entry = {
                        "event_type": event_type,
                        "payload": audit_payload
                    }
                    persistence.append_audit(user_id, audit_entry)
                return cached_result

        # --- Event Routing ---
        try:
            from . import bootstrap, update_math, focus
            result = None
            if event_type == EVENT_USER_CREATED:
                # Expect user_id, role_id, resume_text
                try:
                    out = bootstrap.bootstrap_profile(user_id, event["role_id"], event["resume_text"])
                except Exception as e:
                    return {"error": {"code": "NOT_FOUND", "message": str(e), "details": {"event": event}}}
                persistence.save_user_profile(user_id, out["profile"])
                persistence.upsert_focus(user_id, {"focus": out["focus"]})
                result = out

            elif event_type == EVENT_MODULE_COMPLETED:
                # Expect user_id, skill, target_level, completion_type, optional score
                profile = persistence.load_user_profile(user_id)
                module = persistence.get_module(event.get("module_id"))
                jd = persistence.get_jd(profile["role_id"]) if profile else None
                print("[DEBUG] JD loaded for role_id", profile["role_id"] if profile else None, ":", jd)
                if not profile:
                    return {"error": {"code": "NOT_FOUND", "message": "Profile not found", "details": {"user_id": user_id}}}
                if not module:
                    return {"error": {"code": "NOT_FOUND", "message": "Module not found", "details": {"module_id": event.get("module_id")}}}
                if not jd:
                    return {"error": {"code": "NOT_FOUND", "message": "JD not found", "details": {"role_id": profile.get("role_id")}}}
                # For each skills_covered in module
                audit_deltas = []
                for skill_meta in module.get("skills_covered", []):
                    print("[DEBUG] skill_meta type:", type(skill_meta), skill_meta)
                    skill = skill_meta["skill"]
                    weight = skill_meta.get("weight", 1.0)
                    target_level = skill_meta.get("target_level", event.get("target_level", 1.0))
                    has_assessment = skill_meta.get("has_assessment", event.get("has_assessment", False))
                    pass_threshold = skill_meta.get("pass_threshold", event.get("pass_threshold"))
                    completion_type = event.get("completion_type")
                    score = event.get("score")
                    # Compute alpha
                    alpha = update_math.compute_alpha(weight, completion_type, has_assessment, score, pass_threshold)
                    # Update skill
                    old = profile["skills"].get(skill, {"level": 1.0, "confidence": 0.3})
                    print("[DEBUG] old skill dict type:", type(old), old)
                    print("[DEBUG] event type:", type(event), event)
                    L_old, C_old = old["level"], old["confidence"]
                    L_new, C_new = update_math.update_skill(L_old, C_old, target_level, alpha, completion_type, score, has_assessment)
                    delta_level = L_new - L_old
                    profile["skills"][skill] = {"level": round(L_new, 2), "confidence": round(C_new, 2)}
                    audit_deltas.append({
                        "skill": skill,
                        "delta_level": delta_level,
                        "alpha": alpha,
                        "target_level": target_level
                    })
                # Save profile and focus
                persistence.save_user_profile(user_id, profile)
                print(f"[DEBUG] About to call compute_focus_points. profile type: {type(profile)}, profile: {profile}")
                print(f"[DEBUG] About to call compute_focus_points. jd type: {type(jd)}, jd: {jd}")
                focus_points = focus.compute_focus_points(profile, jd)
                persistence.upsert_focus(user_id, {"focus": focus_points})
                # Audit per-skill delta (use correct nested structure)
                event_fields = copy.deepcopy(event)
                for k in ["deltas", "received_at", "idempotency_key"]:
                    if k in event_fields:
                        event_fields.pop(k)
                audit_payload = {
                    "payload": event_fields,
                    "deltas": audit_deltas,
                    "received_at": now_iso,
                    "idempotency_key": idempotency_key
                }
                persistence.append_audit(user_id, {
                    "event_type": event_type,
                    "payload": audit_payload
                })
                result = {"profile": profile, "focus": focus_points}

            elif event_type == EVENT_ASSESSMENT_SUBMITTED:
                # For now, just audit and return ok
                # TODO: Map assessments to skill updates
                result = {"ok": True, "todo": "Map assessment to skill updates"}

            if idempotency_key and event_type in idempotency_events and state_file and payload_hash is not None:
                # Store result in idempotency state
                idemp_state[idempotency_key] = {
                    'payload_hash': payload_hash,
                    'result': result
                }
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(idemp_state, f, indent=2)
            return result if result is not None else {"ok": True}
        except Exception as e:
            import traceback
            with open("traceback.log", "a") as f:
                f.write("\n[Exception in handle_event at {}]\n".format(datetime.now(timezone.utc).isoformat()))
                traceback.print_exc(file=f)
            # Standardized error for any failure
            return {"error": {"code": "NOT_FOUND", "message": str(e), "details": {"event": event}}}
        # Validation: required fields per event type
        required_fields = {
            EVENT_USER_CREATED: ["user_id", "role_id", "resume_text"],
            EVENT_MODULE_COMPLETED: ["user_id", "skill", "target_level", "completion_type"],
            EVENT_ASSESSMENT_SUBMITTED: ["user_id", "assessment_id", "score"],
        }
        missing = []
        if event_type in required_fields:
            for field in required_fields[event_type]:
                if event.get(field) is None:
                    missing.append(field)
        if missing:
            error = {
                "error": {
                    "code": "MISSING_FIELD",
                    "message": f"Missing required fields: {', '.join(missing)}",
                    "details": {"missing": missing}
                }
            }
            # Audit even on error
            audit_payload = dict(payload)
            audit_payload["received_at"] = now_iso
            audit_payload["idempotency_key"] = idempotency_key
            persistence.append_audit(user_id, {
                "event_type": event_type,
                "payload": audit_payload
            })
            return error
        # Audit every event
        if event_type == EVENT_MODULE_COMPLETED:
            event_fields = copy.deepcopy(event)
            for k in ["deltas", "received_at", "idempotency_key"]:
                if k in event_fields:
                    event_fields.pop(k)
            deltas = None
            if "deltas" in payload and isinstance(payload["deltas"], list):
                deltas = payload["deltas"]
            if deltas is None:
                deltas = []
            audit_payload = {
                "payload": event_fields,
                "deltas": deltas,
                "received_at": now_iso,
                "idempotency_key": idempotency_key
            }
            persistence.append_audit(user_id, {
                "event_type": event_type,
                "payload": audit_payload
            })
        else:
            audit_payload = dict(payload)
            audit_payload = {
                "payload": audit_payload,
                "received_at": now_iso,
                "idempotency_key": idempotency_key
            }
            persistence.append_audit(user_id, {
                "event_type": event_type,
                "payload": audit_payload
            })

        # Idempotency enforcement for write events (not for read-only events)
        import os, json, hashlib
        idempotency_events = {EVENT_USER_CREATED, EVENT_MODULE_COMPLETED, EVENT_ASSESSMENT_SUBMITTED}
        idemp_state = None
        state_file = None
        payload_hash = None
        if idempotency_key and event_type in idempotency_events:
            state_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'state')
            os.makedirs(state_dir, exist_ok=True)
            state_file = os.path.join(state_dir, f"{user_id}_idempotency.json")
            # Load state
            if os.path.exists(state_file):
                with open(state_file, 'r', encoding='utf-8') as f:
                    idemp_state = json.load(f)
            else:
                idemp_state = {}
            # Hash the payload (excluding idempotency_key)
            payload_for_hash = dict(payload)
            payload_for_hash.pop('idempotency_key', None)
            payload_bytes = json.dumps(payload_for_hash, sort_keys=True).encode('utf-8')
            payload_hash = hashlib.sha256(payload_bytes).hexdigest()
            entry = idemp_state.get(idempotency_key)
            if entry and entry.get('payload_hash') == payload_hash:
                # Always append audit for idempotent replay
                cached_result = entry['result']
                if event_type == EVENT_MODULE_COMPLETED:
                    # Try to find deltas from previous audit entry for this idempotency_key
                    from agent.persistence import load_audit
                    deltas = None
                    try:
                        audit_log = load_audit(user_id)
                        for prev_audit_entry in audit_log:
                            if prev_audit_entry.get("event_type") == event_type and prev_audit_entry.get("payload", {}).get("idempotency_key") == idempotency_key:
                                # Check both locations for deltas
                                deltas = None
                                if "deltas" in prev_audit_entry:
                                    deltas = prev_audit_entry["deltas"]
                                elif "payload" in prev_audit_entry and isinstance(prev_audit_entry["payload"], dict):
                                    deltas = prev_audit_entry["payload"].get("deltas")
                                if deltas is not None:
                                    break
                    except Exception:
                        deltas = None
                    event_fields = copy.deepcopy(event)
                    for k in ["deltas", "received_at", "idempotency_key"]:
                        if k in event_fields:
                            event_fields.pop(k)
                    audit_payload = {
                        "payload": event_fields,
                        "deltas": deltas if deltas is not None else [],
                        "received_at": now_iso,
                        "idempotency_key": idempotency_key
                    }
                    audit_entry = {
                        "event_type": event_type,
                        "payload": audit_payload
                    }
                    persistence.append_audit(user_id, audit_entry)
                return cached_result

        # --- Event Routing ---
        try:
            from . import bootstrap, update_math, focus
            result = None
            if event_type == EVENT_USER_CREATED:
                # Expect user_id, role_id, resume_text
                try:
                    out = bootstrap.bootstrap_profile(user_id, event["role_id"], event["resume_text"])
                except Exception as e:
                    return {"error": {"code": "NOT_FOUND", "message": str(e), "details": {"event": event}}}
                persistence.save_user_profile(user_id, out["profile"])
                persistence.upsert_focus(user_id, {"focus": out["focus"]})
                result = out

            elif event_type == EVENT_MODULE_COMPLETED:
                # Expect user_id, skill, target_level, completion_type, optional score
                profile = persistence.load_user_profile(user_id)
                module = persistence.get_module(event.get("module_id"))
                jd = persistence.get_jd(profile["role_id"]) if profile else None
                print("[DEBUG] JD loaded for role_id", profile["role_id"] if profile else None, ":", jd)
                if not profile:
                    return {"error": {"code": "NOT_FOUND", "message": "Profile not found", "details": {"user_id": user_id}}}
                if not module:
                    return {"error": {"code": "NOT_FOUND", "message": "Module not found", "details": {"module_id": event.get("module_id")}}}
                if not jd:
                    return {"error": {"code": "NOT_FOUND", "message": "JD not found", "details": {"role_id": profile.get("role_id")}}}
                # For each skills_covered in module
                audit_deltas = []
                for skill_meta in module.get("skills_covered", []):
                    print("[DEBUG] skill_meta type:", type(skill_meta), skill_meta)
                    skill = skill_meta["skill"]
                    weight = skill_meta.get("weight", 1.0)
                    target_level = skill_meta.get("target_level", event.get("target_level", 1.0))
                    has_assessment = skill_meta.get("has_assessment", event.get("has_assessment", False))
                    pass_threshold = skill_meta.get("pass_threshold", event.get("pass_threshold"))
                    completion_type = event.get("completion_type")
                    score = event.get("score")
                    # Compute alpha
                    alpha = update_math.compute_alpha(weight, completion_type, has_assessment, score, pass_threshold)
                    # Update skill
                    old = profile["skills"].get(skill, {"level": 1.0, "confidence": 0.3})
                    print("[DEBUG] old skill dict type:", type(old), old)
                    print("[DEBUG] event type:", type(event), event)
                    L_old, C_old = old["level"], old["confidence"]
                    L_new, C_new = update_math.update_skill(L_old, C_old, target_level, alpha, completion_type, score, has_assessment)
                    delta_level = L_new - L_old
                    profile["skills"][skill] = {"level": round(L_new, 2), "confidence": round(C_new, 2)}
                    audit_deltas.append({
                        "skill": skill,
                        "delta_level": delta_level,
                        "alpha": alpha,
                        "target_level": target_level
                    })
                # Save profile and focus
                persistence.save_user_profile(user_id, profile)
                print(f"[DEBUG] About to call compute_focus_points. profile type: {type(profile)}, profile: {profile}")
                print(f"[DEBUG] About to call compute_focus_points. jd type: {type(jd)}, jd: {jd}")
                focus_points = focus.compute_focus_points(profile, jd)
                persistence.upsert_focus(user_id, {"focus": focus_points})
                # Audit per-skill delta (use correct nested structure)
                event_fields = copy.deepcopy(event)
                for k in ["deltas", "received_at", "idempotency_key"]:
                    if k in event_fields:
                        event_fields.pop(k)
                audit_payload = {
                    "payload": event_fields,
                    "deltas": audit_deltas,
                    "received_at": now_iso,
                    "idempotency_key": idempotency_key
                }
                persistence.append_audit(user_id, {
                    "event_type": event_type,
                    "payload": audit_payload
                })
                result = {"profile": profile, "focus": focus_points}

            elif event_type == EVENT_ASSESSMENT_SUBMITTED:
                # For now, just audit and return ok
                # TODO: Map assessments to skill updates
                result = {"ok": True, "todo": "Map assessment to skill updates"}

            if idempotency_key and event_type in idempotency_events and state_file and payload_hash is not None:
                # Store result in idempotency state
                idemp_state[idempotency_key] = {
                    'payload_hash': payload_hash,
                    'result': result
                }
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(idemp_state, f, indent=2)
            return result if result is not None else {"ok": True}
        except Exception as e:
            import traceback
            with open("traceback.log", "a") as f:
                f.write("\n[Exception in handle_event at {}]\n".format(datetime.now(timezone.utc).isoformat()))
                traceback.print_exc(file=f)
            # Standardized error for any failure
            return {"error": {"code": "NOT_FOUND", "message": str(e), "details": {"event": event}}}
