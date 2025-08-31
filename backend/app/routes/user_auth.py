from flask import Blueprint, jsonify, request
import os
from werkzeug.security import generate_password_hash, check_password_hash
from ..services.data_access import _read_json, _write_json
from datetime import datetime, timedelta
import uuid
from typing import Any, Dict, Optional, List
import time
import re
import html
from ..services.department import add_manager_to_department

user_auth_bp = Blueprint('user_auth', __name__)

# Prefer the project's top-level `data/` directory so there's a single source
# of truth for user records. The file is located at ../../../../data from
# this file (backend/app/routes/... -> project root/data)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
SESSIONS_FILE = os.path.join(DATA_DIR, 'sessions.json')
RATE_LIMIT_FILE = os.path.join(DATA_DIR, 'rate_limits.json')

# Rate limiting configuration
MAX_LOGIN_ATTEMPTS = 5
RATE_LIMIT_WINDOW = 300  # 5 minutes in seconds

# Helper functions

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def load_users() -> Dict[str, Any]:
    return _read_json(USERS_FILE, {})

def save_users(data: Dict[str, Any]) -> None:
    _write_json(USERS_FILE, data)

def load_sessions() -> Dict[str, Any]:
    return _read_json(SESSIONS_FILE, {})

def save_sessions(data: Dict[str, Any]) -> None:
    _write_json(SESSIONS_FILE, data)

def load_rate_limits() -> Dict[str, Any]:
    return _read_json(RATE_LIMIT_FILE, {})

def save_rate_limits(data: Dict[str, Any]) -> None:
    _write_json(RATE_LIMIT_FILE, data)

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP address has exceeded rate limit for login attempts"""
    rate_limits = load_rate_limits()
    current_time = time.time()
    
    # Clean old entries
    rate_limits = {
        ip: data for ip, data in rate_limits.items()
        if current_time - data.get('first_attempt', 0) < RATE_LIMIT_WINDOW
    }
    
    ip_data = rate_limits.get(ip_address, {'attempts': 0, 'first_attempt': current_time})
    
    if ip_data['attempts'] >= MAX_LOGIN_ATTEMPTS:
        return False
    
    return True

def record_failed_attempt(ip_address: str) -> None:
    """Record a failed login attempt"""
    rate_limits = load_rate_limits()
    current_time = time.time()
    
    if ip_address not in rate_limits:
        rate_limits[ip_address] = {'attempts': 1, 'first_attempt': current_time}
    else:
        # If outside rate limit window, reset
        if current_time - rate_limits[ip_address].get('first_attempt', 0) >= RATE_LIMIT_WINDOW:
            rate_limits[ip_address] = {'attempts': 1, 'first_attempt': current_time}
        else:
            rate_limits[ip_address]['attempts'] += 1
    
    save_rate_limits(rate_limits)

def reset_rate_limit(ip_address: str) -> None:
    """Reset rate limit for IP on successful login"""
    rate_limits = load_rate_limits()
    if ip_address in rate_limits:
        del rate_limits[ip_address]
        save_rate_limits(rate_limits)

def sanitize_input(value: str) -> str:
    """Sanitize user input to prevent XSS and other attacks"""
    if not isinstance(value, str):
        return str(value)
    
    # Remove potential script tags and other dangerous content
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r'<[^>]+>', '', value)  # Remove HTML tags
    value = html.escape(value)  # Escape HTML entities
    return value.strip()

def validate_email_format(email: str) -> bool:
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def get_next_user_id() -> str:
    """Generate the next sequential user_id in format user_XXX"""
    users = load_users()
    
    # Find the highest existing user number
    max_num = 0
    for user_data in users.values():
        user_id = user_data.get('user_id', '')
        if user_id.startswith('user_') and user_id[5:].isdigit():
            num = int(user_id[5:])
            max_num = max(max_num, num)
    
    return f"user_{max_num + 1:03d}"  # Format as user_001, user_002, etc.

def create_user_if_missing(email: str, password: str, name: Optional[str] = None, roleType: Optional[str] = None, newJoiner: Optional[str] = None, dateOfJoining: Optional[str] = None, role: Optional[str] = None, department: Optional[str] = None, manager: Optional[str] = None, employeeId: Optional[str] = None, gender: Optional[str] = None, college: Optional[str] = None, latestDegree: Optional[str] = None, cgpa: Optional[str] = None, country: Optional[str] = None, city: Optional[str] = None, profilePicture: Optional[str] = None, disabilities: Optional[Any] = None) -> Dict[str, Any]:
    users = load_users()
    key = email.strip().lower()
    
    # Validate email format
    if not validate_email_format(key):
        raise ValueError("Invalid email format")
    
    if key in users:
        return users[key]
    
    # Sanitize inputs
    name = sanitize_input(name or key.split("@")[0])
    roleType = sanitize_input(roleType or "")
    newJoiner = sanitize_input(newJoiner or "")
    dateOfJoining = sanitize_input(dateOfJoining or "")
    role = sanitize_input(role or "")
    department = sanitize_input(department or "")
    manager = sanitize_input(manager or "")
    employeeId = sanitize_input(employeeId or "")
    gender = sanitize_input(gender or "")
    college = sanitize_input(college or "")
    latestDegree = sanitize_input(latestDegree or "")
    cgpa = sanitize_input(cgpa or "")
    country = sanitize_input(country or "")
    city = sanitize_input(city or "")
    profilePicture = sanitize_input(profilePicture or "")

    # disabilities may be a list or a string; preserve list if provided
    if isinstance(disabilities, list):
        sanitized_disabilities = [sanitize_input(str(d)) for d in disabilities]
    else:
        sanitized_disabilities = sanitize_input(disabilities or "")
    
    # Generate consistent sequential user_id
    user_id = get_next_user_id()
    users[key] = {
        "email": key,
        "user_id": user_id,
        "name": name,
        "password_hash": generate_password_hash(password),
        "created_at": now_iso(),
        "roleType": roleType,
        "newJoiner": newJoiner,
        "dateOfJoining": dateOfJoining,
        "profile": {
            "role": role,
            "department": department,
            "manager": manager,
            "preferences": {},
            # Onboarding / profile fields persisted from get-started
            "employeeId": employeeId,
            "gender": gender,
            "college": college,
            "latestDegree": latestDegree,
            "cgpa": cgpa,
            "country": country,
            "city": city,
            "profilePicture": profilePicture,
            "disabilities": sanitized_disabilities,
        },
    }
    save_users(users)

    # If manager was provided, try to look up the manager (by email key or user_id)
    # and append this new user's id to the manager's profile.reports list.
    try:
        mgr_key = (manager or "").strip().lower()
        if mgr_key:
            # Reload users to ensure we have the latest state
            users = load_users()
            for m_email, m_data in users.items():
                try:
                    # Normalize manager name for comparison if provided
                    m_name_key = (m_data.get('name') or '').strip().lower()
                    # Match manager by email key, name, or user_id
                    if m_email == mgr_key or m_name_key == mgr_key or m_data.get('user_id') == mgr_key:
                        if 'profile' not in m_data:
                            m_data['profile'] = {}
                        reports = m_data['profile'].get('reports', [])
                        if not isinstance(reports, list):
                            reports = [reports] if reports else []
                        if user_id not in reports:
                            reports.append(user_id)
                            m_data['profile']['reports'] = reports
                            # Persist manager update
                            save_users(users)
                        break
                except Exception:
                    # Skip problematic manager entries but continue
                    continue
    except Exception as e:
        # Don't fail user creation if manager update fails; log and continue
        print(f"Warning: failed to update manager's reports for manager={manager}: {e}")

    # Create corresponding dashboard entry
    create_user_dashboard_entry(user_id)
    
    # Auto-assign default learning paths for new users
    try:
        assign_default_learning_paths(user_id)
    except Exception as e:
        # Log error but don't fail user creation
        print(f"Warning: Failed to assign default learning paths for user {user_id}: {e}")
    
    # Auto-assign department learning paths if department is provided
    if department:
        try:
            assign_department_learning_paths(user_id, department)
        except Exception as e:
            # Log error but don't fail user creation
            print(f"Warning: Failed to assign department learning paths for user {user_id}: {e}")

    # If the user is a manager (roleType or profile.role contains manager), add their name to the department.managers list
    try:
        is_manager = False
        if roleType and 'manager' in roleType.strip().lower():
            is_manager = True
        if role and 'manager' in (role or '').strip().lower():
            is_manager = True
        # Also consider titles like 'VP', 'Director' as management
        if role and any(t in (role or '').strip().lower() for t in ['vp', 'director', 'head']):
            is_manager = True

        if is_manager and department:
            try:
                add_manager_to_department(department, name or users[key].get('name'))
            except Exception as e:
                print(f"Warning: failed to add manager to department for {email}: {e}")
    except Exception:
        pass
    
    return users[key]

def assign_default_learning_paths(user_id: str) -> None:
    """Assign default soft skills learning paths to new users and store in enrollments"""
    try:
        # Load default learning paths
        default_paths_file = os.path.join(DATA_DIR, 'default_learning_paths.json')
        default_paths = _read_json(default_paths_file, {})

        # Load users to update enrollments
        users = load_users()
        
        # Find user and add enrollments
        user_found = False
        for email, user_data in users.items():
            if user_data.get('user_id') == user_id:
                if 'profile' not in user_data:
                    user_data['profile'] = {}
                
                if 'enrollments' not in user_data['profile']:
                    user_data['profile']['enrollments'] = []
                
                # Add all default learning paths to enrollments
                for path_id in default_paths.keys():
                    enrollment = {
                        'learning_path_id': path_id,
                        'enrolled_at': now_iso(),
                        'status': 'enrolled'
                    }
                    user_data['profile']['enrollments'].append(enrollment)
                
                user_found = True
                break
        
        if not user_found:
            print(f"User {user_id} not found for enrollment assignment")
            return
        
        # Save updated users
        save_users(users)

        # Load learning path progress data
        progress_file = os.path.join(DATA_DIR, 'LearningPathProgress.json')
        progress_data = _read_json(progress_file, [])

        # Create progress entries for all default learning paths
        assigned_paths = []
        for path_id, path_data in default_paths.items():
            # Check if user already has this learning path progress entry
            existing_progress = next(
                (p for p in progress_data if p.get('attributes', {}).get('user_id') == user_id and
                 p.get('attributes', {}).get('learning_path_id') == path_id),
                None
            )

            if not existing_progress:
                # Create new progress entry for this learning path
                new_progress = {
                    "attributes": {
                        "id": f"lpp_{user_id}_{path_id}_{str(uuid.uuid4())[:8]}",
                        "user_id": user_id,
                        "learning_path_id": path_id,
                        "status": "not_started",
                        "progress_percent": 0.0,
                        "modules_completed_count": 0,
                        "modules_total_count": len(path_data.get('modules', [])),
                        "time_invested_minutes": 0,
                        "last_accessed_at": None,
                        "started_at": None,
                        "completed_at": None,
                        "current_module_id": None,
                        "enrolled_at": now_iso(),
                        "is_default": True
                    }
                }
                progress_data.append(new_progress)
                assigned_paths.append(path_id)

        # Save updated progress data
        if assigned_paths:
            _write_json(progress_file, progress_data)
            print(f"Assigned {len(assigned_paths)} default learning paths to user {user_id}: {assigned_paths}")

    except Exception as e:
        print(f"Error assigning default learning paths to user {user_id}: {e}")
        # Don't raise exception to avoid breaking user creation

def assign_department_learning_paths(user_id: str, department: str) -> None:
    """Assign department-specific learning paths to new users"""
    try:
        from ..services.data_access import get_data_file_path
        
        # Load department learning paths
        dept_mapping_file = get_data_file_path('department_learning_paths.json')
        dept_mappings = _read_json(dept_mapping_file, {})
        
        # Get department learning paths
        dept_paths = dept_mappings.get('departments', {}).get(department, [])
        
        if not dept_paths:
            print(f"No department learning paths found for department: {department}")
            return
        
        # Load users to update enrollments
        users = load_users()
        
        # Find user and add department enrollments
        user_found = False
        for email, user_data in users.items():
            if user_data.get('user_id') == user_id:
                if 'profile' not in user_data:
                    user_data['profile'] = {}
                
                if 'enrollments' not in user_data['profile']:
                    user_data['profile']['enrollments'] = []
                
                # Add department learning paths to enrollments
                for dept_path in dept_paths:
                    path_id = dept_path.get('learning_path_id')
                    if path_id:
                        # Check if already enrolled
                        existing_enrollment = next(
                            (e for e in user_data['profile']['enrollments'] 
                             if e.get('learning_path_id') == path_id),
                            None
                        )
                        
                        if not existing_enrollment:
                            enrollment = {
                                'learning_path_id': path_id,
                                'enrolled_at': now_iso(),
                                'status': 'enrolled',
                                'source': 'department'
                            }
                            user_data['profile']['enrollments'].append(enrollment)
                
                user_found = True
                break
        
        if not user_found:
            print(f"User {user_id} not found for department enrollment assignment")
            return
        
        # Save updated users
        save_users(users)

        # Load learning path progress data
        progress_file = os.path.join(DATA_DIR, 'LearningPathProgress.json')
        progress_data = _read_json(progress_file, [])

        # Create progress entries for department learning paths
        assigned_dept_paths = []
        for dept_path in dept_paths:
            path_id = dept_path.get('learning_path_id')
            if path_id:
                # Check if user already has this learning path progress entry
                existing_progress = next(
                    (p for p in progress_data if p.get('attributes', {}).get('user_id') == user_id and
                     p.get('attributes', {}).get('learning_path_id') == path_id),
                    None
                )

                if not existing_progress:
                    # Create new progress entry for this learning path
                    new_progress = {
                        "attributes": {
                            "id": f"lpp_{user_id}_{path_id}_{str(uuid.uuid4())[:8]}",
                            "user_id": user_id,
                            "learning_path_id": path_id,
                            "status": "not_started",
                            "progress_percent": 0.0,
                            "modules_completed_count": 0,
                            "modules_total_count": 0,  # Will be updated when learning path data is available
                            "time_invested_minutes": 0,
                            "last_accessed_at": None,
                            "started_at": None,
                            "completed_at": None,
                            "current_module_id": None,
                            "enrolled_at": now_iso(),
                            "is_department": True
                        }
                    }
                    progress_data.append(new_progress)
                    assigned_dept_paths.append(path_id)

        # Save updated progress data
        if assigned_dept_paths:
            _write_json(progress_file, progress_data)
            print(f"Assigned {len(assigned_dept_paths)} department learning paths to user {user_id}: {assigned_dept_paths}")

    except Exception as e:
        print(f"Error assigning department learning paths to user {user_id}: {e}")

def assign_resume_based_learning_paths(user_id: str) -> None:
    """Assign learning paths based on resume analysis recommendations"""
    try:
        # Load onboarding recommendations
        onboarding_file = os.path.join(DATA_DIR, 'onboarding_recommendations.json')
        onboarding_data = _read_json(onboarding_file, {})
        
        # Get user's recommendations
        user_recommendations = onboarding_data.get('recommendations', {}).get(user_id)
        if not user_recommendations:
            print(f"No onboarding recommendations found for user {user_id}")
            return
        
        recommended_paths = user_recommendations.get('recommended_learning_paths', [])
        if not recommended_paths:
            print(f"No recommended learning paths found for user {user_id}")
            return
        
        # Load users to update enrollments
        users = load_users()
        
        # Find user and add resume-based enrollments
        user_found = False
        for email, user_data in users.items():
            if user_data.get('user_id') == user_id:
                if 'profile' not in user_data:
                    user_data['profile'] = {}
                
                if 'enrollments' not in user_data['profile']:
                    user_data['profile']['enrollments'] = []
                
                # Add resume-based learning paths to enrollments
                for path_id in recommended_paths:
                    # Check if already enrolled
                    existing_enrollment = next(
                        (e for e in user_data['profile']['enrollments'] 
                         if e.get('learning_path_id') == path_id),
                        None
                    )
                    
                    if not existing_enrollment:
                        enrollment = {
                            'learning_path_id': path_id,
                            'enrolled_at': now_iso(),
                            'status': 'enrolled',
                            'source': 'resume_analysis'
                        }
                        user_data['profile']['enrollments'].append(enrollment)
                
                user_found = True
                break
        
        if not user_found:
            print(f"User {user_id} not found for resume-based enrollment assignment")
            return
        
        # Save updated users
        save_users(users)

        # Load learning path progress data
        progress_file = os.path.join(DATA_DIR, 'LearningPathProgress.json')
        progress_data = _read_json(progress_file, [])

        # Create progress entries for resume-based learning paths
        assigned_resume_paths = []
        for path_id in recommended_paths:
            # Check if user already has this learning path progress entry
            existing_progress = next(
                (p for p in progress_data if p.get('attributes', {}).get('user_id') == user_id and
                 p.get('attributes', {}).get('learning_path_id') == path_id),
                None
            )

            if not existing_progress:
                # Create new progress entry for this learning path
                new_progress = {
                    "attributes": {
                        "id": f"lpp_{user_id}_{path_id}_{str(uuid.uuid4())[:8]}",
                        "user_id": user_id,
                        "learning_path_id": path_id,
                        "status": "not_started",
                        "progress_percent": 0.0,
                        "modules_completed_count": 0,
                        "modules_total_count": 0,  # Will be updated when learning path data is available
                        "time_invested_minutes": 0,
                        "last_accessed_at": None,
                        "started_at": None,
                        "completed_at": None,
                        "current_module_id": None,
                        "enrolled_at": now_iso(),
                        "is_resume_based": True
                    }
                }
                progress_data.append(new_progress)
                assigned_resume_paths.append(path_id)

        # Save updated progress data
        if assigned_resume_paths:
            _write_json(progress_file, progress_data)
            print(f"Assigned {len(assigned_resume_paths)} resume-based learning paths to user {user_id}: {assigned_resume_paths}")

    except Exception as e:
        print(f"Error assigning resume-based learning paths to user {user_id}: {e}")

def create_user_dashboard_entry(user_id: str) -> None:
    """Create a default dashboard entry for a new user"""
    dashboard_file = os.path.join(DATA_DIR, 'UserDashboard.json')
    dashboard_data = _read_json(dashboard_file, [])
    
    # Check if dashboard entry already exists
    existing_entry = next((item for item in dashboard_data if item.get('attributes', {}).get('user_id') == user_id), None)
    if existing_entry:
        return  # Dashboard entry already exists
    
    # Create new dashboard entry
    new_dashboard_entry = {
        "attributes": {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "modules_completed": 0,
            "overall_progress_percent": 0.0,
            "time_invested_minutes": 0,
            "quiz_average_percent": 0.0,
            "last_accessed_at": now_iso()
        }
    }
    
    dashboard_data.append(new_dashboard_entry)
    _write_json(dashboard_file, dashboard_data)

def verify_user(email: str, password: str) -> bool:
    users = load_users()
    key = email.strip().lower()
    u = users.get(key)
    if not u:
        return False
    
    # Check if user has a plain text password field
    if "password" in u and u["password"] == password:
        return True
    
    # Check hashed password
    if "password_hash" in u:
        try:
            return check_password_hash(u["password_hash"], password)
        except Exception:
            # If password_hash is actually plain text (like admin user), check directly
            return u["password_hash"] == password
    
    return False

def new_session(email: str) -> str:
    sessions = load_sessions()
    token = uuid.uuid4().hex
    sessions[token] = {
        "email": email.strip().lower(),
        "created_at": now_iso(),
    }
    save_sessions(sessions)
    return token

def get_session_user(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    sessions = load_sessions()
    info = sessions.get(token)
    if not info:
        return None
    users = load_users()
    return users.get(info["email"])

@user_auth_bp.route('/sign-in', methods=['POST'])
def sign_in():
    payload = request.get_json(force=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    name = payload.get("name")
    
    # Get client IP for rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
    
    # Check rate limiting
    if not check_rate_limit(client_ip):
        return jsonify({"error": "Too many login attempts. Please try again in 5 minutes."}), 429
    
    # Input validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not validate_email_format(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Enhanced password validation
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Sanitize inputs
    email = sanitize_input(email)
    if name:
        name = sanitize_input(name)
    
    users = load_users()

    # Primary lookup by normalized email key
    user = users.get(email)

    # Secondary lookup: some legacy/admin records may be stored under a
    # different key; search values by their embedded email field and
    # re-key the user to the normalized email to avoid duplicate creation.
    if user is None:
        found_key = None
        for k, u in list(users.items()):
            try:
                if (u.get("email") or "").strip().lower() == email:
                    user = u
                    found_key = k
                    break
            except Exception:
                continue
        if user is not None and found_key is not None and found_key != email:
            users[email] = user
            del users[found_key]
            save_users(users)

    if user is None:
        # Only auto-create for specific endpoints like get-started, not general sign-in
        record_failed_attempt(client_ip)
        return jsonify({"error": "Invalid email or password"}), 401
    else:
        # Ensure users file is up-to-date before verifying
        save_users(users)
        if not verify_user(email, password):
            record_failed_attempt(client_ip)
            return jsonify({"error": "Invalid email or password"}), 401
        reset_rate_limit(client_ip)  # Reset on successful login
    
    token = new_session(email)
    # Ensure manager is listed in department managers array for both new and existing users
    try:
        is_manager = False
        if user.get('roleType') and 'manager' in (user.get('roleType') or '').strip().lower():
            is_manager = True
        if user.get('profile', {}).get('role') and 'manager' in (user.get('profile', {}).get('role') or '').strip().lower():
            is_manager = True
        if user.get('profile', {}).get('role') and any(t in (user.get('profile', {}).get('role') or '').strip().lower() for t in ['vp', 'director', 'head']):
            is_manager = True

        department_name = user.get('profile', {}).get('department')
        if is_manager and department_name:
            try:
                add_manager_to_department(department_name, user.get('name'))
            except Exception as e:
                print(f"Warning: failed to add manager to department for {email}: {e}")
    except Exception:
        pass
    user_obj = {
        "email": user["email"],
        "name": user.get("name"),
        "roleType": user.get("roleType"),
        "newJoiner": user.get("newJoiner"),
        "dateOfJoining": user.get("dateOfJoining"),
        "role": user.get("profile", {}).get("role", ""),
        "department": user.get("profile", {}).get("department", ""),
    }
    if "user_id" in user:
        user_obj["user_id"] = user["user_id"]
    return jsonify({
        "token": token,
        "user": user_obj,
    })

@user_auth_bp.route('/get-started', methods=['POST'])
def get_started():
    payload = request.get_json(force=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    name = payload.get("name")
    
    # Get client IP for rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
    
    # Check rate limiting
    if not check_rate_limit(client_ip):
        return jsonify({"error": "Too many registration attempts. Please try again in 5 minutes."}), 429
    
    # Input validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not validate_email_format(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Enhanced password validation
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Sanitize inputs
    email = sanitize_input(email)
    if name:
        name = sanitize_input(name)
    
    users = load_users()
    user = users.get(email)
    
    if user is not None:
        # User exists, verify credentials
        if not verify_user(email, password):
            record_failed_attempt(client_ip)
            return jsonify({"error": "Email already exists with different password"}), 409
        reset_rate_limit(client_ip)
    else:
        # Create new user for get-started flow
        try:
            user = create_user_if_missing(
                email, password, name,
                sanitize_input(payload.get("roleType", "")),
                sanitize_input(payload.get("newJoiner", "")),
                sanitize_input(payload.get("dateOfJoining", "")),
                sanitize_input(payload.get("role", "")),
                sanitize_input(payload.get("department", "")),
                sanitize_input(payload.get("manager", "")),
                sanitize_input(payload.get("employeeId", "")),
                sanitize_input(payload.get("gender", "")),
                sanitize_input(payload.get("college", "")),
                sanitize_input(payload.get("latestDegree", "")),
                sanitize_input(payload.get("cgpa", "")),
                sanitize_input(payload.get("country", "")),
                sanitize_input(payload.get("city", "")),
                sanitize_input(payload.get("profilePicture", "")),
                payload.get("disabilities")
            )
            reset_rate_limit(client_ip)
        except ValueError as e:
            record_failed_attempt(client_ip)
            return jsonify({"error": str(e)}), 400
    
    token = new_session(email)
    user_obj = {
        "email": user["email"],
        "name": user.get("name"),
        "roleType": user.get("roleType"),
        "newJoiner": user.get("newJoiner"),
        "dateOfJoining": user.get("dateOfJoining"),
        "role": user.get("profile", {}).get("role", ""),
        "department": user.get("profile", {}).get("department", ""),
    # return persisted onboarding/profile fields when available
    "employeeId": user.get("profile", {}).get("employeeId"),
    "gender": user.get("profile", {}).get("gender"),
    "college": user.get("profile", {}).get("college"),
    "latestDegree": user.get("profile", {}).get("latestDegree"),
    "cgpa": user.get("profile", {}).get("cgpa"),
    "country": user.get("profile", {}).get("country"),
    "city": user.get("profile", {}).get("city"),
    "profilePicture": user.get("profile", {}).get("profilePicture"),
    "disabilities": user.get("profile", {}).get("disabilities"),
    }
    if "user_id" in user:
        user_obj["user_id"] = user["user_id"]
    return jsonify({
        "token": token,
        "user": user_obj,
    })

@user_auth_bp.route('/me', methods=['GET'])
def me():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer", "").strip()
    user = get_session_user(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"user": user})

@user_auth_bp.route('/learning-style', methods=['POST'])
def save_learning_style():
    """Save user's learning style (simplified)"""
    payload = request.get_json(force=True) or {}
    user_id = payload.get("user_id")
    learning_style = payload.get("learning_style")
    
    if not user_id or not learning_style:
        return jsonify({"error": "user_id and learning_style are required"}), 400
    
    # Find user by user_id and update their profile
    users = load_users()
    user_found = False
    
    for email, user_data in users.items():
        if user_data.get('user_id') == user_id:
            if 'profile' not in user_data:
                user_data['profile'] = {}
            
            # Just store the learning style simply
            user_data['profile']['learning_style'] = learning_style
            user_found = True
            break
    
    if not user_found:
        return jsonify({"error": "User not found"}), 404
    
    save_users(users)
    
    return jsonify({
        "success": True,
        "message": "Learning style saved successfully"
    })



@user_auth_bp.route('/user/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Get user information by user_id"""
    try:
        users = load_users()
        
        # Find user by user_id
        for email, user_data in users.items():
            if user_data.get('user_id') == user_id:
                # Return user info without sensitive data
                user_info = {
                    "user_id": user_data.get("user_id"),
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "roleType": user_data.get("roleType"),
                    "newJoiner": user_data.get("newJoiner"),
                    "dateOfJoining": user_data.get("dateOfJoining"),
                    "department": user_data.get("profile", {}).get("department", ""),
                    "role": user_data.get("profile", {}).get("role", ""),
                }
                return jsonify({"success": True, "user": user_info})
        
        return jsonify({"success": False, "error": "User not found"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
