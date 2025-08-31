def compute_gaps(profile: dict, jd: dict) -> list[dict]:
    result = []
    for skill, req in jd.get('skills', {}).items():
        current = profile.get('skills', {}).get(skill, {'level': 1})['level']
        gap = max(0, req['required_level'] - current)
        result.append({
            'skill': skill,
            'gap': gap,
            'importance': req.get('importance', 1)
        })
    result.sort(key=lambda x: (-x['gap'], -x['importance']))
    return result

def top_focus_areas(profile: dict, jd: dict, top_n: int = 3) -> list[str]:
    gaps = compute_gaps(profile, jd)
    return [g['skill'] for g in gaps[:top_n] if g['gap'] > 0]
