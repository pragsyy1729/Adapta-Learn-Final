"""
Advanced Resume Analysis System
Extracts skills and determines proficiency levels from PDF resumes
Now with GROQ AI integration for enhanced analysis
"""

import re
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import PyPDF2
import docx2txt
from pathlib import Path

# Try to import GROQ parser
try:
    from .groq_resume_parser import GroqResumeParser
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Try to import dynamic role manager
try:
    from .dynamic_role_manager import DynamicRoleManager
    DYNAMIC_ROLES_AVAILABLE = True
except ImportError:
    DYNAMIC_ROLES_AVAILABLE = False

@dataclass
class SkillMatch:
    skill: str
    proficiency_level: float  # 1.0 to 5.0
    confidence: float  # 0.0 to 1.0
    evidence: List[str]  # Phrases/sentences that indicate this skill
    years_experience: Optional[int] = None

class ResumeAnalyzer:
    def __init__(self):
        # Load skill patterns and indicators
        self.skill_patterns = self._load_skill_patterns()
        self.proficiency_indicators = self._load_proficiency_indicators()
        
    def _load_skill_patterns(self) -> Dict[str, List[str]]:
        """Load skill patterns for detection"""
        return {
            # Programming Languages
            "Python": [
                r"\bpython\b", r"\bdjango\b", r"\bflask\b", r"\bfastapi\b", 
                r"\bnumpy\b", r"\bpandas\b", r"\bscikit-learn\b"
            ],
            "JavaScript": [
                r"\bjavascript\b", r"\bjs\b", r"\bnode\.?js\b", r"\breact\b", 
                r"\bvue\b", r"\bangular\b", r"\btypescript\b"
            ],
            "Java": [r"\bjava\b", r"\bspring\b", r"\bmaven\b", r"\bhibernate\b"],
            "C++": [r"\bc\+\+\b", r"\bcpp\b"],
            "C#": [r"\bc#\b", r"\bc sharp\b", r"\b\.net\b"],
            "SQL": [
                r"\bsql\b", r"\bmysql\b", r"\bpostgresql\b", r"\boracle\b", 
                r"\bdatabase\b", r"\bdata modeling\b"
            ],
            
            # Web Technologies
            "React": [r"\breact\b", r"\breact\.js\b", r"\bjsx\b"],
            "Angular": [r"\bangular\b", r"\btypescript\b"],
            "Vue": [r"\bvue\b", r"\bvue\.js\b"],
            "HTML": [r"\bhtml\b", r"\bhtml5\b"],
            "CSS": [r"\bcss\b", r"\bcss3\b", r"\bsass\b", r"\bless\b"],
            
            # Data Science & ML
            "Machine Learning": [
                r"\bmachine learning\b", r"\bml\b", r"\bdeep learning\b",
                r"\bneural networks\b", r"\btensorflow\b", r"\bpytorch\b"
            ],
            "Data Analysis": [
                r"\bdata analysis\b", r"\bdata analytics\b", r"\bstatistics\b",
                r"\btableau\b", r"\bpower bi\b", r"\br programming\b"
            ],
            "Data Science": [
                r"\bdata science\b", r"\bdata scientist\b", r"\bkaggle\b"
            ],
            
            # Cloud & DevOps
            "AWS": [r"\baws\b", r"\bamazon web services\b", r"\bec2\b", r"\bs3\b"],
            "Docker": [r"\bdocker\b", r"\bcontainer\b", r"\bkubernetes\b"],
            "Git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b", r"\bversion control\b"],
            
            # Soft Skills
            "Leadership": [
                r"\bleadership\b", r"\bteam lead\b", r"\bmanagement\b",
                r"\bmentor\b", r"\bsupervis\w+\b"
            ],
            "Communication": [
                r"\bcommunication\b", r"\bpresentation\b", r"\bpublic speaking\b"
            ],
            "Project Management": [
                r"\bproject management\b", r"\bagile\b", r"\bscrum\b", r"\bjira\b"
            ]
        }
    
    def _load_proficiency_indicators(self) -> Dict[str, Dict[str, float]]:
        """Load patterns that indicate proficiency levels"""
        return {
            "expert": {
                "patterns": [
                    r"\bexpert\b", r"\badvanced\b", r"\bsenior\b", r"\blead\b",
                    r"\barchitect\b", r"\bspecialist\b", r"\bmastery\b"
                ],
                "weight": 5.0
            },
            "advanced": {
                "patterns": [
                    r"\badvanced\b", r"\bproficient\b", r"\bexperienced\b",
                    r"\bstrong\b", r"\bsolid\b"
                ],
                "weight": 4.0
            },
            "intermediate": {
                "patterns": [
                    r"\bintermediate\b", r"\bcompetent\b", r"\bworking knowledge\b",
                    r"\bfamiliar\b", r"\bgood understanding\b"
                ],
                "weight": 3.0
            },
            "beginner": {
                "patterns": [
                    r"\bbeginner\b", r"\bbasic\b", r"\bintroductory\b",
                    r"\blearning\b", r"\bstudying\b"
                ],
                "weight": 2.0
            },
            "exposure": {
                "patterns": [
                    r"\bexposure\b", r"\bfamiliar\b", r"\baware\b",
                    r"\bknowledge of\b"
                ],
                "weight": 1.5
            }
        }
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF or DOCX files"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            return docx2txt.process(str(file_path))
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def analyze_skills(self, resume_text: str, target_skills: List[str] = None) -> Dict[str, SkillMatch]:
        """
        Analyze resume text and extract skills with proficiency levels
        
        Args:
            resume_text: Text content of the resume
            target_skills: List of specific skills to look for (optional)
        
        Returns:
            Dictionary mapping skill names to SkillMatch objects
        """
        text_lower = resume_text.lower()
        results = {}
        
        # If target skills specified, only analyze those
        skills_to_analyze = target_skills if target_skills else list(self.skill_patterns.keys())
        
        for skill in skills_to_analyze:
            if skill not in self.skill_patterns:
                # For unknown skills, do basic text matching
                patterns = [rf"\b{re.escape(skill.lower())}\b"]
            else:
                patterns = self.skill_patterns[skill]
            
            evidence = []
            skill_mentions = []
            
            # Find all mentions of the skill
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 50)
                    end = min(len(resume_text), match.end() + 50)
                    context = resume_text[start:end].strip()
                    evidence.append(context)
                    skill_mentions.append(match.group())
            
            if evidence:
                # Determine proficiency level
                proficiency = self._determine_proficiency(evidence, resume_text)
                years_exp = self._extract_years_experience(evidence, skill)
                
                results[skill] = SkillMatch(
                    skill=skill,
                    proficiency_level=proficiency,
                    confidence=self._calculate_confidence(evidence, skill_mentions),
                    evidence=evidence[:3],  # Keep top 3 evidence pieces
                    years_experience=years_exp
                )
        
        return results
    
    def _determine_proficiency(self, evidence: List[str], full_text: str) -> float:
        """Determine proficiency level based on evidence"""
        base_score = 2.0  # Default intermediate level
        
        # Check for proficiency indicators
        evidence_text = " ".join(evidence).lower()
        full_text_lower = full_text.lower()
        
        max_weight = 0
        for level, config in self.proficiency_indicators.items():
            for pattern in config["patterns"]:
                if re.search(pattern, evidence_text) or re.search(pattern, full_text_lower):
                    max_weight = max(max_weight, config["weight"])
        
        if max_weight > 0:
            base_score = max_weight
        
        # Adjust based on context clues
        if re.search(r"\b(\d+)\+?\s*years?\b", evidence_text):
            years_match = re.search(r"\b(\d+)\+?\s*years?\b", evidence_text)
            if years_match:
                years = int(years_match.group(1))
                if years >= 5:
                    base_score = min(5.0, base_score + 1.0)
                elif years >= 3:
                    base_score = min(5.0, base_score + 0.5)
        
        # Check for project indicators
        project_indicators = [
            r"\bproject\b", r"\bbuilt\b", r"\bdeveloped\b", r"\bcreated\b",
            r"\bimplemented\b", r"\bdesigned\b"
        ]
        
        project_count = sum(1 for pattern in project_indicators 
                          if re.search(pattern, evidence_text))
        
        if project_count >= 2:
            base_score = min(5.0, base_score + 0.5)
        
        return min(5.0, max(1.0, base_score))
    
    def _extract_years_experience(self, evidence: List[str], skill: str) -> Optional[int]:
        """Extract years of experience for a skill"""
        evidence_text = " ".join(evidence).lower()
        
        # Look for patterns like "3 years", "5+ years", etc.
        patterns = [
            rf"{re.escape(skill.lower())}.*?(\d+)\+?\s*years?",
            rf"(\d+)\+?\s*years?.*?{re.escape(skill.lower())}",
            rf"\b(\d+)\+?\s*years?\s*.*?{re.escape(skill.lower())}"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, evidence_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _calculate_confidence(self, evidence: List[str], mentions: List[str]) -> float:
        """Calculate confidence score based on evidence quality"""
        if not evidence:
            return 0.0
        
        base_confidence = min(1.0, len(evidence) * 0.2)  # More evidence = higher confidence
        
        # Boost confidence if there are specific examples or projects
        evidence_text = " ".join(evidence).lower()
        if re.search(r"\bproject\b|\bbuilt\b|\bdeveloped\b", evidence_text):
            base_confidence = min(1.0, base_confidence + 0.2)
        
        # Boost if there are quantifiable results
        if re.search(r"\b\d+%|\bimproved\b|\bincreased\b|\breduced\b", evidence_text):
            base_confidence = min(1.0, base_confidence + 0.1)
        
        return round(base_confidence, 2)
    
    def generate_skill_summary(self, skill_matches: Dict[str, SkillMatch]) -> Dict:
        """Generate a summary of extracted skills"""
        summary = {
            "total_skills_found": len(skill_matches),
            "skills_by_level": {
                "expert": [],
                "advanced": [], 
                "intermediate": [],
                "beginner": [],
                "basic": []
            },
            "top_skills": [],
            "skills_with_experience": []
        }
        
        for skill, match in skill_matches.items():
            level = match.proficiency_level
            if level >= 4.5:
                summary["skills_by_level"]["expert"].append(skill)
            elif level >= 3.5:
                summary["skills_by_level"]["advanced"].append(skill)
            elif level >= 2.5:
                summary["skills_by_level"]["intermediate"].append(skill)
            elif level >= 1.5:
                summary["skills_by_level"]["beginner"].append(skill)
            else:
                summary["skills_by_level"]["basic"].append(skill)
            
            if match.years_experience:
                summary["skills_with_experience"].append({
                    "skill": skill,
                    "years": match.years_experience,
                    "level": level
                })
        
        # Top skills by proficiency and confidence
        top_skills = sorted(skill_matches.items(), 
                          key=lambda x: (x[1].proficiency_level * x[1].confidence), 
                          reverse=True)[:10]
        
        summary["top_skills"] = [
            {
                "skill": skill,
                "proficiency": match.proficiency_level,
                "confidence": match.confidence
            }
            for skill, match in top_skills
        ]
        
        return summary

# Helper function for integration with existing system
def analyze_resume_for_role(resume_file_path: str, role_skills: List[str], 
                           target_role: str = None, department: str = None) -> Dict[str, Dict]:
    """
    Analyze resume for specific role skills with GROQ AI integration
    
    Args:
        resume_file_path: Path to resume PDF/DOCX
        role_skills: List of skills required for the role (can be None if target_role provided)
        target_role: Name of the target role (optional, for dynamic role lookup)
        department: Department of the target role (optional, for dynamic role lookup)
    
    Returns:
        Dictionary with skill analysis results
    """
    # If target_role and department are provided, try to get skills from dynamic role manager
    if target_role and department and DYNAMIC_ROLES_AVAILABLE:
        try:
            dynamic_manager = DynamicRoleManager()
            dynamic_role = dynamic_manager.get_role_by_name(target_role, department)
            if dynamic_role:
                # Get skills from dynamic role
                role_skills = [skill.skill_name for skill in dynamic_role.skills]
                print(f"🔍 Using dynamic role skills: {role_skills}")
        except Exception as e:
            print(f"⚠️ Failed to get dynamic role skills: {e}")
            # Continue with provided role_skills
    
    # Ensure we have role skills to analyze
    if not role_skills:
        print("⚠️ No role skills provided for analysis")
        return {
            "skills": {},
            "summary": {"total_skills_found": 0},
            "resume_text": "",
            "analysis_method": "none"
        }
    # Try GROQ first if available and API key is set
    if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
        try:
            print("🔍 Using GROQ AI for resume analysis...")
            parser = GroqResumeParser()
            
            # Extract target role from file path or use generic
            analysis_role = target_role or "Professional Role"  # Could be enhanced to extract from context
            
            # Analyze with GROQ
            groq_result = parser.analyze_resume_file(resume_file_path, role_skills, analysis_role)
            
            # Convert GROQ format to expected format
            skills_analysis = groq_result.get('skills_analysis', {})
            overall_assessment = groq_result.get('overall_assessment', {})
            
            result_skills = {}
            for skill in role_skills:
                if skill in skills_analysis:
                    skill_data = skills_analysis[skill]
                    result_skills[skill] = {
                        "level": skill_data.get('proficiency_level', 1.0),
                        "confidence": skill_data.get('confidence', 0.1),
                        "evidence": skill_data.get('evidence', ''),
                        "years_experience": None,  # GROQ doesn't extract this specifically
                        "related_experience": skill_data.get('related_experience', '')
                    }
                else:
                    result_skills[skill] = {
                        "level": 1.0,
                        "confidence": 0.1,
                        "evidence": "Skill not analyzed by GROQ",
                        "years_experience": None,
                        "related_experience": ""
                    }
            
            # Create summary from GROQ's overall assessment
            summary = {
                "total_skills_found": overall_assessment.get('total_skills_found', 0),
                "skills_found_in_resume": len([s for s in result_skills.values() if s['level'] > 1.0]),
                "skills_by_level": {
                    "expert": [skill for skill, data in result_skills.items() if data['level'] >= 4.5],
                    "advanced": [skill for skill, data in result_skills.items() if 3.5 <= data['level'] < 4.5],
                    "intermediate": [skill for skill, data in result_skills.items() if 2.5 <= data['level'] < 3.5],
                    "basic": [skill for skill, data in result_skills.items() if 1.5 <= data['level'] < 2.5],
                    "beginner": [skill for skill, data in result_skills.items() if data['level'] < 1.5]
                },
                "top_skills": overall_assessment.get('strongest_skills', []),
                "areas_for_development": overall_assessment.get('areas_for_development', []),
                "transferable_skills_bonus": overall_assessment.get('transferable_skills_bonus', ''),
                "analysis_method": "groq-ai",
                "average_proficiency": overall_assessment.get('average_proficiency', 1.0)
            }
            
            print(f"✅ GROQ analysis complete - found {summary['skills_found_in_resume']} skills above basic level")
            
            return {
                "skills": result_skills,
                "summary": summary,
                "resume_text": groq_result.get('metadata', {}).get('resume_length', 'N/A'),
                "analysis_method": "groq"
            }
            
        except Exception as e:
            print(f"⚠️ GROQ analysis failed: {e}")
            print("📝 Falling back to heuristic analysis...")
    
    # Fallback to original heuristic method
    print("📝 Using heuristic resume analysis...")
    analyzer = ResumeAnalyzer()
    
    try:
        # Extract text from resume
        resume_text = analyzer.extract_text_from_file(resume_file_path)
        
        # Analyze skills
        skill_matches = analyzer.analyze_skills(resume_text, role_skills)
        
        # Generate summary
        summary = analyzer.generate_skill_summary(skill_matches)
        
        # Convert to format compatible with existing system
        result = {}
        for skill, match in skill_matches.items():
            result[skill] = {
                "level": match.proficiency_level,
                "confidence": match.confidence,
                "evidence": match.evidence[0] if match.evidence else "",
                "years_experience": match.years_experience
            }
        
        # Add skills not found in resume with default values
        for skill in role_skills:
            if skill not in result:
                result[skill] = {
                    "level": 1.0,
                    "confidence": 0.1,
                    "evidence": "Skill not mentioned in resume",
                    "years_experience": None
                }
        
        # Add analysis method to summary
        summary["analysis_method"] = "heuristic"
        
        return {
            "skills": result,
            "summary": summary,
            "resume_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
            "analysis_method": "heuristic"
        }
        
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        # Return default values for all skills
        return {
            "skills": {
                skill: {
                    "level": 1.0,
                    "confidence": 0.1,
                    "evidence": f"Error analyzing resume: {str(e)}",
                    "years_experience": None
                }
                for skill in role_skills
            },
            "summary": {"total_skills_found": 0},
            "resume_text": ""
        }

if __name__ == "__main__":
    # Test the analyzer
    analyzer = ResumeAnalyzer()
    
    # Example usage
    test_text = """
    John Doe
    Senior Software Engineer
    
    I have 5+ years of experience in Python development, working with Django and Flask frameworks.
    Built multiple web applications using React and JavaScript. Advanced knowledge of SQL and database design.
    Led a team of 3 developers in creating microservices using Docker. Expert in AWS cloud services.
    """
    
    skills = analyzer.analyze_skills(test_text, ["Python", "React", "SQL", "Docker", "AWS", "Leadership"])
    
    for skill, match in skills.items():
        print(f"\n{skill}:")
        print(f"  Proficiency: {match.proficiency_level}")
        print(f"  Confidence: {match.confidence}")
        print(f"  Years: {match.years_experience}")
        print(f"  Evidence: {match.evidence[0] if match.evidence else 'None'}")
