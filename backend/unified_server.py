#!/usr/bin/env python3
"""
Unified server that runs all backend services in one Flask app:
- Authentication endpoints
- Session Tracking endpoints  
- Main Backend endpoints (from app/)
"""

from flask import Flask
from flask_cors import CORS
from flask import request, make_response, jsonify
import sys
import os


# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Also add the parent directory (root of the project) to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Expose the Flask app for testing (after function definition)


def create_unified_app():
    """Create a unified Flask app with all endpoints"""
    app = Flask(__name__)
    
    # Configure CORS properly - allow all origins for development
    CORS(app, 
         origins="*",  # Allow all origins for development
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=False)  # Set to False when using origins="*"
    
    print("🌟 Creating Unified AdaptaLearn Backend Server...")
    
    # Handle preflight OPTIONS requests explicitly
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Requested-With")
            response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
            response.headers.add("Access-Control-Max-Age", "3600")
            return response
    
    # Import and register the main app blueprints individually
    # This way if one blueprint fails, others still get registered
    try:
        # Register blueprints one by one to avoid single point of failure
        blueprints_to_register = [
            ('backend.app.routes.admin', 'admin_bp', '/api/admin'),
            ('backend.app.routes.user', 'user_bp', '/api/user'),
            ('backend.app.routes.roles', 'roles_bp', '/api'),
            ('backend.app.routes.dashboard', 'dashboard_bp', '/api'),
            ('backend.app.routes.learning_path', 'learning_path_bp', '/api'),
            ('backend.app.routes.recommendation', 'recommendation_bp', '/api'),
            ('backend.app.routes.assessment', 'assessment_bp', '/api'),
            ('backend.app.routes.profile', 'profile_bp', '/api'),
            ('backend.app.routes.events', 'events_bp', '/api'),
            ('backend.app.routes.user_auth', 'user_auth_bp', '/api'),
            ('backend.app.routes.enrollment', 'enrollment_bp', '/api'),
            ('backend.app.routes.onboarding', 'onboarding_bp', '/api/onboarding'),
            ('backend.app.routes.conversation', 'conversation_bp', '/api/conversation'),
        ]
        
        registered_endpoints = set()  # Track registered endpoints to avoid conflicts
        
        for module_name, bp_name, url_prefix in blueprints_to_register:
            try:
                module = __import__(module_name, fromlist=[bp_name])
                blueprint = getattr(module, bp_name)
                
                # Register blueprint directly without checking URL map
                # (Blueprint objects don't have url_map attribute before registration)
                app.register_blueprint(blueprint, url_prefix=url_prefix)
                print(f"✅ Registered {bp_name}")
            except Exception as e:
                print(f"⚠️  Failed to register {bp_name}: {e}")
        
        print("✅ Main backend routes loaded from app/")
        
    except Exception as e:
        print(f"⚠️  Main backend app not available: {e}")
        print("    Continuing with basic services...")
        
    # Add a simple onboarding analyze endpoint as fallback
    @app.route('/api/onboarding/analyze', methods=['POST'])
    def analyze_onboarding_fallback():
        import json
        import time
        from datetime import datetime
        
        try:
            # Handle both FormData and JSON
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle FormData (file upload)
                user_id = request.form.get('user_id', f"user_{int(time.time())}")
                target_role = request.form.get('target_role', 'entry_level')
                department = request.form.get('department', 'general')
                
            else:
                # Handle JSON
                data = request.get_json() or {}
                user_id = data.get('user_id', f"user_{int(time.time())}")
                department = data.get('department', 'general')
                target_role = data.get('target_role', 'entry_level')
            
            # Load department learning paths mapping
            dept_learning_paths_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'department_learning_paths.json')
            try:
                with open(dept_learning_paths_file, 'r') as f:
                    dept_mapping = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                dept_mapping = {"departments": {}}
            
            # Map department names to department IDs
            dept_name_to_id = {
                "KYC": "KYC2024001",
                "ENGINEERING": "ENG2024001", 
                "DATA SCIENCE": "DS2024001",
                "ENG": "ENG2024001"
            }
            
            # Determine appropriate learning paths based on department and role
            recommended_paths = []
            dept_id = dept_name_to_id.get(department.upper())
            
            if dept_id and dept_id in dept_mapping["departments"]:
                # Get learning paths from department mapping
                dept_learning_paths = dept_mapping["departments"][dept_id]
                if department.upper() == "KYC":
                    if "scientist" in target_role.lower():
                        # For KYC Data Scientist: KYC paths + Data Science paths  
                        recommended_paths = [lp["learning_path_id"] for lp in dept_learning_paths]
                        if "DS2024001" in dept_mapping["departments"]:
                            recommended_paths.extend([lp["learning_path_id"] for lp in dept_mapping["departments"]["DS2024001"]])
                    else:
                        # For other KYC roles: just KYC paths
                        recommended_paths = [lp["learning_path_id"] for lp in dept_learning_paths]
                else:
                    # For other departments: use their standard learning paths
                    recommended_paths = [lp["learning_path_id"] for lp in dept_learning_paths]
            else:
                # Fallback to legacy logic for unknown departments
                if department.upper() == "KYC":
                    if "scientist" in target_role.lower():
                        recommended_paths = ["LP2024DS001", "LP2024DS002", "9cbc0df890d546729a36dca20d24a9ba"]
                    else:
                        recommended_paths = ["9cbc0df890d546729a36dca20d24a9ba", "LP2024GEN001"]
                elif department.upper() == "ENGINEERING" or "ENG" in department.upper():
                    recommended_paths = ["LP2024ENG001"]
                else:
                    recommended_paths = ["LP2024GEN001"]
            
            # Create onboarding recommendation
            recommendation = {
                "user_id": user_id,
                "department": department,
                "role": target_role,
                "recommended_learning_paths": recommended_paths,
                "skill_gaps": [
                    {
                        "skill": "Communication",
                        "current_level": 1.0,
                        "required_level": 3.0,
                        "gap": 2.0,
                        "importance": 4,
                        "priority": "high",
                        "confidence": 0.1,
                        "category": "soft"
                    },
                    {
                        "skill": "Problem Solving", 
                        "current_level": 1.0,
                        "required_level": 4.0,
                        "gap": 3.0,
                        "importance": 5,
                        "priority": "high",
                        "confidence": 0.1,
                        "category": "soft"
                    }
                ],
                "estimated_completion_weeks": 12,
                "priority_skills": ["Communication", "Problem Solving"],
                "resume_analysis_summary": {
                    "total_skills_found": 2,
                    "skills_by_level": {
                        "expert": [],
                        "advanced": [],
                        "intermediate": [],
                        "beginner": ["Communication", "Problem Solving"],
                        "basic": []
                    },
                    "top_skills": [
                        {"skill": "Communication", "proficiency": 1.0, "confidence": 0.1},
                        {"skill": "Problem Solving", "proficiency": 1.0, "confidence": 0.1}
                    ],
                    "skills_with_experience": []
                },
                "created_at": datetime.now().isoformat()
            }
            
            # Save to onboarding_recommendations.json
            recommendations_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'onboarding_recommendations.json')
            
            # Load existing recommendations
            try:
                with open(recommendations_file, 'r') as f:
                    recommendations_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                recommendations_data = {"recommendations": {}, "last_updated": ""}
            
            # Add new recommendation
            recommendations_data["recommendations"][user_id] = recommendation
            recommendations_data["last_updated"] = datetime.now().isoformat()
            
            # Save back to file
            with open(recommendations_file, 'w') as f:
                json.dump(recommendations_data, f, indent=2)
            
            # Return response in expected format
            result = {
                "success": True,
                "message": "Analysis completed",
                "user_id": user_id,
                "analysis": {
                    "skills_detected": ["communication", "problem_solving"],
                    "recommended_paths": recommended_paths,
                    "department_match": department,
                    "experience_level": "entry"
                }
            }
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}, 500
    
    # Import and register authentication routes
    try:
        from auth_server import app as auth_app
        print("✅ Authentication routes loaded")
        
        # Copy auth routes to main app
        for rule in auth_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                view_func = auth_app.view_functions[rule.endpoint]
                app.add_url_rule(rule.rule, rule.endpoint + '_auth', view_func, methods=rule.methods)
                
    except Exception as e:
        print(f"⚠️  Could not load auth routes: {e}")
    
    # Import and register session tracking routes
    try:
        from session_tracking import app as session_app
        print("✅ Session tracking routes loaded")
        
        # Copy session routes to main app
        for rule in session_app.url_map.iter_rules():
            if rule.endpoint != 'static' and not rule.endpoint.endswith('_auth'):
                view_func = session_app.view_functions[rule.endpoint]
                app.add_url_rule(rule.rule, rule.endpoint + '_session', view_func, methods=rule.methods)
                
    except Exception as e:
        print(f"⚠️  Could not load session tracking routes: {e}")
    
    # Try to import main backend routes
    try:
        from app import create_app as create_main_app
        main_app = create_main_app()
        print("✅ Main backend routes loaded")
        
        # Copy main app routes
        for rule in main_app.url_map.iter_rules():
            if (rule.endpoint != 'static' and 
                not rule.endpoint.endswith('_auth') and 
                not rule.endpoint.endswith('_session')):
                view_func = main_app.view_functions[rule.endpoint]
                app.add_url_rule(rule.rule, rule.endpoint + '_main', view_func, methods=rule.methods)
                
    except Exception as e:
        print(f"ℹ️  Main backend not available: {e}")
    
    # Remove conflicting manual endpoint definitions since blueprints handle them
    # Remove the manually defined endpoints to avoid conflicts with blueprints:
    # - /api/dashboard -> handled by dashboard_bp
    # - /api/recommendations -> handled by recommendation_bp  
    # - /api/assessments -> handled by assessment_bp
    # - /api/skill-gap -> handled by SkillGapAnalysis route
    # - /api/roles -> handled by roles_bp
    # - /api/admin/departments -> handled by admin_bp
    # - /api/admin/modules -> handled by admin_bp
    # Keep only endpoints that are truly unique to unified_server
    
    # Keep only unique endpoints that aren't handled by blueprints
    
    # Add /api/me endpoint for user info (not handled by any blueprint)
    @app.route('/api/me', methods=['GET'])
    def get_me():
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()
        
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        # For demo purposes, return a basic user - in real app, verify token
        return {
            'user': {
                'user_id': 'user_001',
                'email': 'pragathivetrivemurugan@gmail.com',
                'name': 'Pragathi',
                'roleType': 'learner'
            }
        }
    
    # Add /api/get-started endpoint (fallback if user_auth blueprint fails)
    @app.route('/api/get-started', methods=['POST'])
    def get_started():
        # Reuse the user_auth blueprint's get_started logic
        try:
            from app.routes.user_auth import get_started as auth_get_started
            return auth_get_started()
        except:
            # Fallback basic implementation
            return {'message': 'Get started endpoint - please implement fully'}, 200    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'services': ['auth', 'session_tracking', 'admin', 'learning_paths']}
    
    # Remove all other manual endpoint definitions to avoid conflicts with blueprints
    # The blueprints now handle:
    # - /api/admin/* (admin_bp)
    # - /api/user/* (user_bp) 
    # - /api/roles (roles_bp)
    # - /api/dashboard (dashboard_bp)
    # - /api/learning-paths (learning_path_bp)
    # - /api/recommendations (recommendation_bp)
    # - /api/assessments (assessment_bp)
    # - /api/onboarding/* (onboarding_bp)

    # Add learning paths endpoints
    @app.route('/api/admin/learning-paths', methods=['GET', 'POST'])
    def handle_admin_learning_paths():
        import json
        import uuid
        learning_paths_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'learning_paths.json')
        
        if request.method == 'GET':
            try:
                # Load learning paths
                with open(learning_paths_file, 'r') as f:
                    learning_paths_data = json.load(f)
                print(f"Debug: Loaded {len(learning_paths_data)} learning paths from file")
                
                # Load users to calculate enrollment counts
                users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')
                try:
                    with open(users_file, 'r') as f:
                        users_data = json.load(f)
                except Exception as e:
                    print(f"Error loading users file: {e}")
                    users_data = {}
                
                # Calculate enrollment counts for each learning path
                learning_paths_list = []
                for path_id, path_data in learning_paths_data.items():
                    # Count users enrolled in this learning path
                    enrolled_count = 0
                    for user_email, user_data in users_data.items():
                        try:
                            # Check if user has enrollments or learning paths
                            profile = user_data.get('profile', {})
                            learning_paths = profile.get('learning_paths', [])
                            enrollments = profile.get('enrollments', [])
                            
                            # Check if path_id is in user's learning paths or enrollments
                            if (path_id in learning_paths or 
                                any(enrollment.get('learning_path_id') == path_id for enrollment in enrollments)):
                                enrolled_count += 1
                                print(f"Debug: Found user {user_email} enrolled in {path_id}")
                        except Exception as user_error:
                            print(f"Error processing user {user_email}: {user_error}")
                            continue
                    
                    # Add enrollment count to path data
                    path_with_count = path_data.copy()
                    path_with_count['enrolledUsers'] = enrolled_count
                    learning_paths_list.append(path_with_count)
                    print(f"Debug: Path {path_id} has {enrolled_count} enrolled users")
                
                print(f"Debug: Returning {len(learning_paths_list)} learning paths")
                return jsonify(learning_paths_list)
            except Exception as e:
                print(f"Error in learning paths endpoint: {e}")
                return {'error': str(e)}, 500
                
        elif request.method == 'POST':
            try:
                with open(learning_paths_file, 'r') as f:
                    learning_paths_data = json.load(f)
                
                data = request.get_json() or {}
                path_id = data.get("id") or uuid.uuid4().hex
                data["id"] = path_id
                if not data.get("status"):
                    data["status"] = "active"
                
                learning_paths_data[path_id] = data
                
                with open(learning_paths_file, 'w') as f:
                    json.dump(learning_paths_data, f, indent=2)
                
                return {"success": True, "id": path_id, "department": data.get("department")}
            except Exception as e:
                return {'error': str(e)}, 500



    @app.route('/')
    def index():
        return {
            'message': 'AdaptaLearn Backend Services',
            'services': {
                'authentication': '/api/auth/*',
                'session_tracking': '/api/sessions/*',
                'health_check': '/health'
            }
        }
    

    return app

# Expose the Flask app for testing
app = create_unified_app()

if __name__ == "__main__":
    app = create_unified_app()
    
    print("=" * 60)
    print("🚀 Starting Unified AdaptaLearn Backend Server")
    print("🔗 Available on: http://localhost:5000")
    print("📚 All services combined:")
    print("   • Authentication API: /api/auth/*")
    print("   • Session Tracking API: /api/sessions/*")
    print("   • Health Check: /health")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
