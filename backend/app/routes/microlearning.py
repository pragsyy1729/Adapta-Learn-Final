from flask import Blueprint, jsonify, request
import json
import uuid
from datetime import datetime
from ..services.data_access import get_data_file_path, _read_json, _write_json

microlearning_bp = Blueprint('microlearning', __name__)

def load_microlearning_modules():
    """Load microlearning modules data"""
    path = get_data_file_path('microlearning_modules.json')
    return _read_json(path, {})

def load_user_microlearning_progress():
    """Load user microlearning progress data"""
    path = get_data_file_path('user_microlearning_progress.json')
    return _read_json(path, {})

def save_user_microlearning_progress(data):
    """Save user microlearning progress data"""
    path = get_data_file_path('user_microlearning_progress.json')
    _write_json(path, data)

@microlearning_bp.route('/modules', methods=['GET'])
def get_microlearning_modules():
    """Get all available microlearning modules with optional filtering"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        duration_max = request.args.get('duration_max', type=int)

        modules = load_microlearning_modules()
        filtered_modules = []

        for module_id, module in modules.items():
            # Apply filters
            if category and module.get('category') != category:
                continue
            if difficulty and module.get('difficulty') != difficulty:
                continue
            if duration_max and module.get('duration_minutes', 0) > duration_max:
                continue

            filtered_modules.append(module)

        return jsonify({
            "modules": filtered_modules,
            "total_count": len(filtered_modules)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@microlearning_bp.route('/modules/<module_id>', methods=['GET'])
def get_microlearning_module(module_id):
    """Get a specific microlearning module"""
    try:
        modules = load_microlearning_modules()
        module = modules.get(module_id)

        if not module:
            return jsonify({"error": "Microlearning module not found"}), 404

        return jsonify(module)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@microlearning_bp.route('/user/<user_id>/progress', methods=['GET'])
def get_user_microlearning_progress(user_id):
    """Get user's microlearning progress"""
    try:
        progress_data = load_user_microlearning_progress()
        user_progress = progress_data.get(user_id, {
            "user_id": user_id,
            "completed_modules": [],
            "in_progress_modules": [],
            "total_points": 0,
            "streak_days": 0,
            "last_activity": None
        })

        return jsonify(user_progress)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@microlearning_bp.route('/user/<user_id>/complete/<module_id>', methods=['POST'])
def complete_microlearning_module(user_id, module_id):
    """Mark a microlearning module as completed and award points"""
    try:
        # Load module data
        modules = load_microlearning_modules()
        module = modules.get(module_id)

        if not module:
            return jsonify({"error": "Microlearning module not found"}), 404

        # Load user progress
        progress_data = load_user_microlearning_progress()

        if user_id not in progress_data:
            progress_data[user_id] = {
                "user_id": user_id,
                "completed_modules": [],
                "in_progress_modules": [],
                "total_points": 0,
                "streak_days": 0,
                "last_activity": None
            }

        user_progress = progress_data[user_id]

        # Check if already completed
        if module_id in user_progress["completed_modules"]:
            return jsonify({"error": "Module already completed"}), 400

        # Add to completed modules
        completion_record = {
            "module_id": module_id,
            "completed_at": datetime.now().isoformat() + 'Z',
            "points_awarded": module["completion_points"]
        }

        user_progress["completed_modules"].append(completion_record)
        user_progress["total_points"] += module["completion_points"]
        user_progress["last_activity"] = completion_record["completed_at"]

        # Update streak (simplified - in real implementation, check daily activity)
        user_progress["streak_days"] += 1

        # Remove from in-progress if it was there
        user_progress["in_progress_modules"] = [
            m for m in user_progress["in_progress_modules"]
            if m["module_id"] != module_id
        ]

        # Save updated progress
        save_user_microlearning_progress(progress_data)

        return jsonify({
            "success": True,
            "message": "Module completed successfully",
            "points_awarded": module["completion_points"],
            "total_points": user_progress["total_points"],
            "streak_days": user_progress["streak_days"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@microlearning_bp.route('/user/<user_id>/start/<module_id>', methods=['POST'])
def start_microlearning_module(user_id, module_id):
    """Mark a microlearning module as started"""
    try:
        # Load module data
        modules = load_microlearning_modules()
        module = modules.get(module_id)

        if not module:
            return jsonify({"error": "Microlearning module not found"}), 404

        # Load user progress
        progress_data = load_user_microlearning_progress()

        if user_id not in progress_data:
            progress_data[user_id] = {
                "user_id": user_id,
                "completed_modules": [],
                "in_progress_modules": [],
                "total_points": 0,
                "streak_days": 0,
                "last_activity": None
            }

        user_progress = progress_data[user_id]

        # Check if already completed or in progress
        if module_id in [m["module_id"] for m in user_progress["completed_modules"]]:
            return jsonify({"error": "Module already completed"}), 400

        if module_id in [m["module_id"] for m in user_progress["in_progress_modules"]]:
            return jsonify({"error": "Module already in progress"}), 400

        # Add to in-progress modules
        progress_record = {
            "module_id": module_id,
            "started_at": datetime.now().isoformat() + 'Z'
        }

        user_progress["in_progress_modules"].append(progress_record)

        # Save updated progress
        save_user_microlearning_progress(progress_data)

        return jsonify({
            "success": True,
            "message": "Module started successfully",
            "module": module
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@microlearning_bp.route('/user/<user_id>/recommendations', methods=['GET'])
def get_personalized_microlearning(user_id):
    """Get personalized microlearning recommendations for user"""
    try:
        # Load user progress
        progress_data = load_user_microlearning_progress()
        user_progress = progress_data.get(user_id, {})

        completed_modules = user_progress.get("completed_modules", [])
        completed_ids = [m["module_id"] for m in completed_modules]

        # Load all modules
        modules = load_microlearning_modules()

        # Get user's learning preferences (from profile if available)
        # For now, recommend based on completion history
        completed_categories = set()
        for module_id in completed_ids:
            if module_id in modules:
                completed_categories.add(modules[module_id]["category"])

        # Recommend modules from completed categories or general recommendations
        recommendations = []
        for module_id, module in modules.items():
            if module_id not in completed_ids:
                # Prioritize modules from categories user has engaged with
                priority = "medium"
                if module["category"] in completed_categories:
                    priority = "high"
                elif len(completed_modules) == 0:  # New user
                    priority = "high" if module["difficulty"] == "beginner" else "low"

                recommendations.append({
                    "module": module,
                    "priority": priority,
                    "reason": f"Based on your interest in {module['category']}" if priority == "high" else "Recommended for you"
                })

        # Sort by priority and return top recommendations
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order[x["priority"]])

        return jsonify({
            "recommendations": recommendations[:10],  # Top 10
            "total_available": len(modules) - len(completed_ids)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@microlearning_bp.route('/leaderboard/daily', methods=['GET'])
def get_daily_leaderboard():
    """Get daily microlearning leaderboard"""
    try:
        progress_data = load_user_microlearning_progress()
        users_data = _read_json(get_data_file_path('users.json'), {})

        # Calculate daily scores (simplified - in real implementation, track daily activity)
        leaderboard = []

        for user_id, progress in progress_data.items():
            # Find user details
            user_info = None
            for email, user in users_data.items():
                if user.get('user_id') == user_id:
                    user_info = {
                        "name": user.get('name', 'Unknown'),
                        "department": user.get('profile', {}).get('department', 'Unknown')
                    }
                    break

            if user_info:
                # Calculate daily score (modules completed today * points)
                today_completed = 0
                today_points = 0
                today = datetime.now().date().isoformat()

                for completion in progress.get("completed_modules", []):
                    if completion["completed_at"].startswith(today):
                        today_completed += 1
                        today_points += completion["points_awarded"]

                if today_completed > 0:
                    leaderboard.append({
                        "user_id": user_id,
                        "name": user_info["name"],
                        "department": user_info["department"],
                        "modules_completed": today_completed,
                        "points_earned": today_points,
                        "streak_days": progress.get("streak_days", 0)
                    })

        # Sort by points earned today
        leaderboard.sort(key=lambda x: x["points_earned"], reverse=True)

        return jsonify({
            "leaderboard": leaderboard[:20],  # Top 20
            "date": today
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
