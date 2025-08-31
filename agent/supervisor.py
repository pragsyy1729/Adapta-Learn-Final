
import os
import json
from . import bootstrap, persistence, update_math, focus

IDEMP_SUFFIX = '_idempotency.json'
BASE = os.path.dirname(os.path.dirname(__file__))
STATE_DIR = os.path.join(BASE, 'data', 'state')

def _idempotency_path(user_id):
	return os.path.join(STATE_DIR, f'{user_id}{IDEMP_SUFFIX}')

def _load_idempotency(user_id):
	path = _idempotency_path(user_id)
	if not os.path.exists(path):
		return set()
	with open(path, 'r', encoding='utf-8') as f:
		return set(json.load(f))

def _save_idempotency(user_id, idemp_set):
	path = _idempotency_path(user_id)
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, 'w', encoding='utf-8') as f:
		json.dump(list(idemp_set), f)

def handle_bootstrap(user_id: str, role_id: str, resume_text: str) -> dict:
	return bootstrap.bootstrap_profile(user_id, role_id, resume_text)

def handle_module_completed(event_dict: dict) -> dict:
	user_id = event_dict['user_id']
	idempotency_key = event_dict.get('idempotency_key')
	if idempotency_key:
		idemp_set = _load_idempotency(user_id)
		if idempotency_key in idemp_set:
			# Duplicate event, ignore
			profile = persistence.load_user_profile(user_id)
			focus_points = persistence.load_focus(user_id)
			return {"profile": profile, "focus": focus_points}
		idemp_set.add(idempotency_key)
		_save_idempotency(user_id, idemp_set)

	profile = persistence.load_user_profile(user_id)
	if not profile:
		raise ValueError(f"No profile for user {user_id}")
	role_id = profile['role_id']
	jd = persistence.get_jd(role_id)
	module_id = event_dict['module_id']
	module = persistence.get_module(module_id)
	if not module:
		raise ValueError(f"No module {module_id}")

	deltas = {}
	alphas = {}
	for skill_item in module.get('skills_covered', []):
		skill = skill_item['skill']
		target_level = skill_item.get('target_level', 1.0)
		weight = skill_item.get('weight', 1.0)
		# Compose event for this skill
		alpha = update_math.compute_alpha(
			weight=weight,
			completion_type=event_dict.get('completion_type'),
			has_assessment=event_dict.get('has_assessment', False),
			score=event_dict.get('score'),
			pass_threshold=event_dict.get('pass_threshold')
		)
		L_old = profile['skills'].get(skill, {}).get('level', 1.0)
		C_old = profile['skills'].get(skill, {}).get('confidence', 0.4)
		L_new, C_new = update_math.update_skill(
			L_old, C_old, target_level, alpha,
			event_dict.get('completion_type'),
			event_dict.get('score'),
			event_dict.get('has_assessment', False)
		)
		# Save delta and alpha
		deltas[skill] = {"level": L_new, "confidence": C_new, "prev_level": L_old, "prev_confidence": C_old}
		alphas[skill] = alpha
		# Update profile in-memory
		if 'skills' not in profile:
			profile['skills'] = {}
		profile['skills'][skill] = {"level": round(L_new, 2), "confidence": round(C_new, 2)}

	persistence.save_user_profile(user_id, profile)
	focus_points = focus.compute_focus_points(profile, jd)
	persistence.upsert_focus(user_id, {"focus": focus_points})
	persistence.append_audit(user_id, {
		"event": "module_completed",
		"event_dict": event_dict,
		"module_id": module_id,
		"deltas_per_skill": deltas,
		"alpha_per_skill": alphas
	})
	return {"profile": profile, "focus": focus_points}
