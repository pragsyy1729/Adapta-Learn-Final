def clip(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))

def compute_alpha(event: dict) -> float:
    base = 0.25
    if event.get('completion_type') == 'passed':
        base += 0.15
    if event.get('completion_type') == 'failed':
        base -= 0.10
    if event.get('has_assessment') and event.get('score') is not None:
        base += 0.40 * (event['score'] - event.get('pass_threshold', 0))
    weight = event.get('weight', 1.0)
    return clip(base * weight, 0.05, 0.50)

def update_level(L_old: float, T: float, alpha: float) -> float:
    return clip(L_old + alpha * (T - L_old), 1, 5)

def update_confidence(C_old: float, alpha: float, passed: bool, score: float | None) -> float:
    inc = 0.5 * alpha * (0.5 + (0.2 if passed else 0) + (0.3 * score if score else 0))
    return clip(C_old + inc, 0, 1)
