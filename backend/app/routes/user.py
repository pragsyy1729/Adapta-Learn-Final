from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime, timedelta
from ..services.data_access import get_data_file_path, _read_json, _write_json

user_bp = Blueprint('user', __name__)

@user_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({"message": "User routes are working!", "timestamp": datetime.now().isoformat()})

@user_bp.route('/debug/learning-rate', methods=['GET'])
def test_learning_rate():
    """Simple test endpoint for learning rate functionality"""
    try:
        return jsonify({
            "message": "Learning rate test endpoint working",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@user_bp.route('/managers', methods=['GET'])
def get_managers():
    """
    Get list of managers, optionally filtered by department
    """
    try:
        department = request.args.get('department')
        users_path = get_data_file_path('users.json')
        users = _read_json(users_path, {})

        managers = []
        for user_key, user in users.items():
            if user.get('roleType') == 'Manager' or user.get('roleType') == 'Hiring Manager':
                if department:
                    profile = user.get('profile', {})
                    if profile.get('department') and profile['department'] != department:
                        continue
                managers.append({
                    'email': user.get('email'),
                    'name': user.get('name'),
                    'department': user.get('profile', {}).get('department', None)
                })

        return jsonify(managers)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@user_bp.route('/managers/list', methods=['GET'])
def get_managers_list():
    """
    Explicit managers list endpoint that returns an envelope { success, data }
    This avoids conflicts with the dynamic '/<user_id>' route in some setups.
    """
    try:
        department = request.args.get('department')
        users_path = get_data_file_path('users.json')
        users = _read_json(users_path, {})

        managers = []
        for user_key, user in users.items():
            if user.get('roleType') == 'Manager' or user.get('roleType') == 'Hiring Manager':
                if department:
                    profile = user.get('profile', {})
                    if profile.get('department') and profile['department'] != department:
                        continue
                managers.append({
                    'email': user.get('email'),
                    'name': user.get('name'),
                    'department': user.get('profile', {}).get('department', None)
                })

        return jsonify({"success": True, "data": managers})

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@user_bp.route('/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    Get user profile information by user ID
    """
    try:
        users_path = get_data_file_path('users.json')
        users = _read_json(users_path, {})

        # Find user by user_id
        user_data = None
        for user_key, user in users.items():
            if user.get('user_id') == user_id:
                user_data = user
                break

        if not user_data:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        # Format user profile data
        profile_data = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name", user_data.get("name", "").split()[0]),
            "last_name": user_data.get("last_name", " ".join(user_data.get("name", "").split()[1:])),
            "department": user_data.get("department", user_data.get("profile", {}).get("department")),
            "role": user_data.get("role", user_data.get("roleType")),
            "profile": {
                "phone": user_data.get("profile", {}).get("phone"),
                "location": user_data.get("profile", {}).get("location"),
                "join_date": user_data.get("profile", {}).get("join_date", user_data.get("created_at")),
                "manager": user_data.get("profile", {}).get("manager"),
                "skills": user_data.get("profile", {}).get("skills", []),
                "certifications": user_data.get("profile", {}).get("certifications", []),
                # Persisted onboarding/profile fields
                "employeeId": user_data.get("profile", {}).get("employeeId"),
                "gender": user_data.get("profile", {}).get("gender"),
                "college": user_data.get("profile", {}).get("college"),
                "latestDegree": user_data.get("profile", {}).get("latestDegree"),
                "cgpa": user_data.get("profile", {}).get("cgpa"),
                "country": user_data.get("profile", {}).get("country"),
                "city": user_data.get("profile", {}).get("city"),
                "profilePicture": user_data.get("profile", {}).get("profilePicture"),
                "disabilities": user_data.get("profile", {}).get("disabilities", [])
            }
        }

        return jsonify(profile_data)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@user_bp.route('/<user_id>/skill-gaps', methods=['GET'])
def get_user_skill_gaps(user_id):
    """
    Get skill gap analysis for a user
    """
    try:
        # Get skill gap analysis data
        skill_gaps_path = get_data_file_path('SkillGapAnalysis.json')
        skill_gaps_data = _read_json(skill_gaps_path, [])

        # Filter skill gaps for the specific user
        user_skill_gaps = []
        for gap in skill_gaps_data:
            if gap.get('user_id') == user_id:
                user_skill_gaps.append({
                    "skill": gap.get("skill_name", ""),
                    "current_level": gap.get("current_level", 1),
                    "required_level": gap.get("required_level", 4),
                    "gap_score": gap.get("gap_score", 0),
                    "progress_percentage": gap.get("progress_percentage", 0),
                    "estimated_completion": gap.get("estimated_completion", "Unknown")
                })

        # If no skill gaps found, return some default data for demonstration
        if not user_skill_gaps:
            # Get user's learning paths to generate skill gap analysis
            learning_paths_path = get_data_file_path('learning_paths.json')
            learning_paths = _read_json(learning_paths_path, {})

            # Mock skill gap data based on common skills
            mock_skills = [
                {"skill": "Python Programming", "current": 2, "required": 4, "progress": 50},
                {"skill": "Data Analysis", "current": 1, "required": 3, "progress": 33},
                {"skill": "Machine Learning", "current": 1, "required": 4, "progress": 25},
                {"skill": "SQL Database", "current": 3, "required": 4, "progress": 75},
                {"skill": "Cloud Computing", "current": 2, "required": 3, "progress": 67}
            ]

            user_skill_gaps = []
            for skill in mock_skills:
                gap_score = skill["required"] - skill["current"]
                user_skill_gaps.append({
                    "skill": skill["skill"],
                    "current_level": skill["current"],
                    "required_level": skill["required"],
                    "gap_score": gap_score,
                    "progress_percentage": skill["progress"],
                    "estimated_completion": f"{gap_score * 2} weeks"
                })

        return jsonify(user_skill_gaps)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@user_bp.route('/<user_id>/learning-rate', methods=['GET'])
def get_user_learning_rate(user_id):
    """
    Get learning rate/completion rate data for a user
    """
    try:
        # Get user's learning path progress
        learning_path_progress_path = get_data_file_path('LearningPathProgress.json')
        progress_data = _read_json(learning_path_progress_path, [])

        # Filter progress for this user
        user_progress = []
        for progress in progress_data:
            if progress.get('attributes', {}).get('user_id') == user_id:
                user_progress.append(progress['attributes'])

        if not user_progress:
            return jsonify({
                "success": False,
                "error": "No learning progress found for user"
            }), 404

        # Calculate learning rate metrics
        total_paths = len(user_progress)
        completed_paths = len([p for p in user_progress if p.get('status') == 'completed'])
        in_progress_paths = len([p for p in user_progress if p.get('status') == 'in_progress'])
        not_started_paths = len([p for p in user_progress if p.get('status') == 'not_started'])

        # Calculate overall completion rate
        total_progress = sum([p.get('progress_percent', 0) for p in user_progress])
        overall_completion_rate = total_progress / total_paths if total_paths > 0 else 0

        # Calculate average time spent
        total_time_spent = sum([p.get('time_invested_minutes', 0) for p in user_progress])
        average_time_per_path = total_time_spent / total_paths if total_paths > 0 else 0

        # Get learning paths data for additional metrics
        learning_paths_path = get_data_file_path('learning_paths.json')
        learning_paths_data = _read_json(learning_paths_path, {})

        # Calculate completion rates by difficulty level
        difficulty_rates = {}
        for progress in user_progress:
            lp_id = progress.get('learning_path_id')
            if lp_id in learning_paths_data:
                lp_data = learning_paths_data[lp_id]
                difficulty = lp_data.get('difficulty_level', 'unknown')
                if difficulty not in difficulty_rates:
                    difficulty_rates[difficulty] = {'completed': 0, 'total': 0}
                difficulty_rates[difficulty]['total'] += 1
                if progress.get('status') == 'completed':
                    difficulty_rates[difficulty]['completed'] += 1

        # Convert to completion rates
        for difficulty, data in difficulty_rates.items():
            if data['total'] > 0:
                data['completion_rate'] = data['completed'] / data['total']
            else:
                data['completion_rate'] = 0

        learning_rate_data = {
            "user_id": user_id,
            "total_learning_paths": total_paths,
            "completed_paths": completed_paths,
            "in_progress_paths": in_progress_paths,
            "not_started_paths": not_started_paths,
            "overall_completion_rate": round(overall_completion_rate, 2),
            "average_time_per_path_minutes": round(average_time_per_path, 2),
            "total_time_invested_minutes": total_time_spent,
            "completion_rate_by_difficulty": difficulty_rates,
            "individual_path_progress": [
                {
                    "learning_path_id": p.get('learning_path_id'),
                    "progress_percent": p.get('progress_percent', 0),
                    "status": p.get('status'),
                    "time_invested_minutes": p.get('time_invested_minutes', 0),
                    "last_accessed_at": p.get('last_accessed_at')
                }
                for p in user_progress
            ]
        }

        return jsonify(learning_rate_data)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    """
    Get learning progress warnings for a user
    """
    try:
        users_path = get_data_file_path('users.json')
        users = _read_json(users_path, {})

        # Find user by user_id
        user_data = None
        for user_key, user in users.items():
            if user.get('user_id') == user_id:
                user_data = user
                break

        if not user_data:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        warnings = []

        # Check if user is a new joiner with no progress
        if user_data.get('newJoiner') == 'Yes':
            created_date = user_data.get('created_at', '')
            if created_date:
                try:
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    days_since_joining = (datetime.now(created_dt.tzinfo) - created_dt).days

                    if days_since_joining > 7:
                        warnings.append({
                            "type": "no_progress",
                            "message": "Welcome! You haven't started your learning journey yet. Begin with your personalized learning path to get started.",
                            "days_since_last_access": days_since_joining
                        })
                except:
                    pass

        # Check for stalled learning (no recent activity)
        profile = user_data.get('profile', {})
        last_updated = profile.get('last_updated')
        if last_updated:
            try:
                last_updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                days_since_update = (datetime.now(last_updated_dt.tzinfo) - last_updated_dt).days

                if days_since_update > 14:
                    warnings.append({
                        "type": "stalled_learning",
                        "message": "It's been a while since your last learning activity. Consider resuming your learning path to maintain progress.",
                        "days_since_last_access": days_since_update
                    })
                elif days_since_update > 7:
                    warnings.append({
                        "type": "slow_progress",
                        "message": "Your learning progress has slowed down. Try dedicating more time to your learning activities.",
                        "days_since_last_access": days_since_update
                    })
            except:
                pass

        # Check learning paths progress
        learning_paths_path = get_data_file_path('learning_paths.json')
        learning_paths = _read_json(learning_paths_path, {})

        # Get user's enrollments
        enrollments = profile.get('enrollments', [])
        for enrollment in enrollments:
            lp_id = enrollment.get('learning_path_id')
            progress = enrollment.get('progress', 0)

            if lp_id and lp_id in learning_paths:
                lp_data = learning_paths[lp_id]
                lp_name = lp_data.get('name', f'Learning Path {lp_id}')

                # Low progress warning
                if progress < 25:
                    warnings.append({
                        "type": "slow_progress",
                        "message": f"You're making slow progress on '{lp_name}'. Consider increasing your study time.",
                        "learning_path_id": lp_id,
                        "learning_path_name": lp_name,
                        "progress_percent": progress
                    })

        # If no warnings found, add a positive message for active learners
        if not warnings and last_updated:
            try:
                last_updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                days_since_update = (datetime.now(last_updated_dt.tzinfo) - last_updated_dt).days

                if days_since_update <= 3:
                    warnings.append({
                        "type": "good_progress",
                        "message": "Great job! You're actively engaged with your learning. Keep up the excellent work!",
                        "days_since_last_access": days_since_update
                    })
            except:
                pass

        return jsonify(warnings)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@user_bp.route('/<user_id>/onboard', methods=['POST'])
def onboard_user(user_id):
    """
    Complete user onboarding: assign default learning paths and learning style materials
    """
    try:
        # Get user data
        users_path = get_data_file_path('users.json')
        users = _read_json(users_path, {})

        if user_id not in users:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = users[user_id]

        # Get user's learning style (from VARK quiz results)
        learning_style = user.get('profile', {}).get('learning_style', 'visual')  # default fallback
        vark_scores = user.get('profile', {}).get('vark_scores', {})

        # Determine top 2 learning styles
        if vark_scores:
            sorted_styles = sorted(vark_scores.items(), key=lambda x: x[1], reverse=True)
            top_styles = [style[0] for style in sorted_styles[:2]]
        else:
            top_styles = [learning_style, 'reading_writing']  # fallback

        # Load default learning paths
        default_paths_path = get_data_file_path('default_learning_paths.json')
        default_paths = _read_json(default_paths_path, {})

        # Load learning materials
        materials_path = get_data_file_path('learning_materials.json')
        learning_materials = _read_json(materials_path, [])

        # Assign default learning paths to user
        assigned_paths = []
        enrollments = []
        for path_id, path_data in default_paths.items():
            # Create progress entry for default learning path
            progress_entry = {
                "attributes": {
                    "id": f"lpp_{user_id}_{path_id}",
                    "user_id": user_id,
                    "learning_path_id": path_id,
                    "status": "not_started",
                    "progress_percent": 0.0,
                    "modules_completed_count": 0,
                    "modules_total_count": len(path_data.get('modules', [])),
                    "time_invested_minutes": 0,
                    "started_at": None,
                    "last_accessed_at": None,
                    "completed_at": None,
                    "enrolled_at": datetime.now().isoformat() + 'Z'
                }
            }

            path_info = {
                "learning_path_id": path_id,
                "title": path_data.get('title'),
                "description": path_data.get('description'),
                "difficulty": path_data.get('difficulty'),
                "duration": path_data.get('duration'),
                "status": "assigned",
                "enrolled_at": datetime.now().isoformat() + 'Z',
                "progress": 0
            }
            assigned_paths.append(path_info)

            # Add to enrollments array
            enrollments.append({
                "learning_path_id": path_id,
                "enrolled_at": datetime.now().isoformat() + 'Z',
                "status": "active",
                "progress": 0
            })

        # Save progress entries
        progress_path = get_data_file_path('LearningPathProgress.json')
        existing_progress = _read_json(progress_path, [])

        # Filter out any existing entries for this user and default paths
        filtered_progress = []
        for progress in existing_progress:
            attrs = progress.get('attributes', {})
            if not (attrs.get('user_id') == user_id and
                   attrs.get('learning_path_id', '').startswith('LP_SOFT_')):
                filtered_progress.append(progress)

        # Add new default path assignments
        for path_data in assigned_paths:
            path_id = path_data['learning_path_id']
            progress_entry = {
                "attributes": {
                    "id": f"lpp_{user_id}_{path_id}",
                    "user_id": user_id,
                    "learning_path_id": path_id,
                    "status": "not_started",
                    "progress_percent": 0.0,
                    "modules_completed_count": 0,
                    "modules_total_count": len(default_paths.get(path_id, {}).get('modules', [])),
                    "time_invested_minutes": 0,
                    "started_at": None,
                    "last_accessed_at": None,
                    "completed_at": None,
                    "enrolled_at": datetime.now().isoformat() + 'Z'
                }
            }
            filtered_progress.append(progress_entry)

        _write_json(progress_path, filtered_progress)

        # Assign learning materials based on top 2 learning styles
        assigned_materials = []
        materials_by_path = {}

        for material in learning_materials:
            path_id = material.get('learning_path_id')
            if path_id in default_paths:  # Only assign materials for default paths
                if path_id not in materials_by_path:
                    materials_by_path[path_id] = []

                # Get materials for top 2 learning styles
                style_materials = []
                for style in top_styles:
                    if style in material.get('materials', {}):
                        style_materials.extend(material['materials'][style])

                if style_materials:
                    materials_by_path[path_id].append({
                        "chapter_id": material.get('chapter_id'),
                        "chapter_title": material.get('title'),
                        "materials": style_materials,
                        "learning_objectives": material.get('learning_objectives', []),
                        "estimated_time": material.get('estimated_time')
                    })

        # Update user's profile with assigned materials
        user['profile']['assigned_materials'] = materials_by_path
        user['profile']['learning_styles'] = top_styles
        user['profile']['onboarding_completed'] = True
        user['profile']['onboarding_date'] = datetime.now().isoformat() + 'Z'
        user['profile']['enrollments'] = enrollments

        # Save updated user data
        _write_json(users_path, users)

        result = {
            "success": True,
            "message": "User onboarding completed successfully",
            "user_id": user_id,
            "assigned_learning_paths": assigned_paths,
            "learning_styles": top_styles,
            "assigned_materials": materials_by_path,
            "onboarding_summary": {
                "default_paths_assigned": len(assigned_paths),
                "learning_styles_detected": top_styles,
                "materials_prepared": sum(len(materials) for materials in materials_by_path.values())
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@user_bp.route('/<user_id>/learning-materials', methods=['GET'])
def get_user_learning_materials(user_id):
    """
    Get learning materials tailored to user's learning style
    """
    try:
        # Get user data
        users_path = get_data_file_path('users.json')
        users = _read_json(users_path, {})

        if user_id not in users:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = users[user_id]
        profile = user.get('profile', {})

        # Get assigned materials
        assigned_materials = profile.get('assigned_materials', {})
        learning_styles = profile.get('learning_styles', [])

        # Get learning path progress to show current status
        progress_path = get_data_file_path('LearningPathProgress.json')
        progress_data = _read_json(progress_path, [])

        user_progress = {}
        for progress in progress_data:
            attrs = progress.get('attributes', {})
            if attrs.get('user_id') == user_id:
                lp_id = attrs.get('learning_path_id')
                user_progress[lp_id] = {
                    "progress_percent": attrs.get('progress_percent', 0),
                    "status": attrs.get('status', 'not_started'),
                    "last_accessed_at": attrs.get('last_accessed_at')
                }

        # Load default learning paths for metadata
        default_paths_path = get_data_file_path('default_learning_paths.json')
        default_paths = _read_json(default_paths_path, {})

        # Structure response
        materials_response = []
        for path_id, materials in assigned_materials.items():
            path_data = default_paths.get(path_id, {})
            progress_info = user_progress.get(path_id, {})

            materials_response.append({
                "learning_path_id": path_id,
                "learning_path_title": path_data.get('title', 'Unknown Path'),
                "progress": progress_info,
                "chapters": materials,
                "learning_styles_used": learning_styles
            })

        return jsonify({
            "user_id": user_id,
            "learning_styles": learning_styles,
            "materials": materials_response
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
