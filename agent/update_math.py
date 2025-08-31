
from typing import Optional, Tuple

def clip(x: float, lo: float, hi: float) -> float:
	"""
	Clamp x to the range [lo, hi].
	"""
	return max(lo, min(hi, x))

def compute_alpha(weight: float, completion_type: str, has_assessment: bool, score: Optional[float], pass_threshold: Optional[float]) -> float:
	"""
	Compute alpha for skill update based on event details.
	base = 0.25
	if completion_type=="passed": base += 0.15
	if completion_type=="failed": base -= 0.10
	if has_assessment and score is not None:
		base += 0.40 * (score - pass_threshold)
	alpha = clip(base * weight, 0.05, 0.50)
	"""
	base = 0.25
	if completion_type == "passed":
		base += 0.15
	elif completion_type == "failed":
		base -= 0.10
	if has_assessment and score is not None and pass_threshold is not None:
		base += 0.40 * (score - pass_threshold)
	alpha = clip(base * weight, 0.05, 0.50)
	return alpha

def update_skill(L_old: float, C_old: float, target_level: float, alpha: float, completion_type: str, score: Optional[float], has_assessment: bool) -> Tuple[float, float]:
	"""
	Update skill level and confidence.
	L_new = clip(L_old + alpha * (T - L_old), 1, 5)
	C_new = clip(C_old + 0.5 * alpha * (0.5 + (0.2 if passed else 0) + (0.3*score if score else 0)), 0, 1)
	Returns (L_new, C_new)
	"""
	# Level update
	L_new = clip(L_old + alpha * (target_level - L_old), 1, 5)
	# Confidence update
	passed = completion_type == "passed"
	score_val = score if (has_assessment and score is not None) else 0.0
	conf_incr = 0.5 * alpha * (0.5 + (0.2 if passed else 0) + (0.3 * score_val))
	C_new = clip(C_old + conf_incr, 0, 1)
	return L_new, C_new
