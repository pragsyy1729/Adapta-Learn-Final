
import os
import json
from typing import Dict, List

BASE = os.path.dirname(os.path.dirname(__file__))
MODULES_DIR = os.path.join(BASE, 'data', 'modules')

def _load_modules_catalog() -> List[dict]:
	modules = []
	if not os.path.exists(MODULES_DIR):
		return modules
	for fname in os.listdir(MODULES_DIR):
		if fname.endswith('.json'):
			with open(os.path.join(MODULES_DIR, fname), 'r', encoding='utf-8') as f:
				try:
					modules.append(json.load(f))
				except Exception:
					continue
	return modules

def compute_focus_points(profile_dict: dict, jd_dict: dict) -> List[dict]:
	"""
	Returns top-3 focus points: [{skill, gap, suggested_modules: [module_id, ...]}]
	"""
	print("[DEBUG] compute_focus_points: jd_dict type:", type(jd_dict), jd_dict)
	skills = jd_dict.get('skills', {})
	print("[DEBUG] compute_focus_points: skills type:", type(skills), skills)
	user_skills = profile_dict.get('skills', {})
	print(f"[DEBUG] user_skills: {user_skills}")
	focus = []
	for skill, req in skills.items():
		print(f"[DEBUG] skill: {skill}, req type: {type(req)}, req: {req}")
		skill_val = user_skills.get(skill, {})
		print(f"[DEBUG] skill_val for {skill}: {skill_val} (type: {type(skill_val)})")
		current = skill_val.get('level', 1.0) if isinstance(skill_val, dict) else 1.0
		gap = max(0, req.get('required_level', 1) - current)
		if gap > 0:
			focus.append({
				'skill': skill,
				'gap': gap,
				'importance': req.get('importance', 1)
			})
	# Sort by gap desc, then importance desc
	focus.sort(key=lambda x: (-x['gap'], -x['importance']))
	top_focus = focus[:3]

	# Suggest modules for each focus skill
	modules = _load_modules_catalog()
	for f in top_focus:
		skill = f['skill']
		# Find modules that cover this skill
		matching = [m for m in modules if any(
			s.get('skill') == skill for s in m.get('skills_covered', []))]
		# Sort by weight desc (if present)
		matching.sort(key=lambda m: -max([s.get('weight', 1.0) for s in m.get('skills_covered', []) if s.get('skill') == skill], default=1.0))
		f['suggested_modules'] = [m.get('module_id') for m in matching[:2]]
	return top_focus
