from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime
from ..services.ai_recommendations import AIRecommendationsService

recommendation_bp = Blueprint('recommendation', __name__)

def load_json(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data', filename)
    with open(path, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data', filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

@recommendation_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id')
    min_conf = float(request.args.get('min_confidence', 0.0))
    now = datetime.utcnow().isoformat() + 'Z'
    recs = load_json('Recommendation.json')
    filtered = []
    for r in recs:
        attr = r['attributes']
        if attr['user_id'] != user_id:
            continue
        if attr.get('expires_at') and attr['expires_at'] < now:
            continue
        if attr.get('confidence_score', 0) < min_conf:
            continue
        if attr.get('dismissed', False):
            continue
        filtered.append(attr)
    return jsonify(filtered)

@recommendation_bp.route('/ai-recommendations/<user_id>', methods=['GET'])
def get_ai_recommendations(user_id):
    """
    Get AI-powered personalized recommendations for a user
    """
    try:
        # Initialize AI recommendations service
        ai_service = AIRecommendationsService()

        # Generate recommendations
        recommendations = ai_service.generate_recommendations(user_id)

        return jsonify({
            'success': True,
            'data': recommendations
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate AI recommendations: {str(e)}'
        }), 500

@recommendation_bp.route('/ai-recommendations/<user_id>/learning-data', methods=['GET'])
def get_user_learning_data(user_id):
    """
    Get comprehensive learning data for a user (for debugging/analysis)
    """
    try:
        # Initialize AI recommendations service
        ai_service = AIRecommendationsService()

        # Get user learning data
        learning_data = ai_service.get_user_learning_data(user_id)

        return jsonify({
            'success': True,
            'data': learning_data
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get learning data: {str(e)}'
        }), 500
