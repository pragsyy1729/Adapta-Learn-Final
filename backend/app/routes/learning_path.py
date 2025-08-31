from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime
from ..services.data_access import (get_data_file_path, load_learning_paths, 
                                   _read_json, _write_json)

learning_path_bp = Blueprint('learning_path', __name__)

def load_json(filename):
    path = get_data_file_path(filename)
    return _read_json(path, [] if filename.endswith('.json') and filename not in ['learning_paths.json'] else {})

def save_json(filename, data):
    path = get_data_file_path(filename)
    _write_json(path, data)

@learning_path_bp.route('/learning-paths', methods=['GET'])
def list_learning_paths():
    user_id = request.args.get('user_id', 'user_001')  # Default for demo
    status = request.args.get('status')
    q = request.args.get('q', '').lower()
    limit = int(request.args.get('limit', 20))
    cursor = request.args.get('cursor')
    
    try:
        # Load progress and learning paths with consistent handling
        progress_list = load_json('LearningPathProgress.json')
        paths_data = load_learning_paths()  # Use consistent loader

        # Ensure consistent data structure
        if isinstance(paths_data, dict):
            # Convert dictionary to list format for processing
            paths = [{"attributes": {**path_data}} for path_data in paths_data.values()]
        else:
            paths = paths_data

        # Find user progress for all paths
        user_progress = []
        if isinstance(progress_list, list):
            user_progress = [p['attributes'] for p in progress_list if p.get('attributes', {}).get('user_id') == user_id]
        progress_by_path = {p['learning_path_id']: p for p in user_progress}

        # Attach progress info to each path, include all published paths
        result = []
        for path in paths:
            attr = path.get('attributes', path)  # Handle both formats
            # Only include published/active paths (or all if no status filter)
            if status and attr.get('status') != status:
                continue
            if not status and attr.get('status') not in ("published", "active"):
                continue

            # Filter by search query if provided
            if q:
                title = attr.get('title', '').lower()
                tags = [t.lower() for t in attr.get('tags', [])]
                if q not in title and not any(q in tag for tag in tags):
                    continue

            # Attach user progress if available
            progress = progress_by_path.get(attr.get('id'))
            if progress:
                attr = attr.copy()
                attr['progress_percent'] = progress['progress_percent']
                attr['modules_completed_count'] = progress['modules_completed_count']
                attr['modules_total_count'] = progress['modules_total_count']
                attr['status'] = progress['status']
                attr['progress_id'] = progress['id']

            result.append(attr)

        # Pagination
        start = 0
        if cursor:
            try:
                start = int(cursor)
            except Exception:
                start = 0
        paged = result[start:start+limit]
        next_cursor = str(start+limit) if start+limit < len(result) else None

        return jsonify({
            'results': paged,
            'next_cursor': next_cursor,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({'error': f'Failed to load learning paths: {str(e)}'}), 500

@learning_path_bp.route('/learning-paths/<user_id>', methods=['GET'])
def get_user_assigned_learning_paths(user_id):
    """
    Get learning paths assigned to a specific user (for New Joiner's view)
    """
    try:
        # Load user data to get assigned learning paths
        users_path = get_data_file_path('users.json')
        users = _read_json(users_path, {})

        # Find user by user_id (users are stored with email as key)
        user = None
        user_email = None
        for email, user_data in users.items():
            if user_data.get('user_id') == user_id:
                user = user_data
                user_email = email
                break

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        profile = user.get('profile', {})

        # Get user's enrollments (assigned learning paths)
        enrollments = profile.get('enrollments', [])

        if not enrollments:
            return jsonify({
                "success": True,
                "user_id": user_id,
                "assigned_learning_paths": [],
                "message": "No learning paths assigned to this user"
            })

        # Load learning paths data
        paths_data = load_learning_paths()

        # Load progress data
        progress_list = load_json('LearningPathProgress.json')
        progress_by_path = {}
        if isinstance(progress_list, list):
            user_progress = [p['attributes'] for p in progress_list if p.get('attributes', {}).get('user_id') == user_id]
            progress_by_path = {p['learning_path_id']: p for p in user_progress}

        # Build response with assigned learning paths
        assigned_paths = []
        for enrollment in enrollments:
            path_id = enrollment.get('learning_path_id')
            if path_id and path_id in paths_data:
                path_data = paths_data[path_id]

                # Attach progress info if available
                progress = progress_by_path.get(path_id)
                if progress:
                    path_data = path_data.copy()
                    path_data['progress_percent'] = progress.get('progress_percent', 0)
                    path_data['status'] = progress.get('status', 'not_started')
                    path_data['modules_completed_count'] = progress.get('modules_completed_count', 0)
                    path_data['modules_total_count'] = progress.get('modules_total_count', 0)
                    path_data['last_accessed_at'] = progress.get('last_accessed_at')

                assigned_paths.append(path_data)

        return jsonify({
            "success": True,
            "user_id": user_id,
            "assigned_learning_paths": assigned_paths,
            "total_count": len(assigned_paths)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get user learning paths: {str(e)}"
        }), 500

@learning_path_bp.route('/learning-paths/<path_id>/modules', methods=['GET'])
def get_learning_path_modules(path_id):
    user_id = request.args.get('user_id', 'user_001')  # Default for demo
    
    # Load required data
    modules = load_json('Module.json')
    module_progress = load_json('ModuleProgress.json')
    
    # Filter modules for this learning path
    path_modules = [m['attributes'] for m in modules if m['attributes']['learning_path_id'] == path_id]
    path_modules.sort(key=lambda x: x.get('order', 999))
    
    # Get user's module progress
    user_module_progress = {
        p['attributes']['module_id']: p['attributes'] 
        for p in module_progress 
        if p['attributes'].get('user_id') == user_id
    }
    
    # Enhance modules with progress and status
    enhanced_modules = []
    completed_modules = set()
    
    for module in path_modules:
        module_id = module['id']
        progress = user_module_progress.get(module_id, {})
        
        # Determine status and if module is locked
        status = progress.get('status', 'not_started')
        progress_percent = progress.get('progress_percent', 0)
        
        # Check if module is locked (prerequisites not met)
        prerequisites = module.get('prerequisite_module_ids', [])
        is_locked = bool(prerequisites and not all(prereq in completed_modules for prereq in prerequisites))
        
        if status == 'completed':
            completed_modules.add(module_id)
        
        enhanced_module = {
            **module,
            'status': status,
            'progress_percent': progress_percent,
            'is_locked': is_locked,
            'chapters_completed': progress.get('chapters_completed', 0),
            'time_spent_minutes': progress.get('time_spent_minutes', 0),
            'last_accessed_at': progress.get('last_accessed_at'),
            'started_at': progress.get('started_at'),
            'completed_at': progress.get('completed_at')
        }
        enhanced_modules.append(enhanced_module)
    
    return jsonify({
        'modules': enhanced_modules,
        'total_count': len(enhanced_modules)
    })

@learning_path_bp.route('/modules/<module_id>/start', methods=['POST'])
def start_module(module_id):
    data = request.get_json(force=True)
    user_id = data.get('user_id', 'user_001')
    
    # Load current module progress
    module_progress = load_json('ModuleProgress.json')
    
    # Check if progress already exists
    existing_progress = next(
        (p for p in module_progress if p['attributes']['module_id'] == module_id and p['attributes']['user_id'] == user_id), 
        None
    )
    
    if existing_progress:
        # Update existing progress
        existing_progress['attributes']['status'] = 'in_progress'
        existing_progress['attributes']['last_accessed_at'] = datetime.now().isoformat() + 'Z'
        if not existing_progress['attributes'].get('started_at'):
            existing_progress['attributes']['started_at'] = datetime.now().isoformat() + 'Z'
    else:
        # Create new progress entry
        modules = load_json('Module.json')
        module = next((m['attributes'] for m in modules if m['attributes']['id'] == module_id), None)
        if not module:
            return jsonify({'error': 'Module not found'}), 404
        
        new_progress = {
            'attributes': {
                'id': f"mp-{len(module_progress) + 1:03d}",
                'user_id': user_id,
                'module_id': module_id,
                'learning_path_id': module['learning_path_id'],
                'status': 'in_progress',
                'progress_percent': 0.0,
                'chapters_completed': 0,
                'chapters_total': module['chapter_count'],
                'time_spent_minutes': 0,
                'last_accessed_at': datetime.now().isoformat() + 'Z',
                'started_at': datetime.now().isoformat() + 'Z',
                'completed_at': None,
                'current_chapter_id': None
            }
        }
        module_progress.append(new_progress)
    
    # Save updated progress
    save_json('ModuleProgress.json', module_progress)
    
    return jsonify({'success': True, 'message': 'Module started successfully'})

@learning_path_bp.route('/modules/<module_id>/progress', methods=['PATCH'])
def update_module_progress(module_id):
    data = request.get_json(force=True)
    user_id = data.get('user_id', 'user_001')

    # Load current module progress
    module_progress = load_json('ModuleProgress.json')

    # Find the progress entry to update
    progress_entry = next(
        (p for p in module_progress if p['attributes']['module_id'] == module_id and p['attributes']['user_id'] == user_id),
        None
    )

    if not progress_entry:
        return jsonify({'error': 'Module progress not found'}), 404

    # Check if this is a completion event
    was_completed = progress_entry['attributes'].get('status') == 'completed'
    is_now_completed = data.get('status') == 'completed'

    # Update the progress
    attrs = progress_entry['attributes']
    if 'progress_percent' in data:
        attrs['progress_percent'] = data['progress_percent']
    if 'status' in data:
        attrs['status'] = data['status']
        if data['status'] == 'completed':
            attrs['completed_at'] = datetime.now().isoformat() + 'Z'
            attrs['progress_percent'] = 100.0
    if 'chapters_completed' in data:
        attrs['chapters_completed'] = data['chapters_completed']
    if 'time_spent_minutes' in data:
        attrs['time_spent_minutes'] = data['time_spent_minutes']

    attrs['last_accessed_at'] = datetime.now().isoformat() + 'Z'

    # Save updated progress
    save_json('ModuleProgress.json', module_progress)

    # Trigger gamification if module was just completed
    if not was_completed and is_now_completed:
        try:
            # Import and call gamification function
            from ..routes.gamification import award_points

            # Get module details for gamification
            modules = load_json('Module.json')
            module = next((m['attributes'] for m in modules if m['attributes']['id'] == module_id), None)

            if module:
                # Award points for module completion
                result = award_points(user_id, {
                    'activity_type': 'module_completion',
                    'details': {
                        'module_id': module_id,
                        'category': module.get('category', 'general'),
                        'title': module.get('title', 'Unknown Module')
                    }
                })
                print(f"Gamification result: {result}")  # Debug log
        except Exception as e:
            # Log error but don't fail the request
            print(f"Gamification error: {e}")

    return jsonify({'success': True, 'message': 'Progress updated successfully'})

@learning_path_bp.route('/learning-path-progress/<progress_id>', methods=['PATCH'])
def patch_learning_path_progress(progress_id):
    data = request.get_json(force=True)
    progress_list = load_json('LearningPathProgress.json')
    updated = False
    for p in progress_list:
        if p['attributes']['id'] == progress_id:
            if 'status' in data:
                p['attributes']['status'] = data['status']
            if 'last_accessed_at' in data:
                p['attributes']['last_accessed_at'] = data['last_accessed_at']
            if 'progress_percent' in data:
                p['attributes']['progress_percent'] = data['progress_percent']
            if 'current_module_id' in data:
                p['attributes']['current_module_id'] = data['current_module_id']
            updated = True
            break
    if updated:
        save_json('LearningPathProgress.json', progress_list)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Progress record not found'}), 404

@learning_path_bp.route('/learning-path-progress/<user_id>', methods=['GET'])
def get_learning_path_progress(user_id):
    progress_list = load_json('LearningPathProgress.json')
    user_progress = [p['attributes'] for p in progress_list if p['attributes']['user_id'] == user_id]
    return jsonify(user_progress)

@learning_path_bp.route('/learning-paths/<path_id>/analytics', methods=['GET'])
def get_learning_path_analytics(path_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    # Find progress for this user and path
    progress_list = load_json('LearningPathProgress.json')
    progress = next((p['attributes'] for p in progress_list if p['attributes']['user_id'] == user_id and p['attributes']['learning_path_id'] == path_id), None)
    if not progress:
        return jsonify({'error': 'No analytics available'}), 404
    analytics = {
        'completion_rate': progress.get('progress_percent', 0) / 100.0,
        'time_spent_minutes': progress.get('time_invested_minutes', 0),
        'last_active_at': progress.get('last_accessed_at')
    }
    return jsonify(analytics)
