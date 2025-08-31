import unittest
from backend.app.services.math_utils import compute_alpha, update_level, update_confidence

class TestSkillMath(unittest.TestCase):
    def test_compute_alpha_passed(self):
        event = {
            'completion_type': 'passed',
            'has_assessment': True,
            'score': 0.9,
            'pass_threshold': 0.7,
            'weight': 1.0
        }
        alpha = compute_alpha(event)
        self.assertAlmostEqual(alpha, 0.48, places=2)

    def test_compute_alpha_failed(self):
        event = {
            'completion_type': 'failed',
            'has_assessment': True,
            'score': 0.5,
            'pass_threshold': 0.7,
            'weight': 1.0
        }
        alpha = compute_alpha(event)
        self.assertAlmostEqual(alpha, 0.07, places=2)

    def test_update_level(self):
        L_old = 1
        T = 3
        alpha = 0.41
        L_new = update_level(L_old, T, alpha)
        self.assertAlmostEqual(L_new, 1.82, places=2)

    def test_update_confidence(self):
        C_old = 0.3
        alpha = 0.41
        passed = True
        score = 0.9
        C_new = update_confidence(C_old, alpha, passed, score)
        self.assertAlmostEqual(C_new, 0.50, places=2)

if __name__ == "__main__":
    unittest.main()
