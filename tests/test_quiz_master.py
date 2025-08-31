#!/usr/bin/env python3
"""
Test script to verify Quiz Master badge implementation
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.routes.gamification import count_high_score_quizzes, check_and_award_badges, load_user_gamification

def test_quiz_master_badge():
    """Test the Quiz Master badge functionality"""

    print("🧠 Testing Quiz Master Badge Implementation")
    print("=" * 50)

    # Test 1: Count high score quizzes for user_001
    print("\n1. Testing high score quiz counting:")
    user_id = "user_001"
    high_score_count = count_high_score_quizzes(user_id, min_score=90)
    print(f"   User {user_id} has {high_score_count} quizzes with score >= 90%")

    # Test 2: Check badge qualification
    print("\n2. Testing badge qualification:")
    gamification_data = load_user_gamification()
    user_stats = gamification_data.get(user_id, {})

    print(f"   User stats: {user_stats.get('total_points', 0)} points, {len(user_stats.get('badges', []))} badges")

    # Manually test the badge criteria
    from backend.app.routes.gamification import load_badges
    badges = load_badges()
    quiz_master = badges.get('BADGE_QUIZ_MASTER', {})

    print(f"   Quiz Master criteria: {quiz_master.get('criteria', {})}")

    # Test the badge checking logic
    new_badges = check_and_award_badges(user_id, user_stats)

    print(f"   New badges earned: {len(new_badges)}")
    for badge in new_badges:
        print(f"   - {badge['name']}: {badge['description']}")

    # Test 3: Simulate earning the badge
    print("\n3. Simulating badge earning:")
    if high_score_count >= 5:
        print("   ✅ User qualifies for Quiz Master badge!")
    else:
        print(f"   ❌ User needs {5 - high_score_count} more high-score quizzes")

    print("\n" + "=" * 50)
    print("✅ Quiz Master badge implementation test completed!")

if __name__ == "__main__":
    test_quiz_master_badge()
