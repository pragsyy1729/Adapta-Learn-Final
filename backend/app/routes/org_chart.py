from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime

org_chart_bp = Blueprint('org_chart', __name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

def load_users():
    """Load users data from JSON file"""
    users_file = os.path.join(DATA_DIR, 'users.json')
    try:
        with open(users_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_departments():
    """Load departments data from JSON file"""
    departments_file = os.path.join(DATA_DIR, 'department.json')
    try:
        with open(departments_file, 'r') as f:
            data = json.load(f)
            return data.get('departments', [])
    except FileNotFoundError:
        return []

def generate_org_chart():
    """Generate org chart from users and departments data"""
    users = load_users()
    departments = load_departments()

    print(f"DEBUG: Loaded {len(users)} users from JSON")
    print(f"DEBUG: User emails: {list(users.keys())[:10]}...")

    # Create department lookup
    dept_lookup = {dept['id']: dept for dept in departments}

    org_chart = []

    for email, user_data in users.items():
        profile = user_data.get('profile', {})

        # Build org chart entry
        chart_entry = {
            'id': user_data.get('user_id'),
            'name': user_data.get('name'),
            'email': email,
            'role': profile.get('role', user_data.get('roleType', 'Unknown')),
            'department': profile.get('department', 'Unknown'),
            'title': profile.get('title', profile.get('role', user_data.get('roleType', 'Unknown'))),
            'level': profile.get('level', 'Unknown'),
            'manager': profile.get('manager'),
            'reports': profile.get('reports', []),
            'avatar': '/placeholder.svg',
            'phone': profile.get('phone', ''),
            'location': profile.get('location', ''),
            'start_date': user_data.get('dateOfJoining', user_data.get('created_at', '')),
            'skills': profile.get('skills', []),
            'team': profile.get('team', ''),
            'newJoiner': user_data.get('newJoiner', 'No')
        }

        # Add department info if available
        dept_id = profile.get('department')
        if dept_id and dept_id in dept_lookup:
            chart_entry['department_name'] = dept_lookup[dept_id]['name']
            chart_entry['department_description'] = dept_lookup[dept_id]['description']

        org_chart.append(chart_entry)

    print(f"DEBUG: Generated org chart with {len(org_chart)} entries")
    return org_chart

@org_chart_bp.route('/org-chart', methods=['GET'])
def get_org_chart():
    """Get the complete organizational chart"""
    try:
        org_chart = generate_org_chart()
        return jsonify({
            'success': True,
            'data': org_chart,
            'count': len(org_chart)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@org_chart_bp.route('/org-chart/department/<department>', methods=['GET'])
def get_org_chart_by_department(department):
    """Get org chart for a specific department"""
    try:
        org_chart = generate_org_chart()
        filtered_chart = [user for user in org_chart if user.get('department') == department]

        return jsonify({
            'success': True,
            'data': filtered_chart,
            'department': department,
            'count': len(filtered_chart)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@org_chart_bp.route('/org-chart/user/<user_id>', methods=['GET'])
def get_user_org_info(user_id):
    """Get organizational information for a specific user"""
    try:
        org_chart = generate_org_chart()
        user_info = next((user for user in org_chart if user['id'] == user_id), None)

        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Find manager info
        manager_info = None
        if user_info.get('manager'):
            manager_info = next((user for user in org_chart if user['id'] == user_info['manager']), None)

        # Find reports info
        reports_info = []
        for report_id in user_info.get('reports', []):
            report = next((user for user in org_chart if user['id'] == report_id), None)
            if report:
                reports_info.append({
                    'id': report['id'],
                    'name': report['name'],
                    'role': report['role'],
                    'email': report['email']
                })

        return jsonify({
            'success': True,
            'data': {
                'user': user_info,
                'manager': manager_info,
                'reports': reports_info
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@org_chart_bp.route('/org-chart/managers', methods=['GET'])
def get_managers():
    """Get all managers and their direct reports"""
    try:
        org_chart = generate_org_chart()
        managers = {}

        for user in org_chart:
            if user.get('reports'):
                managers[user['id']] = {
                    'id': user['id'],
                    'name': user['name'],
                    'role': user['role'],
                    'department': user['department'],
                    'reports_count': len(user['reports']),
                    'reports': user['reports']
                }

        return jsonify({
            'success': True,
            'data': list(managers.values()),
            'count': len(managers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
