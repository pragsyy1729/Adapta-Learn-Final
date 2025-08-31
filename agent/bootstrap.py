
from typing import List, Dict
from . import persistence, focus
from .models import UserSkillProfile
import re
import os

# Try to import GROQ parser, fallback to heuristic if not available
try:
    from .groq_resume_parser import GroqResumeParser
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("GROQ parser not available - using heuristic method")

def estimate_from_resume_enhanced(resume_text: str, skills: List[str], target_role: str = "") -> Dict[str, dict]:
	"""
	Enhanced resume skill extraction using GROQ AI if available, otherwise fallback to heuristic
	"""
	# Try GROQ first if available and API key is set
	if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
		try:
			print("🔍 Using GROQ AI for resume analysis...")
			parser = GroqResumeParser()
			analysis = parser.parse_resume_for_skills(resume_text, skills, target_role)
			
			# Convert GROQ format to our expected format
			result = {}
			for skill in skills:
				if skill in analysis.get('skills_analysis', {}):
					skill_data = analysis['skills_analysis'][skill]
					result[skill] = {
						"level": skill_data.get('proficiency_level', 1.0),
						"confidence": skill_data.get('confidence', 0.1),
						"evidence": skill_data.get('evidence', ''),
						"method": "groq_ai"
					}
				else:
					# Fallback for missing skills
					result[skill] = {
						"level": 1.0,
						"confidence": 0.1,
						"evidence": "Not analyzed by GROQ",
						"method": "groq_fallback"
					}
			
			print(f"✅ GROQ analysis complete - found {len([s for s in result.values() if s['level'] > 1.0])} skills above basic level")
			return result
			
		except Exception as e:
			print(f"⚠️ GROQ analysis failed: {e}")
			print("📝 Falling back to heuristic method...")
	
	# Fallback to heuristic method
	print("📝 Using heuristic resume analysis...")
	result = estimate_from_resume(resume_text, skills)
	for skill in result:
		result[skill]["method"] = "heuristic"
	return result

def estimate_from_resume(resume_text: str, skills: List[str]) -> Dict[str, dict]:
	"""
	Enhanced heuristic for resume skill extraction.
	Looks for skill keywords and context clues to determine proficiency.
	"""
	result = {}
	text = resume_text.lower()
	
	for skill in skills:
		skill_lc = skill.lower()
		# Look for skill mentions
		pattern = r'\b' + re.escape(skill_lc) + r'\b'
		found = re.search(pattern, text)
		
		if found:
			# Extract broader context for better analysis
			context_start = max(0, found.start()-100)
			context_end = min(len(resume_text), found.end()+100)
			context = resume_text[context_start:context_end]
			
			# Look for proficiency indicators
			level = 2.0  # Default
			confidence = 0.6
			
			# Check for experience indicators
			if re.search(r'(\d+)\+?\s*years?.*' + skill_lc, context, re.IGNORECASE):
				years_match = re.search(r'(\d+)\+?\s*years?', context)
				if years_match:
					years = int(years_match.group(1))
					if years >= 5:
						level = 4.0
					elif years >= 3:
						level = 3.5
					elif years >= 2:
						level = 3.0
			
			# Check for proficiency keywords
			proficiency_indicators = {
				r'\bexpert\b|\badvanced\b|\bsenior\b': 4.5,
				r'\bproficient\b|\bexperienced\b|\bstrong\b': 3.5,
				r'\bintermediate\b|\bcompetent\b': 3.0,
				r'\bbasic\b|\bbeginner\b|\bfamiliar\b': 2.0,
				r'\bexposure\b|\baware\b': 1.5
			}
			
			for pattern, skill_level in proficiency_indicators.items():
				if re.search(pattern, context, re.IGNORECASE):
					level = max(level, skill_level)
					break
			
			# Check for project indicators
			project_indicators = [
				r'\bproject\b', r'\bbuilt\b', r'\bdeveloped\b', 
				r'\bcreated\b', r'\bimplemented\b', r'\bdesigned\b'
			]
			project_mentions = sum(1 for pattern in project_indicators 
								 if re.search(pattern, context, re.IGNORECASE))
			
			if project_mentions >= 2:
				level = min(5.0, level + 0.5)
				confidence = min(1.0, confidence + 0.1)
			
			snippet = context.strip()[:200] + "..." if len(context) > 200 else context.strip()
		else:
			level = 1.0
			confidence = 0.4
			snippet = ""
		
		result[skill] = {
			"level": level,
			"confidence": confidence,
			"evidence": snippet
		}
	return result

def bootstrap_profile(user_id: str, role_id: str, resume_text: str) -> dict:
	"""Enhanced bootstrap that integrates with onboarding agent"""
	import traceback
	try:
		jd = persistence.get_jd(role_id)
		# Support both {skills: {...}} and {required: [{skill, level}]}
		if not jd:
			raise ValueError(f"No JD for role {role_id}")
		if 'skills' in jd:
			skills = list(jd['skills'].keys())
		elif 'required' in jd:
			skills = [s['skill'] for s in jd['required']]
		else:
			raise ValueError(f"No skills or required in JD for role {role_id}")
		
		# Use enhanced resume analysis (GROQ + fallback)
		role_name = role_id.replace('_', ' ').title()  # Convert role_id to readable name
		est = estimate_from_resume_enhanced(resume_text, skills, role_name)
		
		profile_dict = {
			"user_id": user_id,
			"role_id": role_id,
			"skills": {k: {"level": v["level"], "confidence": v["confidence"]} for k, v in est.items()}
		}
		persistence.save_user_profile(user_id, profile_dict)
		
		# For focus, convert required to skills if needed
		if 'skills' not in jd and 'required' in jd:
			jd_focus = {"skills": {s['skill']: {"required_level": s['level'], "importance": 1} for s in jd['required']}}
		else:
			jd_focus = dict(jd)
			jd_focus.pop('role_id', None)
		focus_points = focus.compute_focus_points(profile_dict, jd_focus)
		persistence.upsert_focus(user_id, {"focus": focus_points})
		
		# Create audit entry with enhanced information
		audit_entry = {
			"event": "resume_bootstrap",
			"profile": profile_dict,
			"focus": focus_points,
			"provenance": {
				"resume_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
				"jd": jd,
				"evidence": {k: v["evidence"][:100] + "..." if len(v["evidence"]) > 100 else v["evidence"] for k, v in est.items()}
			},
			"skill_analysis_summary": {
				"total_skills_analyzed": len(skills),
				"skills_found": len([k for k, v in est.items() if v["level"] > 1.0]),
				"high_confidence_skills": len([k for k, v in est.items() if v["confidence"] > 0.7]),
				"average_skill_level": sum(v["level"] for v in est.values()) / len(est) if est else 1.0
			}
		}
		
		persistence.append_audit(user_id, audit_entry)
		
		# Try to trigger onboarding analysis if available
		try:
			trigger_onboarding_analysis(user_id, role_id, resume_text, profile_dict)
		except Exception as onboarding_error:
			print(f"Warning: Onboarding analysis failed: {onboarding_error}")
		
		return {"profile": profile_dict, "focus": focus_points}
		
	except Exception as e:
		print("[EXCEPTION in bootstrap_profile]", e)
		traceback.print_exc()
		raise

def trigger_onboarding_analysis(user_id: str, role_id: str, resume_text: str, profile_dict: dict):
	"""
	Trigger enhanced onboarding analysis if the new system is available
	This is called after basic bootstrap to provide additional insights
	"""
	try:
		# Map legacy role_id to department and role name
		role_mapping = {
			"jr_data_eng": ("Data Engineer", "engineering"),
			"python_dev": ("Python Developer", "engineering"),
			"data_scientist": ("Data Scientist", "data_science"),
			"frontend_dev": ("Frontend Developer", "engineering"),
			"backend_dev": ("Backend Developer", "engineering")
		}
		
		if role_id in role_mapping:
			role_name, department = role_mapping[role_id]
			
			# Store the enhanced analysis request for later processing
			persistence.append_audit(user_id, {
				"event": "enhanced_onboarding_requested",
				"role_mapping": {
					"legacy_role_id": role_id,
					"target_role": role_name,
					"department": department
				},
				"resume_summary": {
					"length": len(resume_text),
					"skill_indicators_found": len([k for k, v in profile_dict["skills"].items() if v["level"] > 1.0])
				},
				"timestamp": persistence._now()
			})
			
			print(f"✅ Enhanced onboarding analysis queued for {user_id}")
					
	except Exception as e:
		print(f"Enhanced onboarding analysis failed: {e}")
		# Don't let this failure break the basic bootstrap process
		pass
