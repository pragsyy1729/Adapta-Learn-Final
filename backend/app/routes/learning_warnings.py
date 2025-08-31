from flask import Blueprint, jsonify
import json
from datetime import datetime, timedelta, timezone
from ..services.data_access import get_data_file_path

learning_warnings_bp = Blueprint('learning_warnings', __name__)

# File paths
LEARNING_PATH_PROGRESS_FILE = get_data_file_path('LearningPathProgress.json')
LEARNING_PATHS_FILE = get_data_file_path('learning_paths.json')

def load_learning_path_progress():
    """Load learning path progress data"""
    try:
        with open(LEARNING_PATH_PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_learning_paths():
    """Load learning paths data"""
    try:
        with open(LEARNING_PATHS_FILE, 'r') as f:
            data = json.load(f)
            # Convert object format to array format for easier processing
            if isinstance(data, dict):
                return {"learning_paths": list(data.values())}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"learning_paths": []}

def analyze_learning_progress(user_id: str):
    """Analyze user's learning progress and generate warnings"""
    progress_data = load_learning_path_progress()
    learning_paths_data = load_learning_paths()

    # Create lookup for learning paths
    learning_paths_lookup = {}
    for lp in learning_paths_data.get("learning_paths", []):
        learning_paths_lookup[lp["id"]] = lp

    warnings = []
    now = datetime.now(timezone.utc)

    # Filter progress for this user
    user_progress = [p for p in progress_data if p.get("attributes", {}).get("user_id") == user_id]

    for progress in user_progress:
        attrs = progress.get("attributes", {})
        status = attrs.get("status", "")
        progress_percent = attrs.get("progress_percent", 0)
        last_accessed = attrs.get("last_accessed_at")
        started_at = attrs.get("started_at")
        learning_path_id = attrs.get("learning_path_id")

        # Get learning path name
        lp_name = "Unknown Learning Path"
        if learning_path_id in learning_paths_lookup:
            lp_name = learning_paths_lookup[learning_path_id].get("title", lp_name)

        # Check for stalled learning (no progress for 7+ days)
        if last_accessed and status == "in_progress":
            try:
                # Parse the ISO datetime string and make it timezone-aware
                try:
                    if last_accessed.endswith('Z'):
                        last_accessed_date = datetime.fromisoformat(last_accessed[:-1]).replace(tzinfo=timezone.utc)
                    else:
                        last_accessed_date = datetime.fromisoformat(last_accessed)
                        # If no timezone info, assume UTC
                        if last_accessed_date.tzinfo is None:
                            last_accessed_date = last_accessed_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    # Fallback to strptime for different formats
                    if last_accessed.endswith('Z'):
                        last_accessed_date = datetime.strptime(last_accessed, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                    else:
                        last_accessed_date = datetime.strptime(last_accessed, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                
                # Make current time timezone-aware for comparison
                now_aware = datetime.now(timezone.utc)
                days_since_access = (now_aware - last_accessed_date).days

                if days_since_access >= 7:
                    warnings.append({
                        "type": "stalled_learning",
                        "message": f"You haven't accessed '{lp_name}' for {days_since_access} days. Consider resuming your learning to stay on track.",
                        "learning_path_id": learning_path_id,
                        "learning_path_name": lp_name,
                        "days_since_last_access": days_since_access,
                        "progress_percent": progress_percent
                    })
            except (ValueError, TypeError, OSError) as e:
                # Skip this warning if date parsing fails
                continue

        # Check for slow progress (started but low progress after significant time)
        if started_at and status == "in_progress" and progress_percent < 25:
            try:
                # Parse the ISO datetime string and make it timezone-aware
                try:
                    if started_at.endswith('Z'):
                        started_date = datetime.fromisoformat(started_at[:-1]).replace(tzinfo=timezone.utc)
                    else:
                        started_date = datetime.fromisoformat(started_at)
                        # If no timezone info, assume UTC
                        if started_date.tzinfo is None:
                            started_date = started_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    # Fallback to strptime for different formats
                    if started_at.endswith('Z'):
                        started_date = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                    else:
                        started_date = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                
                # Make current time timezone-aware for comparison
                now_aware = datetime.now(timezone.utc)
                days_since_start = (now_aware - started_date).days

                if days_since_start >= 14:  # 2 weeks with less than 25% progress
                    warnings.append({
                        "type": "slow_progress",
                        "message": f"Your progress on '{lp_name}' seems slow. You've been working on it for {days_since_start} days but only completed {progress_percent}%.",
                        "learning_path_id": learning_path_id,
                        "learning_path_name": lp_name,
                        "days_since_start": days_since_start,
                        "progress_percent": progress_percent
                    })
            except (ValueError, TypeError, OSError) as e:
                # Skip this warning if date parsing fails
                continue

        # Check for no progress (not started learning paths)
        if status == "not_started" and started_at is None:
            warnings.append({
                "type": "no_progress",
                "message": f"You haven't started '{lp_name}' yet. Begin your learning journey to build new skills!",
                "learning_path_id": learning_path_id,
                "learning_path_name": lp_name,
                "progress_percent": progress_percent
            })

    return warnings

@learning_warnings_bp.route('/learning-warnings/<user_id>', methods=['GET'])
def get_learning_warnings(user_id):
    """Get learning progress warnings for a user"""
    try:
        warnings = analyze_learning_progress(user_id)
        return jsonify(warnings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
