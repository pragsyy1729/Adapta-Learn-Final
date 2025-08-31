from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime, timezone

dashboard_bp = Blueprint('dashboard', __name__)

def get_user_learning_progress(user_id: str) -> dict:
    """Get comprehensive learning progress for a user"""
    try:
        # Load learning path progress
        progress_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/LearningPathProgress.json')
        with open(progress_path, 'r') as f:
            progress_data = json.load(f)
        
        # Load module progress
        module_progress_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/ModuleProgress.json')
        with open(module_progress_path, 'r') as f:
            module_progress_data = json.load(f)
        
        # Load user dashboard data
        dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/UserDashboard.json')
        with open(dashboard_path, 'r') as f:
            dashboard_data = json.load(f)
        
        # Get user's learning path progress
        user_paths = [p['attributes'] for p in progress_data if p['attributes']['user_id'] == user_id]
        
        # Get user's module progress
        user_modules = [m['attributes'] for m in module_progress_data if m['attributes']['user_id'] == user_id]
        
        # Get user's dashboard stats
        user_dashboard = next((d['attributes'] for d in dashboard_data if d['attributes']['user_id'] == user_id), None)
        
        # Calculate overall progress
        overall_progress = 0
        total_modules = 0
        completed_modules = 0
        total_time = 0
        
        if user_paths:
            # Calculate weighted average progress
            total_weight = sum(path.get('modules_total_count', 0) for path in user_paths)
            if total_weight > 0:
                weighted_progress = sum(
                    (path.get('progress_percent', 0) / 100) * path.get('modules_total_count', 0) 
                    for path in user_paths
                )
                overall_progress = (weighted_progress / total_weight) * 100
            
            total_modules = sum(path.get('modules_total_count', 0) for path in user_paths)
            completed_modules = sum(path.get('modules_completed_count', 0) for path in user_paths)
            total_time = sum(path.get('time_invested_minutes', 0) for path in user_paths)
        
        # Use dashboard data if available (more accurate)
        if user_dashboard:
            overall_progress = user_dashboard.get('overall_progress_percent', overall_progress)
            completed_modules = user_dashboard.get('modules_completed', completed_modules)
            total_time = user_dashboard.get('time_invested_minutes', total_time)
        
        # Get current learning activities
        current_activities = []
        for path in user_paths:
            if path.get('status') == 'in_progress' and path.get('current_module_id'):
                current_activities.append({
                    'type': 'learning_path',
                    'path_id': path.get('learning_path_id'),
                    'current_module': path.get('current_module_id'),
                    'progress': path.get('progress_percent', 0)
                })
        
        return {
            'overall_progress_percent': round(overall_progress, 1),
            'modules_completed': completed_modules,
            'total_modules': total_modules,
            'time_invested_minutes': total_time,
            'learning_paths_count': len(user_paths),
            'current_activities': current_activities,
            'last_activity': max(
                (path.get('last_accessed_at') for path in user_paths if path.get('last_accessed_at')),
                default=None
            )
        }
        
    except Exception as e:
        print(f"Error getting user progress for {user_id}: {e}")
        return {
            'overall_progress_percent': 0,
            'modules_completed': 0,
            'total_modules': 0,
            'time_invested_minutes': 0,
            'learning_paths_count': 0,
            'current_activities': [],
            'last_activity': None
        }

def get_user_gamification_data(user_id: str) -> dict:
    """Get user's gamification data including badges and learning metrics"""
    gamification_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/user_gamification.json')
    try:
        with open(gamification_path, 'r') as f:
            gamification_data = json.load(f)
        
        user_gamification = gamification_data.get(user_id, {})
        
        # Calculate "real learner" score based on multiple factors
        badges_count = len(user_gamification.get('badges', []))
        current_streak = user_gamification.get('current_streak', 0)
        total_points = user_gamification.get('total_points', 0)
        achievements = user_gamification.get('achievements', {})
        
        # Real learner score calculation (0-100)
        # Factors: badges (30%), streak (25%), points (20%), activity (15%), consistency (10%)
        badge_score = min(badges_count * 10, 30)  # Max 30 points for badges
        streak_score = min(current_streak * 2, 25)  # Max 25 points for streak
        points_score = min(total_points / 50, 20)  # Max 20 points for points (1000 points = 20)
        activity_score = min(achievements.get('modules_completed', 0) * 1.5, 15)  # Max 15 points for activity
        consistency_score = min(achievements.get('average_score', 0) / 10, 10)  # Max 10 points for consistency
        
        real_learner_score = badge_score + streak_score + points_score + activity_score + consistency_score
        
        # Determine learner type
        if real_learner_score >= 80:
            learner_type = "Dedicated Learner"
            learner_description = "Highly engaged and consistent learner"
        elif real_learner_score >= 60:
            learner_type = "Active Learner"
            learner_description = "Regularly engaged with learning activities"
        elif real_learner_score >= 40:
            learner_type = "Moderate Learner"
            learner_description = "Somewhat engaged but could be more active"
        elif real_learner_score >= 20:
            learner_type = "Casual Learner"
            learner_description = "Occasional learning activity"
        else:
            learner_type = "New Learner"
            learner_description = "Just getting started with learning"
        
        return {
            'badges_count': badges_count,
            'badges': user_gamification.get('badges', []),
            'current_streak': current_streak,
            'total_points': total_points,
            'real_learner_score': round(real_learner_score, 1),
            'learner_type': learner_type,
            'learner_description': learner_description,
            'achievements': achievements,
            'last_activity': user_gamification.get('last_activity'),
            'current_level': user_gamification.get('current_level', 1)
        }
    except Exception as e:
        print(f"Error getting gamification data for {user_id}: {e}")
        return {
            'badges_count': 0,
            'badges': [],
            'current_streak': 0,
            'total_points': 0,
            'real_learner_score': 0,
            'learner_type': 'Unknown',
            'learner_description': 'No gamification data available',
            'achievements': {},
            'last_activity': None,
            'current_level': 1
        }

def get_user_role_type(user_id: str) -> str:
    """Get user's roleType from users.json"""
    users_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/users.json')
    try:
        with open(users_path, 'r') as f:
            users_data = json.load(f)
        
        # Find user by user_id
        for email, user_info in users_data.items():
            if user_info.get('user_id') == user_id:
                role_type = user_info.get('roleType', '').lower()
                # Check if it's a hiring manager (Director level in a department)
                if role_type == 'director':
                    return 'hiring_manager'
                return role_type
        return 'learner'  # Default to learner if not found
    except Exception:
        return 'learner'

def get_manager_dashboard_data(user_id: str) -> dict:
    """Generate manager-specific dashboard data"""
    users_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/users.json')
    
    try:
        with open(users_path, 'r') as f:
            users_data = json.load(f)
        
        # Find manager's details
        manager_info = None
        for email, user_info in users_data.items():
            if user_info.get('user_id') == user_id:
                manager_info = user_info
                break
        
        if not manager_info:
            return {}
        
        # Count direct reports
        direct_reports = []
        reports_data = manager_info.get('profile', {}).get('reports', [])
        
        # Calculate enhanced KPIs for new joiners
        new_joiners_enhanced = []
        total_new_joiners_progress = 0
        at_risk_count = 0
        completed_onboarding_count = 0
        
        for report_id in reports_data:
            for email, user_info in users_data.items():
                if user_info.get('user_id') == report_id:
                    # Check if this is a new joiner
                    is_new_joiner = user_info.get('newJoiner', '').lower() in ['yes', 'true']
                    
                    # Always add to direct_reports (all team members)
                    report_data = {
                        'user_id': report_id,
                        'name': user_info.get('name', ''),
                        'email': user_info.get('email', ''),
                        'roleType': user_info.get('roleType', ''),
                        'newJoiner': user_info.get('newJoiner', ''),
                        'dateOfJoining': user_info.get('dateOfJoining', ''),
                        'department': user_info.get('profile', {}).get('department', ''),
                        'progress': get_user_learning_progress(report_id),
                        'status': 'active'
                    }
                    direct_reports.append(report_data)
                    
                    # Only add to new_joiners_enhanced if this is a new joiner
                    if is_new_joiner:
                        join_date = user_info.get('dateOfJoining', '')
                        progress_data = report_data['progress']  # Use the same progress data
                        progress_percent = progress_data.get('overall_progress_percent', 0)
                        
                        # Calculate additional metrics
                        days_since_joining = 0
                        is_at_risk = False
                        if join_date:
                            try:
                                join_datetime = datetime.fromisoformat(join_date.replace('Z', '+00:00'))
                                now = datetime.now(timezone.utc)
                                days_since_joining = (now - join_datetime).days
                                
                                # Risk assessment: low progress after 7+ days
                                is_at_risk = progress_percent < 30 and days_since_joining > 7
                                if is_at_risk:
                                    at_risk_count += 1
                            except:
                                days_since_joining = 0
                        
                        # Check if onboarding is complete (80%+)
                        if progress_percent >= 80:
                            completed_onboarding_count += 1
                        
                        total_new_joiners_progress += progress_percent
                        
                        # Get gamification data for the user
                        gamification_data = get_user_gamification_data(report_id)
                        
                        enhanced_joiner_data = {
                            'user_id': report_id,
                            'name': user_info.get('name', ''),
                            'email': user_info.get('email', ''),
                            'roleType': user_info.get('roleType', ''),
                            'newJoiner': user_info.get('newJoiner', ''),
                            'dateOfJoining': join_date,
                            'department': user_info.get('profile', {}).get('department', ''),
                            'progress': progress_data,
                            'days_since_joining': days_since_joining,
                            'is_at_risk': is_at_risk,
                            'last_accessed_days': None,  # Will be calculated from progress data
                            'expected_completion_days': max(0, 30 - days_since_joining),  # Assuming 30-day onboarding
                            'progress_rate_weekly': (progress_percent / max(days_since_joining, 1) * 7) if days_since_joining > 0 else 0,
                            'status': 'active',
                            # Add gamification data
                            'badges_count': gamification_data['badges_count'],
                            'real_learner_score': gamification_data['real_learner_score'],
                            'learner_type': gamification_data['learner_type'],
                            'learner_description': gamification_data['learner_description'],
                            'current_streak': gamification_data['current_streak'],
                            'total_points': gamification_data['total_points']
                        }
                        
                        new_joiners_enhanced.append(enhanced_joiner_data)
                    break
        
        # Calculate averages
        avg_new_joiner_progress = 0
        if new_joiners_enhanced:
            avg_new_joiner_progress = total_new_joiners_progress / len(new_joiners_enhanced)
        
        # Calculate KPIs for all direct reports
        total_team_members = len(direct_reports)
        avg_progress = 0
        completed_modules_total = 0
        
        if direct_reports:
            avg_progress = sum(report['progress'].get('overall_progress_percent', 0) for report in direct_reports) / len(direct_reports)
            completed_modules_total = sum(report['progress'].get('modules_completed', 0) for report in direct_reports)
        
        # Calculate onboarding completion rate for new joiners
        onboarding_completion_rate = 0
        if new_joiners_enhanced:
            completed_onboarding = sum(1 for nj in new_joiners_enhanced if nj['progress'].get('overall_progress_percent', 0) >= 80)
            onboarding_completion_rate = (completed_onboarding / len(new_joiners_enhanced)) * 100
        
        # Update return data with enhanced metrics
        return {
            'team_size': total_team_members,
            'direct_reports': direct_reports,
            'new_joiners': new_joiners_enhanced,  # Use enhanced data
            'department': manager_info.get('profile', {}).get('department', ''),
            'team_name': manager_info.get('profile', {}).get('team', ''),
            'manager_level': manager_info.get('profile', {}).get('level', ''),
            'new_joiners_count': len(new_joiners_enhanced),
            'new_joiners_at_risk': at_risk_count,
            'new_joiners_completed': completed_onboarding_count,
            'average_new_joiner_progress': round(avg_new_joiner_progress, 1),
            'new_joiners_completion_rate': round((completed_onboarding_count / max(len(new_joiners_enhanced), 1)) * 100, 1),
            'average_team_progress': round(avg_progress, 1),
            'total_completed_modules': completed_modules_total,
            'onboarding_completion_rate': round(onboarding_completion_rate, 1),
            'explanations': {
                'team_size': 'Number of direct reports under this manager',
                'new_joiners_count': 'Number of team members who are new joiners',
                'new_joiners_at_risk': 'New joiners with low progress who may need intervention',
                'new_joiners_completed': 'New joiners who have completed 80%+ of onboarding',
                'average_new_joiner_progress': 'Average onboarding progress across new joiners (%)',
                'new_joiners_completion_rate': 'Percentage of new joiners who have completed 80%+ of onboarding',
                'average_team_progress': 'Average learning progress across all team members (%)',
                'total_completed_modules': 'Total modules completed by team members',
                'onboarding_completion_rate': 'Percentage of new joiners who have completed 80%+ of onboarding'
            }
        }
    except Exception as e:
        return {'error': str(e)}

def get_hiring_manager_dashboard_data(user_id: str) -> dict:
    """Generate hiring manager-specific dashboard data"""
    users_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/users.json')
    
    try:
        with open(users_path, 'r') as f:
            users_data = json.load(f)
        
        # Find hiring manager's details
        hiring_manager_info = None
        for email, user_info in users_data.items():
            if user_info.get('user_id') == user_id:
                hiring_manager_info = user_info
                break
        
        if not hiring_manager_info:
            return {}
        
        # Get hiring manager's department
        hm_department = hiring_manager_info.get('profile', {}).get('department', '')
        
        # Find all managers in the same department
        department_managers = []
        department_new_joiners = []
        
        for email, user_info in users_data.items():
            user_dept = user_info.get('profile', {}).get('department', '')
            if user_dept == hm_department:
                role_type = user_info.get('roleType', '').lower()
                
                if role_type == 'manager' or role_type == 'director':
                    # This is a manager in the department
                    manager_reports = user_info.get('profile', {}).get('reports', [])
                    manager_new_joiners = []
                    
                    # Get new joiners under this manager
                    for report_id in manager_reports:
                        for rep_email, rep_info in users_data.items():
                            if rep_info.get('user_id') == report_id:
                                is_new_joiner = rep_info.get('newJoiner', '').lower() in ['yes', 'true']
                                if is_new_joiner:
                                    manager_new_joiners.append({
                                        'user_id': report_id,
                                        'name': rep_info.get('name', ''),
                                        'progress': get_user_learning_progress(report_id)
                                    })
                                break
                    
                    department_managers.append({
                        'user_id': user_info.get('user_id'),
                        'name': user_info.get('name', ''),
                        'email': user_info.get('email', ''),
                        'role': user_info.get('profile', {}).get('role', ''),
                        'team': user_info.get('profile', {}).get('team', ''),
                        'new_joiners_count': len(manager_new_joiners),
                        'new_joiners': manager_new_joiners,
                        'avg_team_progress': round(
                            sum(nj['progress'].get('overall_progress_percent', 0) for nj in manager_new_joiners) / 
                            len(manager_new_joiners) if manager_new_joiners else 0, 1
                        )
                    })
                    
                    # Add to overall department new joiners
                    department_new_joiners.extend(manager_new_joiners)
        
        # Calculate department-wide KPIs
        total_dept_new_joiners = len(department_new_joiners)
        avg_dept_progress = 0
        if department_new_joiners:
            avg_dept_progress = sum(nj['progress'].get('overall_progress_percent', 0) 
                                  for nj in department_new_joiners) / len(department_new_joiners)
        
        # Calculate onboarding completion rate
        onboarding_completion_rate = 0
        if department_new_joiners:
            completed_onboarding = sum(1 for nj in department_new_joiners 
                                     if nj['progress'].get('overall_progress_percent', 0) >= 80)
            onboarding_completion_rate = (completed_onboarding / len(department_new_joiners)) * 100
        
        return {
            'department': hm_department,
            'department_managers': department_managers,
            'department_new_joiners': department_new_joiners,
            'total_dept_new_joiners': total_dept_new_joiners,
            'avg_dept_progress': round(avg_dept_progress, 1),
            'onboarding_completion_rate': round(onboarding_completion_rate, 1),
            'managers_count': len(department_managers),
            'explanations': {
                'department': 'Department this hiring manager oversees',
                'total_dept_new_joiners': 'Total new joiners across all teams in the department',
                'avg_dept_progress': 'Average onboarding progress across department (%)',
                'onboarding_completion_rate': 'Percentage of new joiners who have completed 80%+ of onboarding',
                'managers_count': 'Number of managers in the department'
            }
        }
    except Exception as e:
        return {'error': str(e)}

def get_admin_dashboard_data(user_id: str) -> dict:
    """Generate admin-specific dashboard data"""
    users_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/users.json')
    
    try:
        with open(users_path, 'r') as f:
            users_data = json.load(f)
        
        # Calculate organization-wide metrics
        total_users = len(users_data)
        managers = sum(1 for user in users_data.values() if user.get('roleType', '').lower() == 'manager')
        new_joiners = sum(1 for user in users_data.values() if user.get('newJoiner', '').lower() in ['yes', 'true'])
        departments = {}
        
        for user in users_data.values():
            dept = user.get('profile', {}).get('department', 'Unknown')
            if dept in departments:
                departments[dept] += 1
            else:
                departments[dept] = 1
        
        return {
            'total_users': total_users,
            'total_managers': managers,
            'total_new_joiners': new_joiners,
            'departments': departments,
            'active_learning_paths': 8,  # TODO: Calculate from actual data
            'completion_rate': 78.5,  # TODO: Calculate from actual data
            'average_onboarding_time': 6.2,  # TODO: Calculate from actual data
            'system_health': 'Good',
            'explanations': {
                'total_users': 'Total number of users in the system',
                'total_managers': 'Number of users with Manager role',
                'total_new_joiners': 'Number of users marked as new joiners',
                'departments': 'Distribution of users across departments',
                'active_learning_paths': 'Number of learning paths currently active',
                'completion_rate': 'Overall learning path completion rate (%)',
                'average_onboarding_time': 'Average time to complete onboarding (weeks)',
                'system_health': 'Overall system status'
            }
        }
    except Exception as e:
        return {'error': str(e)}

def get_learner_dashboard_data(user_id: str) -> dict:
    """Generate learner-specific dashboard data (original functionality)"""
    dashboards_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/UserDashboard.json')
    try:
        with open(dashboards_path, 'r') as f:
            dashboards = json.load(f)
        
        dashboard = next((d['attributes'] for d in dashboards if d['attributes']['user_id'] == user_id), None)
        if not dashboard:
            return {'error': 'UserDashboard not found'}
        
        return {
            'modules_completed': dashboard['modules_completed'],
            'overall_progress_percent': dashboard['overall_progress_percent'],
            'time_invested_minutes': dashboard['time_invested_minutes'],
            'quiz_average_percent': dashboard['quiz_average_percent'],
            'explanations': {
                'modules_completed': 'Number of modules completed in all enrolled learning paths.',
                'overall_progress_percent': 'Weighted average progress across all modules.',
                'time_invested_minutes': 'Total time spent on learning activities (minutes).',
                'quiz_average_percent': 'Average score across all quizzes (0-100%).'
            }
        }
    except Exception as e:
        return {'error': str(e)}

@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # Get user's role type
    role_type = get_user_role_type(user_id)
    
    # Return appropriate dashboard based on role
    if role_type == 'hiring_manager':
        dashboard_data = get_hiring_manager_dashboard_data(user_id)
    elif role_type == 'manager':
        dashboard_data = get_manager_dashboard_data(user_id)
    elif role_type == 'admin':
        dashboard_data = get_admin_dashboard_data(user_id)
    else:  # Default to learner dashboard (Associate, learner, or any other role)
        dashboard_data = get_learner_dashboard_data(user_id)
    
    if 'error' in dashboard_data:
        return jsonify(dashboard_data), 404 if dashboard_data['error'] == 'UserDashboard not found' else 500
    
    # Add role type to response
    dashboard_data['user_role'] = role_type
    dashboard_data['dashboard_type'] = f"{role_type}_dashboard"
    
    return jsonify(dashboard_data)

@dashboard_bp.route('/user-progress/<user_id>', methods=['GET'])
def get_user_progress_endpoint(user_id):
    """API endpoint to get detailed progress for a specific user"""
    progress_data = get_user_learning_progress(user_id)
    return jsonify(progress_data)

@dashboard_bp.route('/department-managers/<department>', methods=['GET'])
def get_department_managers(department):
    """API endpoint to get all managers in a department"""
    users_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/users.json')
    
    try:
        with open(users_path, 'r') as f:
            users_data = json.load(f)
        
        department_managers = []
        for email, user_info in users_data.items():
            user_dept = user_info.get('profile', {}).get('department', '')
            if user_dept.lower() == department.lower():
                role_type = user_info.get('roleType', '').lower()
                if role_type in ['manager', 'director']:
                    department_managers.append({
                        'user_id': user_info.get('user_id'),
                        'name': user_info.get('name', ''),
                        'email': user_info.get('email', ''),
                        'role': user_info.get('profile', {}).get('role', ''),
                        'team': user_info.get('profile', {}).get('team', ''),
                        'level': user_info.get('profile', {}).get('level', '')
                    })
        
        return jsonify({
            'department': department,
            'managers': department_managers,
            'count': len(department_managers)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/user-learning-paths/<user_id>', methods=['GET'])
def get_user_learning_paths(user_id):
    """API endpoint to get learning paths assigned to a user and their progress"""
    try:
        # Load learning paths data
        learning_paths_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/learning_paths.json')
        with open(learning_paths_path, 'r') as f:
            learning_paths_data = json.load(f)
        
        # Load learning path progress data
        progress_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/LearningPathProgress.json')
        with open(progress_path, 'r') as f:
            progress_data = json.load(f)
        
        # Get user's learning path progress
        user_progress = [p['attributes'] for p in progress_data if p['attributes']['user_id'] == user_id]
        
        # Build response with learning path details and progress
        user_learning_paths = []
        for progress in user_progress:
            lp_id = progress['learning_path_id']
            lp_details = learning_paths_data.get(lp_id, {})
            
            if lp_details:  # Only include if learning path exists
                user_learning_paths.append({
                    'learning_path_id': lp_id,
                    'title': lp_details.get('title', 'Unknown Path'),
                    'description': lp_details.get('description', ''),
                    'department': lp_details.get('department', ''),
                    'difficulty': lp_details.get('difficulty', 'Unknown'),
                    'duration': lp_details.get('duration', 'Unknown'),
                    'modules': lp_details.get('modules', []),
                    'tags': lp_details.get('tags', []),
                    'status': lp_details.get('status', 'unknown'),
                    'progress': {
                        'status': progress.get('status', 'not_started'),
                        'progress_percent': progress.get('progress_percent', 0),
                        'modules_completed_count': progress.get('modules_completed_count', 0),
                        'modules_total_count': progress.get('modules_total_count', 0),
                        'time_invested_minutes': progress.get('time_invested_minutes', 0),
                        'last_accessed_at': progress.get('last_accessed_at'),
                        'started_at': progress.get('started_at'),
                        'completed_at': progress.get('completed_at'),
                        'current_module_id': progress.get('current_module_id'),
                        'enrolled_at': progress.get('enrolled_at'),
                        'estimated_completion_weeks': progress.get('estimated_completion_weeks'),
                        'difficulty_level': progress.get('difficulty_level'),
                        'tags': progress.get('tags', [])
                    }
                })
        
        # Sort by enrollment date (most recent first)
        user_learning_paths.sort(key=lambda x: x['progress']['enrolled_at'] or '', reverse=True)
        
        return jsonify({
            'user_id': user_id,
            'learning_paths': user_learning_paths,
            'total_paths': len(user_learning_paths),
            'completed_paths': len([lp for lp in user_learning_paths if lp['progress']['status'] == 'completed']),
            'in_progress_paths': len([lp for lp in user_learning_paths if lp['progress']['status'] == 'in_progress']),
            'not_started_paths': len([lp for lp in user_learning_paths if lp['progress']['status'] == 'not_started'])
        })
        
    except Exception as e:
        print(f"Error getting learning paths for user {user_id}: {e}")
        return jsonify({'error': str(e)}), 500
