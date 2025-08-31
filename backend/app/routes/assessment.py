from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime

assessment_bp = Blueprint('assessment', __name__)

def load_json(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data', filename)
    with open(path, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data', filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def is_assessment_locked(assessment, user_id):
    """Check if assessment is locked based on unlock rules."""
    unlock_rule = assessment.get('unlock_rule')
    if not unlock_rule:
        return False
    
    # Simple check - if it mentions completing an assessment, check attempts
    if 'Complete React Fundamentals Assessment' in unlock_rule:
        attempts = load_json('AssessmentAttempt.json')
        for attempt in attempts:
            attr = attempt['attributes']
            if (attr['user_id'] == user_id and 
                attr['assessment_id'] == 'asmt-001' and 
                attr['status'] == 'graded'):
                return False
        return True
    
    return False

@assessment_bp.route('/assessments', methods=['GET'])
def get_assessments():
    user_id = request.args.get('user_id')
    assessment_type = request.args.get('type')
    now = datetime.utcnow().isoformat() + 'Z'
    assessments = load_json('Assessment.json')
    attempts = load_json('AssessmentAttempt.json')
    result = []
    
    if assessment_type == 'learning_style':
        # Only fetch learning style assessments
        learning_style_assessments = [a for a in assessments if a['attributes'].get('assessment_type') == 'learning_style']
        for a in learning_style_assessments:
            attr = a['attributes']
            user_attempts = [att['attributes'] for att in attempts if att['attributes']['assessment_id'] == attr['id'] and att['attributes']['user_id'] == user_id]
            # Get the latest attempt
            if user_attempts:
                latest = max(user_attempts, key=lambda x: x.get('started_at', ''))
                attr = attr.copy()
                attr['last_result'] = latest.get('learning_style_category')
                attr['last_attempt'] = latest
                result.append(attr)
        return jsonify(result)
    
    # Show upcoming assessments within availability window
    for a in assessments:
        attr = a['attributes']
        avail = attr.get('availability_window', {})
        start_at = avail.get('start_at')
        end_at = avail.get('end_at')
        
        # Check availability window
        if start_at and now < start_at:
            continue
        if end_at and now > end_at:
            continue
        
        user_attempts = [att['attributes'] for att in attempts if att['attributes']['assessment_id'] == attr['id'] and att['attributes']['user_id'] == user_id]
        
        # Check if user has reached max attempts
        attempts_allowed = attr.get('attempts_allowed')
        if attempts_allowed and len(user_attempts) >= attempts_allowed:
            continue
        
        # Check if user has a completed attempt (for single-attempt assessments)
        has_completed = any(
            attempt['status'] in ['graded', 'submitted'] 
            for attempt in user_attempts
        )
        if has_completed and attempts_allowed == 1:
            continue
        
        # Check if assessment is locked
        is_locked = is_assessment_locked(attr, user_id)
        
        # Check if user has an in-progress attempt
        in_progress_attempt = next(
            (attempt for attempt in user_attempts if attempt['status'] == 'in_progress'),
            None
        )
        
        attr = attr.copy()
        attr['attempts'] = user_attempts
        attr['attempts_used'] = len(user_attempts)
        attr['is_locked'] = is_locked
        attr['can_start'] = not in_progress_attempt and not is_locked
        attr['has_in_progress'] = in_progress_attempt is not None
        attr['in_progress_attempt_id'] = in_progress_attempt['id'] if in_progress_attempt else None
        
        result.append(attr)
    
    return jsonify(result)

@assessment_bp.route('/assessment-attempts', methods=['POST'])
def start_assessment_attempt():
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    assessment_id = data.get('assessment_id')
    learning_style_category = data.get('learning_style_category')
    
    if not user_id or not assessment_id:
        return jsonify({'error': 'user_id and assessment_id required'}), 400
    
    # Load assessments and check if assessment exists
    assessments = load_json('Assessment.json')
    assessment = None
    for a in assessments:
        if a['attributes']['id'] == assessment_id:
            assessment = a['attributes']
            break
    
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404
    
    # Check availability window
    now = datetime.utcnow().isoformat() + 'Z'
    avail = assessment.get('availability_window', {})
    start_at = avail.get('start_at')
    end_at = avail.get('end_at')
    
    if start_at and now < start_at:
        return jsonify({'error': 'Assessment is not yet available'}), 403
    if end_at and now > end_at:
        return jsonify({'error': 'Assessment availability window has expired'}), 403
    
    # Check if assessment is locked
    if is_assessment_locked(assessment, user_id):
        return jsonify({'error': 'Assessment is locked. Complete prerequisites first.'}), 403
    
    attempts = load_json('AssessmentAttempt.json')
    user_attempts = [att['attributes'] for att in attempts if att['attributes']['assessment_id'] == assessment_id and att['attributes']['user_id'] == user_id]
    
    # Check if already in progress
    for att in user_attempts:
        if att['status'] == 'in_progress':
            return jsonify({'error': 'Attempt already in progress'}), 400
    
    # Check attempts limit
    attempts_allowed = assessment.get('attempts_allowed')
    if attempts_allowed and len(user_attempts) >= attempts_allowed:
        return jsonify({'error': 'Maximum attempts reached for this assessment'}), 403
    
    from uuid import uuid4
    new_attempt = {
        'attributes': {
            'id': str(uuid4()),
            'assessment_id': assessment_id,
            'user_id': user_id,
            'status': 'in_progress',
            'started_at': now,
            'submitted_at': None,
            'graded_at': None,
            'raw_score': None,
            'score_percent': None,
            'duration_seconds': 0,
            'response_blob': {},
            'feedback': None,
            'attempt_number': len(user_attempts) + 1,
            'version_taken': assessment.get('version', 1)
        }
    }
    
    if learning_style_category:
        new_attempt['attributes']['learning_style_category'] = learning_style_category
    
    attempts.append(new_attempt)
    save_json('AssessmentAttempt.json', attempts)
    
    return jsonify({
        'success': True,
        'attempt': new_attempt,
        'message': 'Assessment attempt started successfully'
    }), 201
