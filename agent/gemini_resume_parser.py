"""
Simple resume parser using Google Gemini 2.5 Flash
Extracts skills from resume text with proficiency levels
"""

import google.generativeai as genai
import json
import os
from typing import Dict, List, Optional
import PyPDF2
import docx

class GeminiResumeParser:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Resume Parser
        Args:
            api_key: Google AI API key. If None, will try to read from GEMINI_API_KEY environment variable
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            
        if not api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
            
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
            
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from supported file formats"""
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError("Unsupported file format. Supported: PDF, DOCX, TXT")
            
    def parse_resume_for_skills(self, resume_text: str, target_skills: List[str], target_role: str = "") -> Dict:
        """
        Parse resume text and extract skill proficiency levels using Gemini
        
        Args:
            resume_text: The extracted text from resume
            target_skills: List of skills to look for
            target_role: Target role for context
            
        Returns:
            Dictionary with skill analysis results
        """
        
        prompt = f"""
You are an expert resume analyzer. Analyze the following resume and assess the candidate's proficiency in the specified skills.

RESUME TEXT:
{resume_text}

TARGET SKILLS TO ANALYZE:
{', '.join(target_skills)}

TARGET ROLE: {target_role}

For each skill, provide:
1. **Proficiency Level** (1.0-5.0 scale):
   - 1.0: No evidence or minimal mention
   - 2.0: Basic understanding, some exposure
   - 3.0: Intermediate, has used in projects
   - 4.0: Advanced, significant experience
   - 5.0: Expert level, extensive experience

2. **Confidence** (0.0-1.0): How confident you are in the assessment
3. **Evidence**: Brief quote or reasoning from the resume

IMPORTANT GUIDELINES:
- Consider transferable skills (e.g., Python experience helps with JavaScript)
- Look for years of experience, project complexity, leadership roles
- Consider related technologies and frameworks
- Be realistic but give credit for related experience
- If a skill isn't explicitly mentioned, consider if related skills suggest competency

Respond in this exact JSON format:
{{
    "skills_analysis": {{
        "skill_name": {{
            "proficiency_level": X.X,
            "confidence": X.X,
            "evidence": "Brief explanation with resume quotes",
            "related_experience": "Any related skills that support this assessment"
        }}
    }},
    "overall_assessment": {{
        "total_skills_found": X,
        "average_proficiency": X.X,
        "strongest_skills": ["skill1", "skill2"],
        "areas_for_development": ["skill1", "skill2"],
        "transferable_skills_bonus": "Explanation of how other skills help"
    }}
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean the response and extract JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                
            # Parse JSON
            result = json.loads(response_text.strip())
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.text}")
            # Return a fallback structure
            return self._create_fallback_analysis(target_skills)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._create_fallback_analysis(target_skills)
            
    def _create_fallback_analysis(self, target_skills: List[str]) -> Dict:
        """Create a fallback analysis if Gemini fails"""
        return {
            "skills_analysis": {
                skill: {
                    "proficiency_level": 1.0,
                    "confidence": 0.1,
                    "evidence": "Analysis failed - using fallback",
                    "related_experience": "Unknown"
                } for skill in target_skills
            },
            "overall_assessment": {
                "total_skills_found": 0,
                "average_proficiency": 1.0,
                "strongest_skills": [],
                "areas_for_development": target_skills,
                "transferable_skills_bonus": "Analysis unavailable"
            }
        }
        
    def analyze_resume_file(self, file_path: str, target_skills: List[str], target_role: str = "") -> Dict:
        """
        Complete workflow: extract text from file and analyze skills
        
        Args:
            file_path: Path to resume file
            target_skills: List of skills to analyze
            target_role: Target role for context
            
        Returns:
            Complete skill analysis
        """
        # Extract text from file
        resume_text = self.extract_text_from_file(file_path)
        
        # Analyze skills
        analysis = self.parse_resume_for_skills(resume_text, target_skills, target_role)
        
        # Add metadata
        analysis['metadata'] = {
            'resume_length': len(resume_text),
            'file_path': file_path,
            'target_role': target_role,
            'analysis_method': 'gemini-1.5-flash'
        }
        
        return analysis


# Simple test function
def test_parser():
    """Test the parser with a sample"""
    try:
        parser = GeminiResumeParser()
        
        # Test with your resume
        file_path = "/Users/pragathi.vetrivelmurugan/Downloads/Pragathi Kalidasan Vetrivel Murugan.pdf"
        target_skills = ["JavaScript", "React", "Python", "Problem Solving", "HTML", "CSS", "Git"]
        
        result = parser.analyze_resume_file(file_path, target_skills, "Frontend Developer")
        
        print("=== GEMINI RESUME ANALYSIS ===")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_parser()
