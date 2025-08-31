"""
AI Recommendations Service using Groq
Analyzes learning paths progress, user progress, deadlines, and skill gaps to provide personalized recommendations
"""

import groq
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .data_access import get_data_file_path, _read_json


class AIRecommendationsService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Recommendations Service
        Args:
            api_key: Groq API key. If None, will try to read from GROQ_API_KEY environment variable
        """
        if api_key is None:
            api_key = os.getenv('GROQ_API_KEY')

        if not api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")

        self.client = groq.Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def get_user_learning_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive learning data for a user including progress, skill gaps, and deadlines
        """
        # Get learning path progress
        learning_path_progress = self._get_learning_path_progress(user_id)

        # Get user dashboard data
        user_dashboard = self._get_user_dashboard(user_id)

        # Get learning paths details
        learning_paths = self._get_learning_paths()

        # Get skill gap analysis
        skill_gaps = self._get_skill_gap_analysis(user_id)

        # Calculate deadlines and progress insights
        progress_analysis = self._analyze_progress(learning_path_progress, learning_paths)

        return {
            "user_id": user_id,
            "learning_path_progress": learning_path_progress,
            "user_dashboard": user_dashboard,
            "learning_paths": learning_paths,
            "skill_gaps": skill_gaps,
            "progress_analysis": progress_analysis,
            "timestamp": datetime.now().isoformat()
        }

    def _get_learning_path_progress(self, user_id: str) -> List[Dict]:
        """Get learning path progress for a specific user"""
        try:
            progress_file = get_data_file_path('LearningPathProgress.json')
            all_progress = _read_json(progress_file, [])

            user_progress = [
                item for item in all_progress
                if item.get('attributes', {}).get('user_id') == user_id
            ]

            return user_progress
        except Exception as e:
            print(f"Error getting learning path progress: {e}")
            return []

    def _get_user_dashboard(self, user_id: str) -> Optional[Dict]:
        """Get user dashboard data"""
        try:
            dashboard_file = get_data_file_path('UserDashboard.json')
            all_dashboards = _read_json(dashboard_file, [])

            for dashboard in all_dashboards:
                if dashboard.get('attributes', {}).get('user_id') == user_id:
                    return dashboard.get('attributes', {})

            return None
        except Exception as e:
            print(f"Error getting user dashboard: {e}")
            return None

    def _get_learning_paths(self) -> Dict[str, Dict]:
        """Get all learning paths data"""
        try:
            paths_file = get_data_file_path('LearningPaths.json')
            learning_paths = _read_json(paths_file, {})

            # Also get LearningPath.json if it exists
            try:
                lp_file = get_data_file_path('LearningPath.json')
                lp_data = _read_json(lp_file, [])
                for item in lp_data:
                    if 'id' in item:
                        learning_paths[item['id']] = item
            except:
                pass

            return learning_paths
        except Exception as e:
            print(f"Error getting learning paths: {e}")
            return {}

    def _get_skill_gap_analysis(self, user_id: str) -> List[Dict]:
        """Get skill gap analysis for a specific user"""
        try:
            skill_gap_file = get_data_file_path('SkillGapAnalysis.json')
            all_gaps = _read_json(skill_gap_file, [])

            user_gaps = []
            for gap_entry in all_gaps:
                if gap_entry.get('attributes', {}).get('user_id') == user_id:
                    user_gaps = gap_entry.get('attributes', {}).get('gaps', [])
                    break

            return user_gaps
        except Exception as e:
            print(f"Error getting skill gap analysis: {e}")
            return []

    def _analyze_progress(self, progress_data: List[Dict], learning_paths: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze progress data to extract insights"""
        analysis = {
            "total_paths": len(progress_data),
            "completed_paths": 0,
            "in_progress_paths": 0,
            "not_started_paths": 0,
            "average_progress": 0.0,
            "total_time_invested": 0,
            "upcoming_deadlines": [],
            "stalled_paths": [],
            "high_priority_paths": []
        }

        total_progress = 0
        current_date = datetime.now()

        for progress in progress_data:
            attrs = progress.get('attributes', {})
            path_id = attrs.get('learning_path_id')
            status = attrs.get('status', 'not_started')
            progress_percent = attrs.get('progress_percent', 0)
            time_invested = attrs.get('time_invested_minutes', 0)
            enrolled_at = attrs.get('enrolled_at')
            estimated_weeks = attrs.get('estimated_completion_weeks')

            # Count by status
            if status == 'completed':
                analysis["completed_paths"] += 1
            elif status == 'in_progress':
                analysis["in_progress_paths"] += 1
            else:
                analysis["not_started_paths"] += 1

            # Calculate progress
            total_progress += progress_percent
            analysis["total_time_invested"] += time_invested

            # Calculate deadlines
            if enrolled_at and estimated_weeks:
                try:
                    enrolled_date = datetime.fromisoformat(enrolled_at.replace('Z', '+00:00'))
                    deadline = enrolled_date + timedelta(weeks=int(estimated_weeks))
                    days_until_deadline = (deadline - current_date).days

                    if days_until_deadline > 0:
                        analysis["upcoming_deadlines"].append({
                            "path_id": path_id,
                            "deadline": deadline.isoformat(),
                            "days_remaining": days_until_deadline,
                            "progress": progress_percent
                        })

                        # High priority if deadline is within 2 weeks and progress < 50%
                        if days_until_deadline <= 14 and progress_percent < 50:
                            analysis["high_priority_paths"].append(path_id)
                except Exception as e:
                    print(f"Error calculating deadline for {path_id}: {e}")

            # Stalled paths (no progress for more than 7 days)
            last_accessed = attrs.get('last_accessed_at')
            if last_accessed and status == 'in_progress':
                try:
                    last_access_date = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                    days_since_access = (current_date - last_access_date).days
                    if days_since_access > 7:
                        analysis["stalled_paths"].append({
                            "path_id": path_id,
                            "days_stalled": days_since_access,
                            "current_progress": progress_percent
                        })
                except Exception as e:
                    print(f"Error checking stalled status for {path_id}: {e}")

        # Calculate averages
        if analysis["total_paths"] > 0:
            analysis["average_progress"] = total_progress / analysis["total_paths"]

        # Sort deadlines by urgency
        analysis["upcoming_deadlines"].sort(key=lambda x: x["days_remaining"])

        return analysis

    def generate_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Generate AI-powered recommendations for a user based on their learning data and skill gaps
        """
        # Get user learning data
        user_data = self.get_user_learning_data(user_id)

        # Create comprehensive prompt for Groq
        prompt = self._create_recommendations_prompt(user_data)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            # Clean and parse response
            response_text = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            # Parse JSON response
            recommendations = json.loads(response_text.strip())

            # Add metadata
            recommendations['metadata'] = {
                'user_id': user_id,
                'generated_at': datetime.now().isoformat(),
                'analysis_timestamp': user_data['timestamp'],
                'ai_model': 'llama-3.1-8b-instant'
            }

            return recommendations

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response.choices[0].message.content}")
            return self._create_fallback_recommendations(user_data)

        except Exception as e:
            print(f"Groq API error: {e}")
            return self._create_fallback_recommendations(user_data)

    def _create_recommendations_prompt(self, user_data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for GROQ to generate recommendations"""

        progress_analysis = user_data['progress_analysis']
        skill_gaps = user_data.get('skill_gaps', [])

        # Format skill gaps for the prompt
        skill_gaps_text = ""
        if skill_gaps:
            skill_gaps_text = "\nSKILL GAP ANALYSIS:\n"
            for gap in skill_gaps:
                skill_gaps_text += f"- {gap['skill']}: Current Level {gap['current_level']}, Required Level {gap['required_level']}, Gap Score {gap['gap_score']:.2f}\n"
        else:
            skill_gaps_text = "\nSKILL GAP ANALYSIS: No skill gap data available\n"

        prompt = f"""
You are an expert learning advisor AI. Analyze the following user learning data and provide personalized recommendations to help them succeed in their learning journey.

USER LEARNING DATA:
{json.dumps(user_data, indent=2)}

{skill_gaps_text}

KEY METRICS TO ANALYZE:
- Total Learning Paths: {progress_analysis['total_paths']}
- Completed: {progress_analysis['completed_paths']}
- In Progress: {progress_analysis['in_progress_paths']}
- Not Started: {progress_analysis['not_started_paths']}
- Average Progress: {progress_analysis['average_progress']:.1f}%
- Total Time Invested: {progress_analysis['total_time_invested']} minutes
- Upcoming Deadlines: {len(progress_analysis['upcoming_deadlines'])}
- Stalled Paths: {len(progress_analysis['stalled_paths'])}
- High Priority Paths: {len(progress_analysis['high_priority_paths'])}

ANALYSIS REQUIREMENTS:
1. **Learning Pace Assessment**: Evaluate if the user is progressing too slowly, too quickly, or at an optimal pace
2. **Time Management**: Assess time investment patterns and suggest improvements
3. **Deadline Management**: Identify urgent deadlines and prioritization needs
4. **Stalled Learning**: Address paths with no recent progress
5. **Skill Gap Analysis**: Review skill gaps and recommend targeted learning activities
6. **Difficulty Balance**: Suggest appropriate difficulty levels based on performance
7. **Focus Areas**: Identify which skills/topics need more attention based on gaps
8. **Motivation & Engagement**: Provide encouragement and motivation strategies

RECOMMENDATION CATEGORIES TO INCLUDE:
- **Immediate Actions** (next 1-3 days)
- **Short-term Goals** (next 1-2 weeks)
- **Long-term Strategy** (next 1-3 months)
- **Study Habits** (ongoing improvements)
- **Skill Development** (addressing specific skill gaps)
- **Resource Suggestions** (additional materials/tools)
- **Motivational Support** (encouragement and mindset)

IMPORTANT GUIDELINES:
- Be specific and actionable, not generic
- Consider the user's current progress and time constraints
- Balance challenging goals with realistic expectations
- Focus on both technical skills and learning habits
- Include measurable objectives where possible
- Provide time estimates for recommended activities
- Consider work-life balance and sustainable learning pace
- Address skill gaps with targeted recommendations

Respond in this exact JSON format:
{{
    "learning_pace_assessment": {{
        "current_pace": "too_slow|optimal|too_fast",
        "assessment": "Detailed analysis of learning speed",
        "recommendation": "Specific advice on pace adjustment"
    }},
    "priority_actions": [
        {{
            "action": "Specific actionable step",
            "timeframe": "1-3 days|1-2 weeks|ongoing",
            "impact": "high|medium|low",
            "reasoning": "Why this action is important"
        }}
    ],
    "deadline_management": {{
        "urgent_deadlines": ["List of critical deadlines"],
        "time_management_strategy": "Specific strategy for meeting deadlines",
        "prioritization_plan": "How to prioritize multiple deadlines"
    }},
    "stalled_paths_recovery": [
        {{
            "path_id": "learning_path_id",
            "days_stalled": X,
            "recovery_strategy": "Specific plan to restart progress",
            "motivation_tip": "Encouraging message to restart"
        }}
    ],
    "skill_gap_analysis": {{
        "critical_gaps": ["Most important skill gaps to address"],
        "skill_development_plan": "Strategy for addressing skill gaps",
        "recommended_learning_activities": ["Specific activities to improve skills"],
        "time_allocation": "Suggested time allocation for skill development"
    }},
    "skill_development_plan": {{
        "focus_areas": ["Key skills to prioritize based on gaps"],
        "learning_sequence": ["Recommended order of topics based on gaps"],
        "difficulty_progression": "How to advance difficulty levels",
        "practice_recommendations": ["Specific practice activities for skill gaps"]
    }},
    "time_management_advice": {{
        "daily_study_time": "Recommended daily study hours",
        "session_structure": "How to structure study sessions",
        "consistency_tips": ["Tips for maintaining regular study habits"],
        "break_strategies": "How to incorporate breaks effectively"
    }},
    "motivational_support": {{
        "progress_celebration": "Acknowledge current achievements",
        "encouragement_message": "Motivational message for continued progress",
        "mindset_tips": ["Positive mindset strategies"],
        "goal_setting": "SMART goals for the next milestone"
    }},
    "resource_suggestions": [
        {{
            "resource_type": "book|course|tool|community",
            "name": "Specific resource name",
            "purpose": "How it helps the learning journey",
            "time_commitment": "Estimated time to complete/use"
        }}
    ],
    "success_prediction": {{
        "confidence_level": "high|medium|low",
        "estimated_completion": "Time estimate for current goals",
        "key_success_factors": ["Critical elements for success"],
        "potential_challenges": ["Anticipated obstacles and solutions"]
    }}
}}
"""

        return prompt

    def _create_fallback_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback recommendations if GROQ fails"""
        progress_analysis = user_data['progress_analysis']
        skill_gaps = user_data.get('skill_gaps', [])

        return {
            "learning_pace_assessment": {
                "current_pace": "unknown",
                "assessment": "Analysis unavailable - using basic recommendations",
                "recommendation": "Continue with current learning path and maintain regular study sessions"
            },
            "priority_actions": [
                {
                    "action": "Complete at least one module this week",
                    "timeframe": "1-3 days",
                    "impact": "high",
                    "reasoning": "Maintain momentum in learning journey"
                },
                {
                    "action": "Review progress on all enrolled learning paths",
                    "timeframe": "1-2 weeks",
                    "impact": "medium",
                    "reasoning": "Ensure balanced progress across all paths"
                }
            ],
            "deadline_management": {
                "urgent_deadlines": [],
                "time_management_strategy": "Set aside dedicated study time each day",
                "prioritization_plan": "Focus on high-priority paths first"
            },
            "stalled_paths_recovery": [],
            "skill_gap_analysis": {
                "critical_gaps": [gap.get('skill', 'Unknown skill') for gap in skill_gaps[:3]],
                "skill_development_plan": "Focus on high-gap skills first",
                "recommended_learning_activities": ["Practice exercises", "Review materials", "Apply concepts"],
                "time_allocation": "30 minutes daily per skill gap"
            },
            "skill_development_plan": {
                "focus_areas": [gap.get('skill', 'Unknown skill') for gap in skill_gaps[:3]],
                "learning_sequence": ["Start with fundamentals", "Build complexity gradually"],
                "difficulty_progression": "Begin at current level, increase gradually",
                "practice_recommendations": ["Daily practice sessions", "Apply skills in projects"]
            },
            "time_management_advice": {
                "daily_study_time": "1-2 hours daily",
                "session_structure": "25-minute focused sessions with 5-minute breaks",
                "consistency_tips": ["Study at the same time each day", "Track progress weekly"],
                "break_strategies": "Take regular breaks to maintain focus"
            },
            "motivational_support": {
                "progress_celebration": "Keep up the good work!",
                "encouragement_message": "Every step forward is progress toward your goals",
                "mindset_tips": ["Focus on learning, not perfection", "Celebrate small wins"],
                "goal_setting": "Complete one module per week"
            },
            "resource_suggestions": [
                {
                    "resource_type": "practice",
                    "name": "Regular practice exercises",
                    "purpose": "Reinforce learning through application",
                    "time_commitment": "30 minutes daily"
                }
            ],
            "success_prediction": {
                "confidence_level": "medium",
                "estimated_completion": f"{progress_analysis['total_paths']} learning paths",
                "key_success_factors": ["Consistency", "Regular practice", "Skill gap focus"],
                "potential_challenges": ["Time management", "Maintaining motivation", "Skill complexity"]
            },
            "metadata": {
                "user_id": user_data['user_id'],
                "generated_at": datetime.now().isoformat(),
                "analysis_timestamp": user_data['timestamp'],
                "ai_model": "llama-3.1-8b-instant"
            }
        }


# Test function
def test_recommendations_service():
    """Test the recommendations service"""
    try:
        service = AIRecommendationsService()

        # Test with a sample user
        user_id = "user_022"  # Using an existing user from the data

        print(f"🔍 Generating AI recommendations for user: {user_id}")

        recommendations = service.generate_recommendations(user_id)

        print("=== AI RECOMMENDATIONS RESULTS ===")
        print(json.dumps(recommendations, indent=2))

    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    test_recommendations_service()
