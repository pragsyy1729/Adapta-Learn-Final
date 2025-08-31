
import os
import json
from typing import Optional, Any

BASE = os.path.dirname(os.path.dirname(__file__))
STATE_DIR = os.path.join(BASE, 'data', 'state')
JD_DIR = os.path.join(BASE, 'data', 'jd')
MODULES_DIR = os.path.join(BASE, 'data', 'modules')
FOCUS_SUFFIX = '_focus.json'

def _ensure_dir(path: str):
	os.makedirs(os.path.dirname(path), exist_ok=True)

def load_user_profile(user_id: str) -> Optional[dict]:
	path = os.path.join(STATE_DIR, f'{user_id}_profile.json')
	if not os.path.exists(path):
		return None
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)

def save_user_profile(user_id: str, profile_dict: dict) -> None:
	path = os.path.join(STATE_DIR, f'{user_id}_profile.json')
	_ensure_dir(path)
	with open(path, 'w', encoding='utf-8') as f:
		json.dump(profile_dict, f, indent=2, ensure_ascii=False)


from datetime import datetime, timezone

def append_audit(user_id: str, entry: dict) -> None:
	"""
	Appends an audit entry with ts, event_type, and payload.
	"""
	print(f"[DEBUG] append_audit entry type: {type(entry)}, entry: {entry}")
	path = os.path.join(STATE_DIR, f'{user_id}_audit.jsonl')
	_ensure_dir(path)
	ts = entry.get("ts") or datetime.now(timezone.utc).isoformat()
	event_type = entry.get("event_type")
	if not event_type:
		event = entry.get("event")
		if isinstance(event, dict):
			event_type = event.get("type")
		else:
			event_type = None
	if not event_type:
		event_type = "unknown"
	payload = entry.get("payload") or entry.get("event") or entry
	audit_entry = {"ts": ts, "event_type": event_type, "payload": payload}
	with open(path, 'a', encoding='utf-8') as f:
		f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')

def load_audit(user_id: str) -> list:
	"""
	Loads the audit log for a user as a list of events.
	"""
	path = os.path.join(STATE_DIR, f'{user_id}_audit.jsonl')
	if not os.path.exists(path):
		return []
	with open(path, 'r', encoding='utf-8') as f:
		return [json.loads(line) for line in f if line.strip()]

def get_jd(role_id: str) -> Optional[dict]:
	path = os.path.join(JD_DIR, f'{role_id}.json')
	if not os.path.exists(path):
		return None
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)

def get_module(module_id: str) -> Optional[dict]:
	path = os.path.join(MODULES_DIR, f'{module_id}.json')
	if not os.path.exists(path):
		return None
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)

def upsert_focus(user_id: str, focus_dict: dict) -> None:
	path = os.path.join(STATE_DIR, f'{user_id}{FOCUS_SUFFIX}')
	_ensure_dir(path)
	with open(path, 'w', encoding='utf-8') as f:
		json.dump(focus_dict, f, indent=2, ensure_ascii=False)

def load_focus(user_id: str) -> Optional[dict]:
	path = os.path.join(STATE_DIR, f'{user_id}{FOCUS_SUFFIX}')
	if not os.path.exists(path):
		return None
	with open(path, 'r', encoding='utf-8') as f:
		return json.load(f)
