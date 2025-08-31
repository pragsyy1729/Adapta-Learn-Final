import json
import os
import uuid
import shutil
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_json_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    backup_filepath = filepath + '.backup'
    
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            data = json.loads(content)
            # Create backup of valid file
            if content.strip():  # Only backup non-empty files
                shutil.copy2(filepath, backup_filepath)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        
        # Try to load from backup
        if os.path.exists(backup_filepath):
            try:
                print(f"Attempting to restore from backup: {backup_filepath}")
                with open(backup_filepath, 'r') as file:
                    data = json.load(file)
                # Restore the backup to main file
                shutil.copy2(backup_filepath, filepath)
                print(f"Successfully restored {filename} from backup")
                return data
            except Exception as backup_error:
                print(f"Backup restore failed: {backup_error}")
        
        # Return empty structure if all else fails
        return {}

def save_json_file(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    temp_filepath = filepath + '.tmp'
    
    try:
        # Validate data can be serialized
        json_string = json.dumps(data, indent=2)
        
        # Write to temporary file first
        with open(temp_filepath, 'w') as file:
            file.write(json_string)
        
        # Validate the temporary file can be read back
        with open(temp_filepath, 'r') as file:
            json.load(file)
        
        # Atomically rename temp file to actual file
        os.rename(temp_filepath, filepath)
        print(f"Successfully saved {filename}")
        
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise e

def validate_session_data(data):
    """Validate session data structure"""
    if not isinstance(data, dict):
        return False
    
    for user_id, user_data in data.items():
        if not isinstance(user_data, dict):
            return False
        
        required_fields = ['sessions', 'total_time_spent_seconds', 'average_session_duration']
        if not all(field in user_data for field in required_fields):
            return False
        
        if not isinstance(user_data['sessions'], list):
            return False
    
    return True

def save_session_data(session_data):
    """Save session data with validation"""
    if not validate_session_data(session_data):
        raise ValueError('Invalid session data structure')
    save_json_file('SessionTimeTracking.json', session_data)

@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    """Start a new session for a user or return existing active session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Load session tracking data
        session_data = load_json_file('SessionTimeTracking.json')
        
        # Initialize user data if not exists
        if user_id not in session_data:
            session_data[user_id] = {
                'sessions': [],
                'total_time_spent_seconds': 0,
                'average_session_duration': 0,
                'last_activity': None
            }
        
        # Check if there's already an active session (no end_time)
        active_session = None
        for session in session_data[user_id]['sessions']:
            if session.get('end_time') is None:
                active_session = session
                break
        
        if active_session:
            # Return existing active session
            return jsonify({
                'session_id': active_session['session_id'],
                'start_time': active_session['start_time'],
                'existing_session': True
            })
        
        # Create new session with UUID for guaranteed uniqueness
        session_id = f"session_{uuid.uuid4().hex[:8]}_{user_id}"
        new_session = {
            'session_id': session_id,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'activities': []
        }
        
        session_data[user_id]['sessions'].append(new_session)
        
        # Validate before saving
        if not validate_session_data(session_data):
            return jsonify({'error': 'Invalid session data structure'}), 500
            
        save_session_data(session_data)
        
        return jsonify({
            'session_id': session_id,
            'start_time': new_session['start_time'],
            'existing_session': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/end', methods=['POST'])
def end_session():
    """End a session and calculate duration"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id or not session_id:
            return jsonify({'error': 'user_id and session_id are required'}), 400
        
        session_data = load_json_file('SessionTimeTracking.json')
        
        if user_id not in session_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Find and update the session
        for session in session_data[user_id]['sessions']:
            if session['session_id'] == session_id:
                end_time = datetime.now(timezone.utc)
                start_time = datetime.fromisoformat(session['start_time'].replace('Z', '+00:00'))
                
                duration_seconds = int((end_time - start_time).total_seconds())
                
                session['end_time'] = end_time.isoformat()
                session['duration_seconds'] = duration_seconds
                
                # End any remaining activities
                if session['activities']:
                    last_activity = session['activities'][-1]
                    if last_activity.get('end_time') is None:
                        activity_start = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                        activity_duration = int((end_time - activity_start).total_seconds())
                        
                        last_activity['end_time'] = end_time.isoformat()
                        last_activity['duration_seconds'] = activity_duration
                
                # Update user totals (maintain backward compatibility with minutes)
                session_data[user_id]['total_time_spent_seconds'] = session_data[user_id].get('total_time_spent_seconds', 0) + duration_seconds
                session_data[user_id]['last_activity'] = end_time.isoformat()
                
                # Calculate average session duration
                completed_sessions = [s for s in session_data[user_id]['sessions'] if s.get('end_time')]
                if completed_sessions:
                    avg_duration = sum(s.get('duration_seconds', s.get('duration_minutes', 0) * 60) for s in completed_sessions) / len(completed_sessions)
                    session_data[user_id]['average_session_duration'] = round(avg_duration, 2)
                
                save_session_data(session_data)
                
                return jsonify({
                    'session_id': session_id,
                    'duration_seconds': duration_seconds,
                    'duration_minutes': round(duration_seconds / 60, 2),
                    'total_time_spent_seconds': session_data[user_id]['total_time_spent_seconds']
                })
        
        return jsonify({'error': 'Session not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/update-activity', methods=['POST'])
def update_activity_progress():
    """Update the duration of the current active activity without ending it"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        session_data = load_json_file('SessionTimeTracking.json')
        
        if user_id not in session_data:
            return jsonify({'error': 'User not found'}), 404
            
        # Find the current session and update the last activity duration
        for session in session_data[user_id]['sessions']:
            if session['session_id'] == session_id and session['activities']:
                last_activity = session['activities'][-1]
                if last_activity.get('end_time') is None:
                    # Calculate current duration without ending the activity
                    start_time = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    duration_seconds = int((current_time - start_time).total_seconds())
                    
                    # Update duration but keep activity active
                    last_activity['duration_seconds'] = duration_seconds
                    
                    # Save to file
                    save_session_data(session_data)
                    
                    return jsonify({
                        'success': True,
                        'activity_type': last_activity['activity_type'],
                        'current_duration_seconds': duration_seconds,
                        'is_active': True
                    })
        
        return jsonify({'error': 'No active activity found'}), 404
        
    except Exception as e:
        print(f"Error updating activity progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/end-activity', methods=['POST'])
def end_activity():
    """End a specific activity in the current session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        session_data = load_json_file('SessionTimeTracking.json')
        
        if user_id not in session_data:
            return jsonify({'error': 'User not found'}), 404
            
        # Find the current session and end the last activity
        for session in session_data[user_id]['sessions']:
            if session['session_id'] == session_id and session['activities']:
                last_activity = session['activities'][-1]
                if last_activity.get('end_time') is None:
                    end_time = datetime.now(timezone.utc)
                    start_time = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                    duration_seconds = int((end_time - start_time).total_seconds())
                    
                    last_activity['end_time'] = end_time.isoformat()
                    last_activity['duration_seconds'] = duration_seconds
                    
                    # Save to file
                    save_session_data(session_data)
                    
                    return jsonify({
                        'success': True,
                        'activity_ended': last_activity['activity_type'],
                        'duration_seconds': duration_seconds,
                        'duration_minutes': round(duration_seconds / 60, 2)
                    })
        
        return jsonify({'error': 'No active activity found'}), 404
        
    except Exception as e:
        print(f"Error ending activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/activity', methods=['POST'])
def track_activity():
    """Track activity within a session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        activity_type = data.get('activity_type')
        
        if not all([user_id, session_id, activity_type]):
            return jsonify({'error': 'user_id, session_id, and activity_type are required'}), 400
        
        session_data = load_json_file('SessionTimeTracking.json')
        
        if user_id not in session_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Find the session and add activity
        for session in session_data[user_id]['sessions']:
            if session['session_id'] == session_id:
                # Check for existing activities
                if session['activities']:
                    last_activity = session['activities'][-1]
                    
                    # If there's an active activity of the same type, update it instead of creating new one
                    if (last_activity.get('end_time') is None and 
                        last_activity.get('activity_type') == activity_type):
                        
                        # For same activity type, check if it's the exact same activity (same module, path, etc.)
                        same_activity = True
                        if data.get('learning_path_id') and last_activity.get('learning_path_id') != data.get('learning_path_id'):
                            same_activity = False
                        if data.get('module_id') and last_activity.get('module_id') != data.get('module_id'):
                            same_activity = False
                            
                        if same_activity:
                            # Check if this call is too rapid (less than 1 second from last activity start)
                            last_start_time = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                            current_time = datetime.now(timezone.utc)
                            time_diff = (current_time - last_start_time).total_seconds()
                            
                            if time_diff < 1.0:  # Less than 1 second
                                return jsonify({
                                    'message': 'Rate limited: Activity call too rapid',
                                    'activity_id': len(session['activities']) - 1,
                                    'existing_activity': True
                                })
                            
                            # Same activity already in progress, just return success
                            return jsonify({
                                'message': 'Activity already in progress',
                                'activity_id': len(session['activities']) - 1,
                                'existing_activity': True
                            })
                        else:
                            # Different module/path, end the previous and start new
                            end_time = datetime.now(timezone.utc)
                            start_time = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                            duration_seconds = int((end_time - start_time).total_seconds())
                            
                            last_activity['end_time'] = end_time.isoformat()
                            last_activity['duration_seconds'] = duration_seconds
                    
                    # If there's an active activity of different type, end it
                    elif (last_activity.get('end_time') is None and 
                          last_activity.get('activity_type') != activity_type):
                        end_time = datetime.now(timezone.utc)
                        start_time = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                        duration_seconds = int((end_time - start_time).total_seconds())
                        
                        last_activity['end_time'] = end_time.isoformat()
                        last_activity['duration_seconds'] = duration_seconds
                
                # Create new activity
                activity = {
                    'activity_type': activity_type,
                    'start_time': datetime.now(timezone.utc).isoformat(),
                    'end_time': None,
                    'duration_seconds': 0
                }
                
                # Add optional fields
                if data.get('learning_path_id'):
                    activity['learning_path_id'] = data['learning_path_id']
                if data.get('module_id'):
                    activity['module_id'] = data['module_id']
                
                session['activities'].append(activity)
                save_session_data(session_data)
                
                return jsonify({'message': f'Activity "{activity_type}" started successfully'})
        
        return jsonify({'error': 'Session not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/stats/<user_id>', methods=['GET'])
def get_session_stats(user_id):
    """Get session statistics for a user"""
    try:
        session_data = load_json_file('SessionTimeTracking.json')
        
        if user_id not in session_data:
            return jsonify({
                'total_sessions': 0,
                'total_time_spent_seconds': 0,
                'total_time_spent_minutes': 0,
                'average_session_duration': 0,
                'sessions': []
            })
        
        user_stats = session_data[user_id]
        
        # Calculate totals with backward compatibility
        total_seconds = user_stats.get('total_time_spent_seconds', 0)
        if total_seconds == 0 and 'total_time_spent_minutes' in user_stats:
            total_seconds = user_stats['total_time_spent_minutes'] * 60
        
        return jsonify({
            'total_sessions': len(user_stats['sessions']),
            'total_time_spent_seconds': total_seconds,
            'total_time_spent_minutes': round(total_seconds / 60, 2),
            'average_session_duration': user_stats['average_session_duration'],
            'last_activity': user_stats['last_activity'],
            'sessions': user_stats['sessions']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
