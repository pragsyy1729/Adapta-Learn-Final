from flask import Blueprint, jsonify, request
import json
from datetime import datetime
from ..services.data_access import get_data_file_path, _read_json, _write_json

recommendations_bp = Blueprint('recommendations', __name__)

def load_recommendations():
    """Load recommendations data"""
    path = get_data_file_path('recommendations.json')
    return _read_json(path, {
        "AI_RECOMMENDATIONS": {},
        "HR_RECOMMENDATIONS": {},
        "ADMIN_RECOMMENDATIONS": {}
    })

def save_recommendations(data):
    """Save recommendations data"""
    path = get_data_file_path('recommendations.json')
    _write_json(path, data)

def load_users():
    """Load users data"""
    path = get_data_file_path('users.json')
    return _read_json(path, {})

@recommendations_bp.route('/user/<user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """Get all recommendations for a user (AI, HR, Admin)"""
    try:
        recommendations_data = load_recommendations()

        # Get recommendations from all sources
        ai_recs = recommendations_data.get("AI_RECOMMENDATIONS", {}).get(user_id, [])
        hr_recs = recommendations_data.get("HR_RECOMMENDATIONS", {}).get(user_id, [])
        admin_recs = recommendations_data.get("ADMIN_RECOMMENDATIONS", {}).get(user_id, [])

        # Combine and sort by priority
        all_recommendations = []

        for rec in ai_recs:
            rec['source'] = 'ai'
            all_recommendations.append(rec)

        for rec in hr_recs:
            rec['source'] = 'hr'
            all_recommendations.append(rec)

        for rec in admin_recs:
            rec['source'] = 'admin'
            all_recommendations.append(rec)

        # Sort by priority (high > medium > low)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_recommendations.sort(key=lambda x: (
            priority_order.get(x.get('priority', 'low'), 2),
            x.get('generated_at', ''),  # Newer first
        ), reverse=True)

        # Group by source for easier frontend handling
        grouped_recommendations = {
            'ai': [rec for rec in all_recommendations if rec['source'] == 'ai'],
            'hr': [rec for rec in all_recommendations if rec['source'] == 'hr'],
            'admin': [rec for rec in all_recommendations if rec['source'] == 'admin'],
            'all': all_recommendations
        }

        return jsonify({
            'recommendations': grouped_recommendations,
            'total_count': len(all_recommendations),
            'counts_by_source': {
                'ai': len(ai_recs),
                'hr': len(hr_recs),
                'admin': len(admin_recs)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/user/<user_id>/ai', methods=['GET'])
def get_ai_recommendations(user_id):
    """Get AI-generated recommendations for a user"""
    try:
        recommendations_data = load_recommendations()
        ai_recs = recommendations_data.get("AI_RECOMMENDATIONS", {}).get(user_id, [])

        return jsonify({
            'recommendations': ai_recs,
            'count': len(ai_recs)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/user/<user_id>/hr', methods=['GET'])
def get_hr_recommendations(user_id):
    """Get HR recommendations for a user"""
    try:
        recommendations_data = load_recommendations()
        hr_recs = recommendations_data.get("HR_RECOMMENDATIONS", {}).get(user_id, [])

        return jsonify({
            'recommendations': hr_recs,
            'count': len(hr_recs)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/user/<user_id>/admin', methods=['GET'])
def get_admin_recommendations(user_id):
    """Get Admin recommendations for a user"""
    try:
        recommendations_data = load_recommendations()
        admin_recs = recommendations_data.get("ADMIN_RECOMMENDATIONS", {}).get(user_id, [])

        return jsonify({
            'recommendations': admin_recs,
            'count': len(admin_recs)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/hr/add', methods=['POST'])
def add_hr_recommendation():
    """Add HR recommendation (HR only)"""
    try:
        data = request.get_json()
        required_fields = ['user_id', 'title', 'description', 'content_id', 'content_type', 'assigned_by']

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        recommendations_data = load_recommendations()

        if "HR_RECOMMENDATIONS" not in recommendations_data:
            recommendations_data["HR_RECOMMENDATIONS"] = {}

        if data['user_id'] not in recommendations_data["HR_RECOMMENDATIONS"]:
            recommendations_data["HR_RECOMMENDATIONS"][data['user_id']] = []

        # Generate recommendation ID
        rec_id = f"hr_rec_{data['user_id']}_{str(len(recommendations_data['HR_RECOMMENDATIONS'][data['user_id']]) + 1)}"

        recommendation = {
            "id": rec_id,
            "type": data.get('type', 'general'),
            "title": data['title'],
            "description": data['description'],
            "reason": data.get('reason', ''),
            "priority": data.get('priority', 'medium'),
            "content_id": data['content_id'],
            "content_type": data['content_type'],
            "assigned_by": data['assigned_by'],
            "due_date": data.get('due_date'),
            "generated_at": datetime.now().isoformat() + 'Z'
        }

        recommendations_data["HR_RECOMMENDATIONS"][data['user_id']].append(recommendation)
        save_recommendations(recommendations_data)

        return jsonify({
            "success": True,
            "message": "HR recommendation added successfully",
            "recommendation": recommendation
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/admin/add', methods=['POST'])
def add_admin_recommendation():
    """Add Admin recommendation (Admin only)"""
    try:
        data = request.get_json()
        required_fields = ['user_id', 'title', 'description', 'content_id', 'content_type', 'assigned_by']

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        recommendations_data = load_recommendations()

        if "ADMIN_RECOMMENDATIONS" not in recommendations_data:
            recommendations_data["ADMIN_RECOMMENDATIONS"] = {}

        if data['user_id'] not in recommendations_data["ADMIN_RECOMMENDATIONS"]:
            recommendations_data["ADMIN_RECOMMENDATIONS"][data['user_id']] = []

        # Generate recommendation ID
        rec_id = f"admin_rec_{data['user_id']}_{str(len(recommendations_data['ADMIN_RECOMMENDATIONS'][data['user_id']]) + 1)}"

        recommendation = {
            "id": rec_id,
            "type": data.get('type', 'general'),
            "title": data['title'],
            "description": data['description'],
            "reason": data.get('reason', ''),
            "priority": data.get('priority', 'medium'),
            "content_id": data['content_id'],
            "content_type": data['content_type'],
            "assigned_by": data['assigned_by'],
            "target_audience": data.get('target_audience'),
            "generated_at": datetime.now().isoformat() + 'Z'
        }

        recommendations_data["ADMIN_RECOMMENDATIONS"][data['user_id']].append(recommendation)
        save_recommendations(recommendations_data)

        return jsonify({
            "success": True,
            "message": "Admin recommendation added successfully",
            "recommendation": recommendation
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/ai/generate/<user_id>', methods=['POST'])
def generate_ai_recommendations(user_id):
    """Generate AI recommendations for a user (simulated)"""
    try:
        # In a real implementation, this would call an AI service
        # For now, we'll simulate AI recommendation generation

        # Load user data to understand their profile
        users_data = load_users()
        user_profile = None

        for email, user in users_data.items():
            if user.get('user_id') == user_id:
                user_profile = user
                break

        if not user_profile:
            return jsonify({"error": "User not found"}), 404

        # Simulate AI analysis based on user profile
        department = user_profile.get('profile', {}).get('department', '')
        role = user_profile.get('profile', {}).get('role', '')

        # Generate recommendations based on department and role
        ai_recommendations = []

        if department == 'Data Science':
            ai_recommendations.append({
                "id": f"ai_rec_{user_id}_ds_001",
                "type": "skill_development",
                "title": "Advanced Machine Learning Techniques",
                "description": "Deep dive into advanced ML algorithms and their applications",
                "reason": f"Based on your role as {role} in {department}, advanced ML skills would enhance your career progression",
                "priority": "high",
                "content_id": "LP_ML_ADV_001",
                "content_type": "learning_path",
                "confidence_score": 0.88,
                "generated_at": datetime.now().isoformat() + 'Z'
            })

        # Add general recommendations
        ai_recommendations.append({
            "id": f"ai_rec_{user_id}_general_001",
            "type": "microlearning",
            "title": "Daily Skill Building",
            "description": "Short, focused learning sessions to build skills incrementally",
            "reason": "Your learning pattern suggests you benefit from frequent, short learning sessions",
            "priority": "medium",
            "content_id": "MICRO_DAILY_001",
            "content_type": "microlearning",
            "confidence_score": 0.75,
            "generated_at": datetime.now().isoformat() + 'Z'
        })

        # Save AI recommendations
        recommendations_data = load_recommendations()

        if "AI_RECOMMENDATIONS" not in recommendations_data:
            recommendations_data["AI_RECOMMENDATIONS"] = {}

        recommendations_data["AI_RECOMMENDATIONS"][user_id] = ai_recommendations
        save_recommendations(recommendations_data)

        return jsonify({
            "success": True,
            "message": "AI recommendations generated successfully",
            "recommendations": ai_recommendations,
            "count": len(ai_recommendations)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/user/<user_id>/interaction/<recommendation_id>', methods=['POST'])
def track_recommendation_interaction(user_id, recommendation_id):
    """Track user interaction with a recommendation"""
    try:
        data = request.get_json()
        interaction_type = data.get('interaction_type')  # viewed, clicked, started, completed, dismissed

        if not interaction_type:
            return jsonify({"error": "interaction_type is required"}), 400

        # In a real implementation, this would be saved to a separate interactions table
        # For now, we'll just acknowledge the interaction

        return jsonify({
            "success": True,
            "message": f"Interaction '{interaction_type}' tracked for recommendation {recommendation_id}",
            "user_id": user_id,
            "recommendation_id": recommendation_id,
            "interaction_type": interaction_type,
            "timestamp": datetime.now().isoformat() + 'Z'
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/analytics', methods=['GET'])
def get_recommendations_analytics():
    """Get analytics about recommendations effectiveness"""
    try:
        # This would analyze recommendation interactions and effectiveness
        # For now, return basic stats

        recommendations_data = load_recommendations()

        total_recommendations = 0
        recommendations_by_source = {
            'ai': 0,
            'hr': 0,
            'admin': 0
        }

        for source_key, source_data in recommendations_data.items():
            if source_key == "AI_RECOMMENDATIONS":
                for user_recs in source_data.values():
                    recommendations_by_source['ai'] += len(user_recs)
                    total_recommendations += len(user_recs)
            elif source_key == "HR_RECOMMENDATIONS":
                for user_recs in source_data.values():
                    recommendations_by_source['hr'] += len(user_recs)
                    total_recommendations += len(user_recs)
            elif source_key == "ADMIN_RECOMMENDATIONS":
                for user_recs in source_data.values():
                    recommendations_by_source['admin'] += len(user_recs)
                    total_recommendations += len(user_recs)

        return jsonify({
            "total_recommendations": total_recommendations,
            "recommendations_by_source": recommendations_by_source,
            "users_with_recommendations": len(set().union(
                *[set(data.keys()) for data in recommendations_data.values() if isinstance(data, dict)]
            ))
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
