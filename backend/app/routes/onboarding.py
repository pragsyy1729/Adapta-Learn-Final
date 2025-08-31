"""
API Routes for AI Onboarding Agent
Integrates the onboarding system with the existing Flask application
"""

from flask import Blueprint, request, jsonify
import os
import json
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime
from ..services.data_access import get_data_file_path, _read_json, _write_json

# Create blueprint with consistent URL prefix
onboarding_bp = Blueprint('onboarding', __name__)

# File upload configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@onboarding_bp.route('/analyze', methods=['POST'])
def analyze_user_onboarding():
    """
    Analyze a new user for onboarding
    Expects: multipart form with resume file, user_id, target_role, department
    """
    try:
        # Handle both FormData and JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle FormData (file upload)
            user_id = request.form.get('user_id', f"user_{int(datetime.now().timestamp())}")
            target_role = request.form.get('target_role', 'entry_level')
            department = request.form.get('department', 'general')
            
            # Handle file upload
            if 'resume' not in request.files:
                return jsonify({"success": False, "error": "No resume file provided"}), 400
            
            file = request.files['resume']
            if file.filename == '':
                return jsonify({"success": False, "error": "No resume file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"success": False, "error": "Invalid file type. Only PDF and DOCX allowed"}), 400
            
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)
            resume_file_path = temp_path
            
        else:
            # Handle JSON (for testing without file upload)
            data = request.get_json() or {}
            user_id = data.get('user_id', f"user_{int(datetime.now().timestamp())}")
            department = data.get('department', 'general')
            target_role = data.get('target_role', 'entry_level')
            resume_file_path = data.get('resume_path', None)  # Optional for testing
        
        # Import and use the OnboardingAIAgent
        try:
            import sys
            # Add the agent directory to the path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            agent_dir = os.path.join(project_root, 'agent')
            if agent_dir not in sys.path:
                sys.path.insert(0, agent_dir)
            
            print(f"DEBUG: Attempting to import OnboardingAIAgent from {agent_dir}")
            from onboarding_agent import OnboardingAIAgent
            print("DEBUG: OnboardingAIAgent import successful")
            
            # Create agent instance
            agent = OnboardingAIAgent()
            
            # Perform AI-powered onboarding analysis
            if resume_file_path and os.path.exists(resume_file_path):
                print(f"🤖 Starting AI onboarding analysis for user {user_id}")
                analysis_result = agent.analyze_user_for_onboarding(
                    user_id=user_id,
                    resume_file_path=resume_file_path,
                    target_role=target_role,
                    department=department
                )
                
                # Clean up temporary file if it was uploaded
                if request.content_type and 'multipart/form-data' in request.content_type:
                    try:
                        os.remove(resume_file_path)
                    except:
                        pass
                
                # Return the AI analysis result
                return jsonify({
                    "success": True,
                    "message": "AI-powered analysis completed",
                    "user_id": user_id,
                    "data": analysis_result
                })
            else:
                # Fallback to basic analysis if no resume provided
                print(f"📋 Performing basic onboarding analysis for user {user_id} (no resume)")
                
                # Load department learning paths mapping
                dept_learning_paths_file = get_data_file_path('department_learning_paths.json')
                try:
                    dept_mapping = _read_json(dept_learning_paths_file, {"departments": {}})
                except Exception:
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
                    recommended_paths = [lp["learning_path_id"] for lp in dept_learning_paths]
                    
                    # Special case: Data Scientists in KYC should also get Data Science learning paths
                    if department.upper() == "KYC" and "scientist" in target_role.lower():
                        print(f"DEBUG: User is Data Scientist in KYC - adding Data Science learning paths")
                        ds_dept_id = dept_name_to_id.get("DATA SCIENCE")
                        if ds_dept_id and ds_dept_id in dept_mapping["departments"]:
                            ds_learning_paths = dept_mapping["departments"][ds_dept_id]
                            ds_path_ids = [lp["learning_path_id"] for lp in ds_learning_paths]
                            recommended_paths.extend(ds_path_ids)
                            print(f"DEBUG: Added Data Science paths: {ds_path_ids}")
                else:
                    # Fallback to generic paths
                    recommended_paths = ["LP2024GEN001"]
                
                print(f"DEBUG: Final recommended paths for {user_id}: {recommended_paths}")
                
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
                            "priority": "high"
                        }
                    ],
                    "estimated_completion_weeks": 8,
                    "priority_skills": ["Communication"],
                    "created_at": datetime.now().isoformat()
                }
                
                # Save to onboarding_recommendations.json
                recommendations_file = get_data_file_path('onboarding_recommendations.json')
                
                # Load existing recommendations
                try:
                    recommendations_data = _read_json(recommendations_file, {"recommendations": {}, "last_updated": ""})
                except Exception:
                    recommendations_data = {"recommendations": {}, "last_updated": ""}
                
                # Add new recommendation
                recommendations_data["recommendations"][user_id] = recommendation
                recommendations_data["last_updated"] = datetime.now().isoformat()
                
                # Save back to file
                _write_json(recommendations_file, recommendations_data)
                
                # Try to auto-assign the recommended paths using the agent
                try:
                    # Import the agent for auto-assignment
                    import sys
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                    agent_dir = os.path.join(project_root, 'agent')
                    if agent_dir not in sys.path:
                        sys.path.insert(0, agent_dir)
                    
                    from onboarding_agent import OnboardingAIAgent
                    agent = OnboardingAIAgent()
                    agent._auto_assign_recommended_paths(user_id, recommended_paths)
                    print(f"✅ Auto-assigned {len(recommended_paths)} learning paths to user {user_id}")
                except Exception as e:
                    print(f"⚠️ Failed to auto-assign learning paths: {e}")
                    # Continue with the response even if auto-assignment fails
                
                # Return response in expected format
                result = {
                    "success": True,
                    "message": "Basic analysis completed",
                    "user_id": user_id,
                    "analysis": {
                        "skills_detected": ["communication", "problem_solving"],
                        "recommended_paths": recommended_paths,
                        "department_match": department,
                        "experience_level": "entry"
                    }
                }
                
                return jsonify(result)
                
        except ImportError as e:
            print(f"⚠️ OnboardingAIAgent import failed: {e}. Using basic analysis.")
            print(f"DEBUG: sys.path includes: {[p for p in sys.path if 'adapta-learn' in p]}")
            # Fall back to the original basic analysis logic
            return jsonify({"success": False, "error": "AI analysis not available"}), 500
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@onboarding_bp.route('/status/<user_id>', methods=['GET'])
def get_onboarding_status(user_id):
    """Get onboarding status for a specific user"""
    try:
        # Simple status implementation
        recommendations_file = get_data_file_path('onboarding_recommendations.json')
        recommendations_data = _read_json(recommendations_file, {"recommendations": {}})
        
        if user_id in recommendations_data["recommendations"]:
            status = {
                "user_id": user_id,
                "status": "analyzed",
                "recommendation": recommendations_data["recommendations"][user_id]
            }
        else:
            status = {
                "user_id": user_id,
                "status": "not_analyzed",
                "recommendation": None
            }
        
        return jsonify({
            "success": True,
            "data": status
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get status: {str(e)}"}), 500

@onboarding_bp.route('/departments', methods=['GET'])
def get_departments():
    """Get all available departments"""
    try:
        departments_file = get_data_file_path('department.json')
        departments_data = _read_json(departments_file, {"departments": []})
        
        # Load department learning paths mapping
        dept_learning_paths_file = get_data_file_path('department_learning_paths.json')
        dept_learning_paths_data = _read_json(dept_learning_paths_file, {"departments": {}})
        
        # Enhance departments with their learning paths
        for dept in departments_data["departments"]:
            dept_id = dept["id"]
            dept["learning_paths"] = dept_learning_paths_data["departments"].get(dept_id, [])
            dept["mandatory_paths"] = [lp for lp in dept["learning_paths"] if lp.get("is_mandatory", False)]
        
        return jsonify({
            "success": True,
            "data": departments_data["departments"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@onboarding_bp.route('/departments/<dept_id>/learning-paths', methods=['POST'])
def add_learning_path_to_department(dept_id):
    """Add a learning path to a department"""
    try:
        data = request.get_json() or {}
        
        # Load department learning paths
        dept_learning_paths_file = get_data_file_path('department_learning_paths.json')
        dept_learning_paths_data = _read_json(dept_learning_paths_file, {"departments": {}})
        
        # Initialize department if not exists
        if dept_id not in dept_learning_paths_data["departments"]:
            dept_learning_paths_data["departments"][dept_id] = []
        
        # Check if learning path already exists
        existing_paths = dept_learning_paths_data["departments"][dept_id]
        learning_path_id = data.get("learning_path_id")
        
        if any(lp["learning_path_id"] == learning_path_id for lp in existing_paths):
            return jsonify({"error": "Learning path already exists for this department"}), 400
        
        # Add new learning path
        new_path = {
            "department": dept_id,
            "learning_path_id": learning_path_id,
            "is_mandatory": data.get("is_mandatory", True),
            "priority": data.get("priority", 1),
            "estimated_duration_weeks": data.get("estimated_duration_weeks"),
            "prerequisites": data.get("prerequisites", [])
        }
        
        existing_paths.append(new_path)
        _write_json(dept_learning_paths_file, dept_learning_paths_data)
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@onboarding_bp.route('/auto-enroll-from-onboarding', methods=['POST'])
def auto_enroll_from_onboarding():
    """
    Auto-enroll user in recommended learning paths from onboarding
    Expects: JSON with user_id
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"success": False, "error": "user_id is required"}), 400
        
        # Load onboarding recommendations
        recommendations_file = get_data_file_path('onboarding_recommendations.json')
        recommendations_data = _read_json(recommendations_file, {"recommendations": {}})
        
        if user_id not in recommendations_data["recommendations"]:
            return jsonify({"success": False, "error": "No onboarding recommendations found for user"}), 404
        
        user_recommendations = recommendations_data["recommendations"][user_id]
        recommended_paths = user_recommendations.get('recommended_learning_paths', [])
        
        if not recommended_paths:
            return jsonify({"success": False, "error": "No recommended learning paths found"}), 404
        
        # Load users to check current enrollments
        users_file = get_data_file_path('users.json')
        users = _read_json(users_file, {})
        
        # Find user and check current enrollments
        user_found = False
        current_enrollments = []
        enrolled_paths = []
        
        for email, user_data in users.items():
            if user_data.get('user_id') == user_id:
                user_found = True
                current_enrollments = user_data.get('profile', {}).get('enrollments', [])
                break
        
        if not user_found:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Check which recommended paths are not already enrolled
        existing_path_ids = {enrollment.get('learning_path_id') for enrollment in current_enrollments}
        paths_to_enroll = [path_id for path_id in recommended_paths if path_id not in existing_path_ids]
        
        if not paths_to_enroll:
            print(f"DEBUG: All {len(recommended_paths)} recommended paths already enrolled for user {user_id}")
            return jsonify({
                "success": True,
                "message": "All recommended paths already enrolled",
                "enrolled_paths": [],
                "total_enrolled": 0
            })
        
        # Load learning paths data to get path details
        learning_paths_file = get_data_file_path('learning_paths.json')
        learning_paths_data = _read_json(learning_paths_file, {})
        
        # Create enrollment entries
        now_iso = datetime.now().isoformat()
        new_enrollments = []
        
        for path_id in paths_to_enroll:
            path_info = learning_paths_data.get(path_id, {})
            
            enrollment = {
                'learning_path_id': path_id,
                'enrolled_at': now_iso,
                'status': 'enrolled',
                'source': 'onboarding_auto_enroll'
            }
            
            new_enrollments.append(enrollment)
            enrolled_paths.append({
                'learning_path_id': path_id,
                'learning_path_title': path_info.get('title', path_id),
                'enrolled_at': now_iso
            })
        
        # Update user's enrollments
        for email, user_data in users.items():
            if user_data.get('user_id') == user_id:
                if 'profile' not in user_data:
                    user_data['profile'] = {}
                if 'enrollments' not in user_data['profile']:
                    user_data['profile']['enrollments'] = []
                
                user_data['profile']['enrollments'].extend(new_enrollments)
                break
        
        # Save updated users data
        _write_json(users_file, users)
        
        return jsonify({
            "success": True,
            "message": f"Successfully enrolled in {len(enrolled_paths)} learning paths",
            "enrolled_paths": enrolled_paths,
            "total_enrolled": len(enrolled_paths)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Dynamic Role Management API Routes
@onboarding_bp.route('/roles', methods=['GET'])
def get_roles():
    """Get all roles"""
    try:
        from agent.dynamic_role_manager import DynamicRoleManager
        manager = DynamicRoleManager()
        roles = manager.get_all_roles()

        return jsonify({
            "success": True,
            "data": [{"role_id": role.role_id, "role_name": role.role_name,
                     "department": role.department, "level": role.level,
                     "skills_count": len(role.skills)} for role in roles]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@onboarding_bp.route('/roles', methods=['POST'])
def create_role():
    """Create new role"""
    try:
        from agent.dynamic_role_manager import DynamicRoleManager
        data = request.get_json() or {}

        required_fields = ['role_name', 'department', 'level', 'skills']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        manager = DynamicRoleManager()
        role_id = manager.create_role(
            role_name=data['role_name'],
            department=data['department'],
            level=data['level'],
            skills=data['skills'],
            description=data.get('description', ''),
            responsibilities=data.get('responsibilities', [])
        )

        return jsonify({
            "success": True,
            "message": "Role created successfully",
            "role_id": role_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@onboarding_bp.route('/roles/<role_id>', methods=['GET'])
def get_role(role_id):
    """Get specific role"""
    try:
        from agent.dynamic_role_manager import DynamicRoleManager
        manager = DynamicRoleManager()
        role = manager.get_role_by_id(role_id)

        if not role:
            return jsonify({"success": False, "error": "Role not found"}), 404

        return jsonify({
            "success": True,
            "data": {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "department": role.department,
                "level": role.level,
                "skills": [{"skill_name": s.skill_name, "required_level": s.required_level,
                           "importance": s.importance, "category": s.category} for s in role.skills],
                "description": role.description,
                "responsibilities": role.responsibilities
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@onboarding_bp.route('/roles/<role_id>', methods=['PUT'])
def update_role(role_id):
    """Update existing role"""
    try:
        from agent.dynamic_role_manager import DynamicRoleManager
        data = request.get_json() or {}
        manager = DynamicRoleManager()
        success = manager.update_role(role_id, data)

        if not success:
            return jsonify({"success": False, "error": "Role not found or update failed"}), 404

        return jsonify({
            "success": True,
            "message": "Role updated successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@onboarding_bp.route('/roles/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    """Delete role"""
    try:
        from agent.dynamic_role_manager import DynamicRoleManager
        manager = DynamicRoleManager()
        success = manager.delete_role(role_id)

        if not success:
            return jsonify({"success": False, "error": "Role not found"}), 404

        return jsonify({
            "success": True,
            "message": "Role deleted successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@onboarding_bp.route('/departments/<department>/roles', methods=['GET'])
def get_department_roles(department):
    """Get roles for a department"""
    try:
        from agent.dynamic_role_manager import DynamicRoleManager
        manager = DynamicRoleManager()
        roles = manager.get_roles_by_department(department)

        return jsonify({
            "success": True,
            "data": [{"role_id": role.role_id, "role_name": role.role_name,
                     "level": role.level, "skills_count": len(role.skills)} for role in roles]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
