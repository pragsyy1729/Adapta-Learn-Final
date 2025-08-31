from flask import Blueprint, jsonify, request
import json
from datetime import datetime, timedelta
from ..services.data_access import get_data_file_path, _read_json, _write_json

gamification_bp = Blueprint('gamification', __name__)

def load_badges():
    """Load badges data"""
    path = get_data_file_path('badges.json')
    return _read_json(path, {})

def load_user_gamification():
    """Load user gamification data"""
    path = get_data_file_path('user_gamification.json')
    return _read_json(path, {})

def save_user_gamification(data):
    """Save user gamification data"""
    path = get_data_file_path('user_gamification.json')
    _write_json(path, data)

def load_users():
    """Load users data"""
    path = get_data_file_path('users.json')
    return _read_json(path, {})

def load_assessment_attempts():
    """Load assessment attempt data"""
    path = get_data_file_path('AssessmentAttempt.json')
    return _read_json(path, [])

def count_high_score_quizzes(user_id, min_score=90):
    """Count the number of quizzes where user scored >= min_score"""
    try:
        assessment_attempts = load_assessment_attempts()
        high_score_count = 0

        for attempt in assessment_attempts:
            attempt_data = attempt.get('attributes', attempt)
            if (attempt_data.get('user_id') == user_id and
                attempt_data.get('status') == 'graded' and
                attempt_data.get('score_percent', 0) >= min_score):
                high_score_count += 1

        return high_score_count

    except Exception as e:
        print(f"Error counting high score quizzes: {e}")
        return 0

def load_assessment_attempts():
    """Load assessment attempt data"""
    path = get_data_file_path('AssessmentAttempt.json')
    return _read_json(path, [])

def load_users():
    """Load users data"""
    path = get_data_file_path('users.json')
    return _read_json(path, {})

# Points system configuration
POINTS_CONFIG = {
    "module_completion": 50,
    "quiz_completion": 25,
    "quiz_perfect_score": 100,  # Bonus for 100% on quiz
    "microlearning_completion": 10,
    "daily_login": 5,
    "streak_bonus": 10,  # Per day of streak
    "first_module_category": 25,  # Bonus for completing first module in a category
}

def calculate_level(experience_points):
    """Calculate user level based on experience points"""
    # Simple level calculation: every 100 points = 1 level
    return max(1, (experience_points // 100) + 1)

def load_badges():
    """Load badges data"""
    path = get_data_file_path('badges.json')
    return _read_json(path, {})

@ gamification_bp.route('/user/<user_id>/stats', methods=['GET'])
def get_user_gamification_stats(user_id):
    """Get user's gamification statistics"""
    try:
        gamification_data = load_user_gamification()
        user_stats = gamification_data.get(user_id, {
            "user_id": user_id,
            "total_points": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "badges": [],
            "current_level": 1,
            "streak_days": 0,
            "last_activity": None,
            "activity_history": [],
            "category_progress": {}
        })

        # Calculate level based on experience points
        user_stats["current_level"] = calculate_level(user_stats["total_points"])
        user_stats["level"] = user_stats["current_level"]  # For backward compatibility

        return jsonify(user_stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ gamification_bp.route('/user/<user_id>/award-points', methods=['POST'])
def award_points(user_id):
    """Award points to user for an activity"""
    try:
        data = request.get_json()
        activity_type = data.get('activity_type')
        activity_details = data.get('details', {})

        if not activity_type:
            return jsonify({"error": "activity_type is required"}), 400

        # Get base points for activity
        base_points = POINTS_CONFIG.get(activity_type, 0)

        # Calculate bonus points
        bonus_points = 0

        if activity_type == "quiz_completion":
            score = activity_details.get('score_percentage', 0)
            if score == 100:
                bonus_points += POINTS_CONFIG["quiz_perfect_score"]
        elif activity_type == "module_completion":
            category = activity_details.get('category')
            if category:
                # Check if this is the first module in this category
                gamification_data = load_user_gamification()
                user_stats = gamification_data.get(user_id, {})
                category_progress = user_stats.get('category_progress', {})

                if category not in category_progress:
                    bonus_points += POINTS_CONFIG["first_module_category"]
                    category_progress[category] = {"completed": 1, "first_completion": True}
                else:
                    category_progress[category]["completed"] += 1

        total_points = base_points + bonus_points

        # Update user gamification data
        gamification_data = load_user_gamification()

        if user_id not in gamification_data:
            gamification_data[user_id] = {
                "user_id": user_id,
                "total_points": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "badges": [],
                "current_level": 1,
                "streak_days": 0,
                "last_activity": None,
                "activity_history": [],
                "category_progress": {}
            }

        user_stats = gamification_data[user_id]

        # Update points and experience
        user_stats["total_points"] += total_points

        # Update streak
        now = datetime.now()
        last_activity = user_stats.get("last_activity")

        if last_activity:
            last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00')).date()
            today = now.date()

            if (today - last_date).days == 1:
                # Consecutive day
                user_stats["current_streak"] += 1
            elif (today - last_date).days > 1:
                # Streak broken
                user_stats["current_streak"] = 1
        else:
            # First activity
            user_stats["current_streak"] = 1

        # Update longest streak
        if user_stats["current_streak"] > user_stats["longest_streak"]:
            user_stats["longest_streak"] = user_stats["current_streak"]

        # Update last activity
        user_stats["last_activity"] = now.isoformat() + 'Z'

        # Add to activity history
        activity_record = {
            "activity_type": activity_type,
            "points_awarded": total_points,
            "base_points": base_points,
            "bonus_points": bonus_points,
            "timestamp": user_stats["last_activity"],
            "details": activity_details
        }
        user_stats["activity_history"].append(activity_record)

        # Keep only last 50 activities
        user_stats["activity_history"] = user_stats["activity_history"][-50:]

        # Check for new badges
        new_badges = check_and_award_badges(user_id, user_stats)
        if "badges" not in user_stats:
            user_stats["badges"] = []
        user_stats["badges"].extend(new_badges)

        # Save updated data
        save_user_gamification(gamification_data)

        return jsonify({
            "success": True,
            "points_awarded": total_points,
            "base_points": base_points,
            "bonus_points": bonus_points,
            "total_points": user_stats["total_points"],
            "current_streak": user_stats["current_streak"],
            "level": calculate_level(user_stats["total_points"]),
            "new_badges": new_badges
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def award_points(user_id, activity_data):
    """Standalone function to award points that can be called from other modules"""
    try:
        data = {
            'activity_type': activity_data.get('activity_type'),
            'details': activity_data.get('details', {})
        }

        if not data['activity_type']:
            return {"error": "activity_type is required"}

        # Get base points for activity
        base_points = POINTS_CONFIG.get(data['activity_type'], 0)

        # Calculate bonus points
        bonus_points = 0
        activity_details = data.get('details', {})

        if data['activity_type'] == "quiz_completion":
            score = activity_details.get('score_percentage', 0)
            if score == 100:
                bonus_points += POINTS_CONFIG["quiz_perfect_score"]
        elif data['activity_type'] == "module_completion":
            category = activity_details.get('category')
            if category:
                # Check if this is the first module in this category
                gamification_data = load_user_gamification()
                user_stats = gamification_data.get(user_id, {})
                category_progress = user_stats.get('category_progress', {})

                if category not in category_progress:
                    bonus_points += POINTS_CONFIG["first_module_category"]
                    category_progress[category] = {"completed": 1, "first_completion": True}
                else:
                    category_progress[category]["completed"] += 1

        total_points = base_points + bonus_points

        # Update user gamification data
        gamification_data = load_user_gamification()

        if user_id not in gamification_data:
            gamification_data[user_id] = {
                "user_id": user_id,
                "total_points": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "badges": [],
                "current_level": 1,
                "streak_days": 0,
                "last_activity": None,
                "activity_history": [],
                "category_progress": {}
            }

        user_stats = gamification_data[user_id]

        # Update points
        user_stats["total_points"] += total_points

        # Update streak
        now = datetime.now()
        last_activity = user_stats.get("last_activity")

        if last_activity:
            last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00')).date()
            today = now.date()

            if (today - last_date).days == 1:
                # Consecutive day
                user_stats["current_streak"] += 1
            elif (today - last_date).days > 1:
                # Streak broken
                user_stats["current_streak"] = 1
        else:
            # First activity
            user_stats["current_streak"] = 1

        # Update longest streak
        if user_stats["current_streak"] > user_stats["longest_streak"]:
            user_stats["longest_streak"] = user_stats["current_streak"]

        # Update last activity
        user_stats["last_activity"] = now.isoformat() + 'Z'

        # Add to activity history
        activity_record = {
            "activity_type": data['activity_type'],
            "points_awarded": total_points,
            "base_points": base_points,
            "bonus_points": bonus_points,
            "timestamp": user_stats["last_activity"],
            "details": activity_details
        }
        user_stats["activity_history"].append(activity_record)

        # Keep only last 50 activities
        user_stats["activity_history"] = user_stats["activity_history"][-50:]

        # Check for new badges
        new_badges = check_and_award_badges(user_id, user_stats)
        if "badges" not in user_stats:
            user_stats["badges"] = []
        user_stats["badges"].extend(new_badges)

        # Save updated data
        save_user_gamification(gamification_data)

        return {
            "success": True,
            "points_awarded": total_points,
            "base_points": base_points,
            "bonus_points": bonus_points,
            "total_points": user_stats["total_points"],
            "current_streak": user_stats["current_streak"],
            "level": calculate_level(user_stats["total_points"]),
            "new_badges": new_badges
        }

    except Exception as e:
        return {"error": str(e)}

def check_and_award_badges(user_id, user_stats):
    """Check if user qualifies for any new badges"""
    badges = load_badges()
    new_badges = []

    for badge_id, badge in badges.items():
        # Skip if already earned
        existing_badge_ids = [b.get("badge_id") if isinstance(b, dict) else b for b in user_stats.get("badges", [])]
        if badge_id in existing_badge_ids:
            continue

        criteria = badge.get("criteria", {})
        criteria_type = criteria.get("type")

        qualifies = False

        if criteria_type == "total_points":
            if user_stats.get("total_points", 0) >= criteria.get("threshold", 0):
                qualifies = True

        elif criteria_type == "streak":
            if user_stats.get("longest_streak", 0) >= criteria.get("days", 0):
                qualifies = True

        elif criteria_type == "module_completion":
            category = criteria.get("category")
            required_count = criteria.get("count", 0)
            category_progress = user_stats.get("category_progress", {})
            if category in category_progress:
                if category_progress[category].get("completed", 0) >= required_count:
                    qualifies = True

        elif criteria_type == "quiz_score":
            # Count high-scoring quiz attempts for this user
            min_score = criteria.get("min_score", 90)
            required_count = criteria.get("count", 5)
            high_score_quizzes = count_high_score_quizzes(user_id, min_score)
            if high_score_quizzes >= required_count:
                qualifies = True

        elif criteria_type == "microlearning_completion":
            # This would need to be checked against microlearning progress
            # For now, we'll use a simplified check
            microlearning_completed = 0  # This should be calculated from microlearning history
            if microlearning_completed >= criteria.get("count", 0):
                qualifies = True

        if qualifies:
            new_badges.append({
                "badge_id": badge_id,
                "name": badge["name"],
                "description": badge["description"],
                "icon": badge["icon"],
                "rarity": badge["rarity"],
                "awarded_at": datetime.now().isoformat() + 'Z'
            })

    return new_badges

@ gamification_bp.route('/badges', methods=['GET'])
def get_all_badges():
    """Get all available badges"""
    try:
        badges = load_badges()
        return jsonify({"badges": list(badges.values())})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ gamification_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get gamification leaderboard"""
    try:
        department = request.args.get('department')
        timeframe = request.args.get('timeframe', 'all')  # all, month, week

        gamification_data = load_user_gamification()
        users_data = load_users()

        leaderboard = []

        for user_id, stats in gamification_data.items():
            # Find user details
            user_info = None
            for email, user in users_data.items():
                if user.get('user_id') == user_id:
                    user_info = {
                        "name": user.get('name', 'Unknown'),
                        "department": user.get('profile', {}).get('department', 'Unknown'),
                        "role": user.get('profile', {}).get('role', 'Unknown')
                    }
                    break

            if user_info:
                # Apply department filter
                if department and user_info['department'] != department:
                    continue

                # Calculate score based on timeframe
                score = stats.get('total_points', 0)

                if timeframe != 'all':
                    # Filter activities by timeframe
                    cutoff_date = datetime.now()
                    if timeframe == 'week':
                        cutoff_date = cutoff_date - timedelta(days=7)
                    elif timeframe == 'month':
                        cutoff_date = cutoff_date - timedelta(days=30)

                    recent_activities = [
                        activity for activity in stats.get('activity_history', [])
                        if datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00')) >= cutoff_date
                    ]

                    score = sum(activity['points_awarded'] for activity in recent_activities)

                leaderboard.append({
                    "user_id": user_id,
                    "name": user_info["name"],
                    "department": user_info["department"],
                    "role": user_info["role"],
                    "total_points": stats.get('total_points', 0),
                    "score": score,
                    "level": calculate_level(stats.get('total_points', 0)),
                    "current_streak": stats.get('current_streak', 0),
                    "badges_count": len(stats.get('badges', []))
                })

        # Sort by score
        leaderboard.sort(key=lambda x: x["score"], reverse=True)

        return jsonify({
            "leaderboard": leaderboard[:50],  # Top 50
            "department": department,
            "timeframe": timeframe,
            "total_participants": len(leaderboard)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ gamification_bp.route('/user/<user_id>/badges', methods=['GET'])
def get_user_badges(user_id):
    """Get user's earned badges"""
    try:
        gamification_data = load_user_gamification()
        user_stats = gamification_data.get(user_id, {})

        badges = load_badges()
        earned_badges = []

        for badge_id in user_stats.get("badges", []):
            if isinstance(badge_id, dict):
                # Already full badge object
                earned_badges.append(badge_id)
            elif badge_id in badges:
                badge_data = badges[badge_id].copy()
                earned_badges.append(badge_data)

        return jsonify({
            "earned_badges": earned_badges,
            "total_badges": len(earned_badges)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ gamification_bp.route('/user/<user_id>/rank', methods=['GET'])
def get_user_rank(user_id):
    """Get user's rank in leaderboard"""
    try:
        department = request.args.get('department')

        # Get leaderboard
        leaderboard_response = get_leaderboard()
        if leaderboard_response.status_code != 200:
            return leaderboard_response

        leaderboard_data = leaderboard_response.get_json()
        leaderboard = leaderboard_data['leaderboard']

        # Find user's rank
        user_rank = None
        user_stats = None

        for i, entry in enumerate(leaderboard, 1):
            if entry['user_id'] == user_id:
                user_rank = i
                user_stats = entry
                break

        if user_rank:
            return jsonify({
                "rank": user_rank,
                "total_participants": len(leaderboard),
                "user_stats": user_stats,
                "percentile": ((len(leaderboard) - user_rank + 1) / len(leaderboard)) * 100
            })
        else:
            return jsonify({"error": "User not found in leaderboard"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
