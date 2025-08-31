#!/usr/bin/env python3
"""
All-in-One AdaptaLearn Backend Server
Combines Authentication + Session Tracking in one server
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timezone
import uuid
import hashlib

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def load_json_file(filename):
    """Load JSON data from file"""
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    """Save JSON data to file"""
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """Handle user sign in"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Load users data
        users_data = load_json_file('users.json')
        
        # Find user by email
        user = None
        for user_data in users_data:
            if user_data.get('email') == email:
                user = user_data
                break
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password (in real app, use proper password hashing)
        if user.get('password') != password:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate session token
        session_token = str(uuid.uuid4())
        
        # Update user with session token
        user['session_token'] = session_token
        user['last_login'] = datetime.now().isoformat()
        save_json_file('users.json', users_data)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['user_id'],
                'email': user['email'],
                'name': user.get('name', ''),
                'role': user.get('role', 'student')
            },
            'session_token': session_token
        })
        
    except Exception as e:
        print(f"Signin error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/signout', methods=['POST'])
def signout():
    """Handle user sign out"""
    try:
        data = request.json or {}
        session_token = data.get('session_token')
        
        if session_token:
            users_data = load_json_file('users.json')
            
            # Find and clear session token
            for user in users_data:
                if user.get('session_token') == session_token:
                    user['session_token'] = None
                    break
            
            save_json_file('users.json', users_data)
        
        return jsonify({'success': True, 'message': 'Signed out successfully'})
        
    except Exception as e:
        print(f"Signout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/validate', methods=['POST'])
def validate_session():
    """Validate a session token"""
    try:
        data = request.json
        session_token = data.get('session_token')
        
        if not session_token:
            return jsonify({'valid': False}), 401
        
        users_data = load_json_file('users.json')
        
        # Find user by session token
        for user in users_data:
            if user.get('session_token') == session_token:
                return jsonify({
                    'valid': True,
                    'user': {
                        'id': user['user_id'],
                        'email': user['email'],
                        'name': user.get('name', ''),
                        'role': user.get('role', 'student')
                    }
                })
        
        return jsonify({'valid': False}), 401
        
    except Exception as e:
        print(f"Validation error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# =============================================================================
# SESSION TRACKING ENDPOINTS
# =============================================================================

@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    """Start a new session for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        session_data = load_json_file('SessionTimeTracking.json')
        
        # Initialize user data if not exists
        if user_id not in session_data:
            session_data[user_id] = {
                'user_id': user_id,
                'total_time_spent_minutes': 0,
                'total_sessions': 0,
                'average_session_duration': 0.0,
                'last_activity': None,
                'sessions': []
            }
        
        # Create new session
        session_id = generate_session_id()
        new_session = {
            'session_id': session_id,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'end_time': None,
            'duration_minutes': 0,
            'activities': []
        }
        
        session_data[user_id]['sessions'].append(new_session)
        session_data[user_id]['total_sessions'] += 1
        
        save_json_file('SessionTimeTracking.json', session_data)
        
        return jsonify({'session_id': session_id})
        
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
                
                duration_minutes = int((end_time - start_time).total_seconds() / 60)
                
                session['end_time'] = end_time.isoformat()
                session['duration_minutes'] = duration_minutes
                
                # End any remaining activities
                if session['activities']:
                    last_activity = session['activities'][-1]
                    if last_activity.get('end_time') is None:
                        activity_start = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                        activity_duration = int((end_time - activity_start).total_seconds() / 60)
                        
                        last_activity['end_time'] = end_time.isoformat()
                        last_activity['duration_minutes'] = activity_duration
                
                # Update user totals
                session_data[user_id]['total_time_spent_minutes'] += duration_minutes
                session_data[user_id]['last_activity'] = end_time.isoformat()
                
                # Calculate average session duration
                completed_sessions = [s for s in session_data[user_id]['sessions'] if s.get('end_time')]
                if completed_sessions:
                    avg_duration = sum(s['duration_minutes'] for s in completed_sessions) / len(completed_sessions)
                    session_data[user_id]['average_session_duration'] = round(avg_duration, 2)
                
                save_json_file('SessionTimeTracking.json', session_data)
                
                return jsonify({
                    'session_id': session_id,
                    'duration_minutes': duration_minutes,
                    'total_time_spent': session_data[user_id]['total_time_spent_minutes']
                })
        
        return jsonify({'error': 'Session not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/activity', methods=['POST'])
def track_activity():
    """Track an activity within a session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        activity_type = data.get('activity_type')
        
        if not user_id or not session_id or not activity_type:
            return jsonify({'error': 'user_id, session_id, and activity_type are required'}), 400
        
        session_data = load_json_file('SessionTimeTracking.json')
        
        if user_id not in session_data:
            return jsonify({'error': 'User not found'}), 404
            
        # Find the current session
        for session in session_data[user_id]['sessions']:
            if session['session_id'] == session_id:
                # End previous activity if exists
                if session['activities']:
                    last_activity = session['activities'][-1]
                    if last_activity.get('end_time') is None:
                        end_time = datetime.now(timezone.utc)
                        start_time = datetime.fromisoformat(last_activity['start_time'].replace('Z', '+00:00'))
                        duration = int((end_time - start_time).total_seconds() / 60)
                        
                        last_activity['end_time'] = end_time.isoformat()
                        last_activity['duration_minutes'] = duration
                
                # Create new activity
                activity = {
                    'activity_type': activity_type,
                    'start_time': datetime.now(timezone.utc).isoformat(),
                    'end_time': None,
                    'duration_minutes': 0
                }
                
                # Add optional fields
                if 'learning_path_id' in data:
                    activity['learning_path_id'] = data['learning_path_id']
                if 'module_id' in data:
                    activity['module_id'] = data['module_id']
                
                session['activities'].append(activity)
                save_json_file('SessionTimeTracking.json', session_data)
                
                return jsonify({'message': 'Activity tracked successfully'})
        
        return jsonify({'error': 'Session not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/end-activity', methods=['POST'])
def end_activity():
    """End a specific activity in the current session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user_001')
        session_id = data.get('session_id')
        
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
                    duration = int((end_time - start_time).total_seconds() / 60)
                    
                    last_activity['end_time'] = end_time.isoformat()
                    last_activity['duration_minutes'] = duration
                    
                    # Save to file
                    save_json_file('SessionTimeTracking.json', session_data)
                    
                    return jsonify({
                        'success': True,
                        'activity_ended': last_activity['activity_type'],
                        'duration_minutes': duration
                    })
        
        return jsonify({'error': 'No active activity found'}), 404
        
    except Exception as e:
        print(f"Error ending activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/stats/<user_id>', methods=['GET'])
def get_session_stats(user_id):
    """Get session statistics for a user"""
    try:
        session_data = load_json_file('SessionTimeTracking.json')
        
        if user_id not in session_data:
            return jsonify({
                'total_sessions': 0,
                'total_time_spent_minutes': 0,
                'average_session_duration': 0,
                'sessions': []
            })
        
        user_stats = session_data[user_id]
        
        return jsonify({
            'total_sessions': len(user_stats['sessions']),
            'total_time_spent_minutes': user_stats['total_time_spent_minutes'],
            'average_session_duration': user_stats['average_session_duration'],
            'last_activity': user_stats['last_activity'],
            'sessions': user_stats['sessions']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# HEALTH CHECK AND INFO ENDPOINTS
# =============================================================================

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': ['authentication', 'session_tracking'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """API info endpoint"""
    return jsonify({
        'message': 'AdaptaLearn All-in-One Backend Server',
        'version': '1.0.0',
        'endpoints': {
            'authentication': [
                'POST /api/auth/signin',
                'POST /api/auth/signout',
                'POST /api/auth/validate'
            ],
            'session_tracking': [
                'POST /api/sessions/start',
                'POST /api/sessions/end',
                'POST /api/sessions/activity',
                'POST /api/sessions/end-activity',
                'GET /api/sessions/stats/<user_id>'
            ],
            'utilities': [
                'GET /health',
                'GET /'
            ]
        }
    })

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("🌟 AdaptaLearn All-in-One Backend Server")
    print("=" * 60)
    print("🔐 Authentication API: http://localhost:5000/api/auth/*")
    print("📊 Session Tracking API: http://localhost:5000/api/sessions/*")
    print("❤️  Health Check: http://localhost:5000/health")
    print("📚 API Info: http://localhost:5000/")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
