from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime
import uuid

enrollment_bp = Blueprint('enrollment', __name__)

def load_json(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data', filename)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(filename, data):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data', filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

@enrollment_bp.route('/enroll', methods=['POST'])
def enroll_user_in_learning_path():
    """Enroll a user in a learning path by creating a progress entry"""
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    learning_path_id = data.get('learning_path_id')
    
    if not user_id or not learning_path_id:
        return jsonify({'error': 'user_id and learning_path_id are required'}), 400
    
    # Load existing progress data
    progress_list = load_json('LearningPathProgress.json')
    if not isinstance(progress_list, list):
        progress_list = []
    
    # Check if user is already enrolled in this learning path
    existing_enrollment = any(
        p.get('attributes', {}).get('user_id') == user_id and 
        p.get('attributes', {}).get('learning_path_id') == learning_path_id
        for p in progress_list
    )
    
    if existing_enrollment:
        return jsonify({'error': 'User is already enrolled in this learning path'}), 400
    
    # Load learning path details to get module information
    learning_paths = load_json('learning_paths.json')
    modules = load_json('Module.json')
    
    # Find the learning path
    learning_path = learning_paths.get(learning_path_id)
    if not learning_path:
        return jsonify({'error': 'Learning path not found'}), 404
    
    # Count total modules for this learning path
    path_modules = [m for m in modules if m.get('attributes', {}).get('learning_path_id') == learning_path_id]
    total_modules = len(path_modules)
    
    # Create new progress entry
    new_progress = {
        'attributes': {
            'id': f"lpp-{len(progress_list) + 1:03d}",
            'user_id': user_id,
            'learning_path_id': learning_path_id,
            'status': 'not_started',
            'progress_percent': 0.0,
            'modules_completed_count': 0,
            'modules_total_count': total_modules,
            'time_invested_minutes': 0,
            'estimated_completion_weeks': learning_path.get('duration', '12 weeks').replace(' weeks', ''),
            'current_module_id': None,
            'enrolled_at': datetime.now().isoformat() + 'Z',
            'started_at': None,
            'last_accessed_at': None,
            'completed_at': None,
            'difficulty_level': learning_path.get('difficulty', 'Beginner'),
            'tags': learning_path.get('tags', [])
        }
    }
    
    # Add to progress list
    progress_list.append(new_progress)
    
    # Save updated progress
    save_json('LearningPathProgress.json', progress_list)
    
    return jsonify({
        'success': True, 
        'message': f'User {user_id} enrolled in learning path {learning_path_id}',
        'progress_id': new_progress['attributes']['id']
    })

@enrollment_bp.route('/auto-enroll-from-onboarding', methods=['POST'])
def auto_enroll_from_onboarding():
    """Auto-enroll user in learning paths based on onboarding recommendations"""
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # Load onboarding recommendations
    onboarding_recs = load_json('onboarding_recommendations.json')
    
    # Find recommendations for this user
    user_recommendations = onboarding_recs.get('recommendations', {}).get(user_id)
    if not user_recommendations:
        return jsonify({'error': f'No onboarding recommendations found for user {user_id}'}), 404
    
    # Get recommended learning paths
    recommended_paths = user_recommendations.get('recommended_learning_paths', [])
    
    # Handle empty recommendations with fallback strategy
    if not recommended_paths:
        print(f"⚠️ No learning paths recommended for {user_id}, attempting fallback strategy...")
        
        # Fallback 1: Try to infer from department
        user_department = user_recommendations.get('department', '')
        user_role = user_recommendations.get('role', '')
        
        # Department mapping for fallback
        department_mapping = {
            'engineering': 'ENG2024001',
            'ENG2024001': 'ENG2024001',
            'data_science': 'DS2024001', 
            'DS2024001': 'DS2024001'
        }
        
        # Default learning paths by department
        fallback_paths = {
            'ENG2024001': ['LP2024ENG001'],
            'DS2024001': ['LP2024DS001']
        }
        
        # Try to map old department to new format
        mapped_department = department_mapping.get(user_department)
        if mapped_department and mapped_department in fallback_paths:
            recommended_paths = fallback_paths[mapped_department]
            print(f"✅ Fallback: Assigned default paths for department {mapped_department}: {recommended_paths}")
        else:
            # Final fallback: assign basic engineering path for associates/learners
            if user_role and 'associate' in user_role.lower():
                recommended_paths = ['LP2024ENG001']  # Default to React Development Track
                print(f"✅ Final fallback: Assigned default engineering path for {user_role}")
            else:
                return jsonify({
                    'error': f'No learning paths available for user {user_id}',
                    'details': f'Department: {user_department}, Role: {user_role}',
                    'suggestion': 'Contact administrator to assign learning paths manually'
                }), 400
    
    # Enroll user in each recommended learning path
    enrolled_paths = []
    errors = []
    
    for path_id in recommended_paths:
        try:
            # Use the existing enroll endpoint logic
            # Load existing progress data
            progress_list = load_json('LearningPathProgress.json')
            if not isinstance(progress_list, list):
                progress_list = []
            
            # Check if already enrolled
            existing_enrollment = any(
                p.get('attributes', {}).get('user_id') == user_id and 
                p.get('attributes', {}).get('learning_path_id') == path_id
                for p in progress_list
            )
            
            if existing_enrollment:
                print(f"ℹ️ User {user_id} already enrolled in {path_id}, skipping...")
                continue  # Skip if already enrolled
            
            # Load learning path details
            learning_paths = load_json('learning_paths.json')
            modules = load_json('Module.json')
            
            # Find the learning path
            learning_path = learning_paths.get(path_id)
            if not learning_path:
                errors.append(f'Learning path {path_id} not found')
                continue
            
            # Count total modules for this learning path
            path_modules = [m for m in modules if m.get('attributes', {}).get('learning_path_id') == path_id]
            total_modules = len(path_modules)
            
            # Create new progress entry
            new_progress = {
                'attributes': {
                    'id': f"lpp-{len(progress_list) + 1:03d}",
                    'user_id': user_id,
                    'learning_path_id': path_id,
                    'status': 'not_started',
                    'progress_percent': 0.0,
                    'modules_completed_count': 0,
                    'modules_total_count': total_modules,
                    'time_invested_minutes': 0,
                    'estimated_completion_weeks': learning_path.get('duration', '12 weeks').replace(' weeks', ''),
                    'current_module_id': None,
                    'enrolled_at': datetime.now().isoformat() + 'Z',
                    'started_at': None,
                    'last_accessed_at': None,
                    'completed_at': None,
                    'difficulty_level': learning_path.get('difficulty', 'Beginner'),
                    'tags': learning_path.get('tags', [])
                }
            }
            
            # Add to progress list
            progress_list.append(new_progress)
            
            # Save updated progress
            save_json('LearningPathProgress.json', progress_list)
            
            enrolled_paths.append({
                'learning_path_id': path_id,
                'learning_path_title': learning_path.get('title', 'Unknown'),
                'progress_id': new_progress['attributes']['id']
            })
            
        except Exception as e:
            errors.append(f'Failed to enroll in {path_id}: {str(e)}')
    
    result = {
        'success': len(enrolled_paths) > 0,
        'enrolled_paths': enrolled_paths,
        'total_enrolled': len(enrolled_paths)
    }
    
    if errors:
        result['errors'] = errors
        
    return jsonify(result)

@enrollment_bp.route('/user/<user_id>/enrolled-paths', methods=['GET'])
def get_user_enrolled_paths(user_id):
    """Get all learning paths a user is enrolled in"""
    progress_list = load_json('LearningPathProgress.json')
    if not isinstance(progress_list, list):
        progress_list = []
    
    # Find all enrollments for this user
    user_enrollments = [
        p['attributes'] for p in progress_list 
        if p.get('attributes', {}).get('user_id') == user_id
    ]
    
    # Load learning path details
    learning_paths = load_json('learning_paths.json')
    
    # Enhance enrollments with learning path details
    enhanced_enrollments = []
    for enrollment in user_enrollments:
        path_id = enrollment.get('learning_path_id')
        learning_path = learning_paths.get(path_id, {})
        
        enhanced_enrollment = {
            **enrollment,
            'learning_path_title': learning_path.get('title', 'Unknown'),
            'learning_path_description': learning_path.get('description', ''),
            'learning_path_department': learning_path.get('department', ''),
            'learning_path_duration': learning_path.get('duration', '')
        }
        enhanced_enrollments.append(enhanced_enrollment)
    
    return jsonify({
        'user_id': user_id,
        'enrolled_paths': enhanced_enrollments,
        'total_enrolled': len(enhanced_enrollments)
    })
