#!/usr/bin/env python3
"""
Test script for GROQ Resume Parser
"""

import os
import sys
import json

# Add the agent directory to the path
sys.path.append('/Users/pragathi.vetrivelmurugan/Downloads/adapta-learn')

def test_groq_parser():
    """Test the GROQ parser with Pragathi's resume"""
    
    # You need to set your GROQ API key
    api_key = input("Enter your GROQ API key (or press Enter to skip): ").strip()
    if not api_key:
        print("No API key provided. Please set GROQ_API_KEY environment variable.")
        print("Get your key from: https://console.groq.com/keys")
        return
    
    # Set the API key
    os.environ['GROQ_API_KEY'] = api_key
    
    try:
        from agent.groq_resume_parser import GroqResumeParser
        
        # Initialize parser
        parser = GroqResumeParser(api_key)
        
        # Test with your resume
        resume_path = "/Users/pragathi.vetrivelmurugan/Downloads/Pragathi Kalidasan Vetrivel Murugan.pdf"
        
        # Skills to analyze (matching the onboarding analysis)
        target_skills = [
            "JavaScript",
            "React", 
            "Problem Solving",
            "HTML",
            "CSS",
            "Git",
            "Python"  # Added since you clearly have Python experience
        ]
        
        target_role = "Frontend Developer"
        
        print("🔍 Analyzing resume with GROQ...")
        print(f"📄 File: {resume_path}")
        print(f"🎯 Target Role: {target_role}")
        print(f"📋 Skills to analyze: {', '.join(target_skills)}")
        print("-" * 60)
        
        result = parser.analyze_resume_file(resume_path, target_skills, target_role)
        
        print("=== GROQ ANALYSIS RESULTS ===")
        print(json.dumps(result, indent=2))
        
        # Compare with basic skill counts
        skills_analysis = result.get('skills_analysis', {})
        above_basic = [skill for skill, data in skills_analysis.items() 
                      if data.get('proficiency_level', 0) > 1.5]
        
        print(f"\n📊 SUMMARY:")
        print(f"   Skills above basic level: {len(above_basic)}")
        print(f"   Skills: {', '.join(above_basic)}")
        
        # Show evidence for top skills
        print(f"\n💡 TOP SKILL EVIDENCE:")
        for skill, data in skills_analysis.items():
            if data.get('proficiency_level', 0) > 2.0:
                print(f"   {skill}: {data.get('evidence', '')[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_groq_parser()
