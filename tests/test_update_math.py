
import unittest
from agent import update_math

class TestUpdateMath(unittest.TestCase):
	def test_compute_alpha_base(self):
		# Watched only
		a = update_math.compute_alpha(1.0, "watched", False, None, None)
		self.assertAlmostEqual(a, 0.25)

	def test_compute_alpha_passed(self):
		# Passed, no score
		a = update_math.compute_alpha(1.0, "passed", False, None, None)
		self.assertAlmostEqual(a, 0.4)

	def test_compute_alpha_failed(self):
		# Failed, no score
		a = update_math.compute_alpha(1.0, "failed", False, None, None)
		self.assertAlmostEqual(a, 0.15)

	def test_compute_alpha_passed_with_score(self):
		# Passed, with assessment and score above threshold
		a = update_math.compute_alpha(1.0, "passed", True, 0.9, 0.7)
		# base = 0.25+0.15+0.4*(0.9-0.7)=0.25+0.15+0.08=0.48, clipped to 0.48
		self.assertAlmostEqual(a, 0.48)

	def test_compute_alpha_failed_with_score(self):
		# Failed, with assessment and score below threshold
		a = update_math.compute_alpha(1.0, "failed", True, 0.5, 0.7)
		# base = 0.25-0.10+0.4*(0.5-0.7)=0.25-0.10-0.08=0.07, clipped to 0.07
		self.assertAlmostEqual(a, 0.07)

	def test_update_skill_bounds_and_monotonic(self):
		# Should never leave [1,5] and move toward target if passed
		for L0 in [1.0, 2.5, 4.9]:
			for T in [2.0, 5.0]:
				L1, _ = update_math.update_skill(L0, 0.5, T, 0.3, "passed", 0.8, True)
				self.assertGreaterEqual(L1, 1.0)
				self.assertLessEqual(L1, 5.0)
				# Monotonic toward target
				if T > L0:
					self.assertGreaterEqual(L1, L0)
				else:
					self.assertLessEqual(L1, L0)

	def test_python_module_scenario(self):
		# Start at L=1.0, apply three modules with scores, expect L>=3.0
		L, C = 1.0, 0.5
		modules = [
			{"weight": 0.7, "target_level": 3, "score": 0.85, "completion_type": "passed", "has_assessment": True, "pass_threshold": 0.7},
			{"weight": 0.8, "target_level": 4, "score": 0.90, "completion_type": "passed", "has_assessment": True, "pass_threshold": 0.7},
			{"weight": 0.9, "target_level": 4, "score": 0.92, "completion_type": "passed", "has_assessment": True, "pass_threshold": 0.7},
		]
		for m in modules:
			alpha = update_math.compute_alpha(m["weight"], m["completion_type"], m["has_assessment"], m["score"], m["pass_threshold"])
			L, C = update_math.update_skill(L, C, m["target_level"], alpha, m["completion_type"], m["score"], m["has_assessment"])
		self.assertGreaterEqual(L, 3.0)

if __name__ == "__main__":
	unittest.main()
