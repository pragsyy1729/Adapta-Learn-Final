#!/usr/bin/env python3
"""
Fix Missing User Dashboard Entries
Creates dashboard entries for users who don't have them
"""

import json
import os
import uuid
from datetime import datetime

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def main():
    # Get the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    users_file = os.path.join(data_dir, 'users.json')
    dashboard_file = os.path.join(data_dir, 'UserDashboard.json')
    
    # Load users and dashboard data
    with open(users_file, 'r') as f:
        users_data = json.load(f)
    
    with open(dashboard_file, 'r') as f:
        dashboard_data = json.load(f)
    
    # Get existing dashboard user_ids
    existing_dashboard_users = set()
    for entry in dashboard_data:
        user_id = entry.get('attributes', {}).get('user_id')
        if user_id:
            existing_dashboard_users.add(user_id)
    
    # Find users missing dashboard entries
    missing_dashboard_users = []
    for email, user_info in users_data.items():
        user_id = user_info.get('user_id')
        if user_id and user_id not in existing_dashboard_users:
            missing_dashboard_users.append({
                'email': email,
                'user_id': user_id,
                'name': user_info.get('name', ''),
                'created_at': user_info.get('created_at', now_iso())
            })
    
    print(f"🔍 Found {len(missing_dashboard_users)} users missing dashboard entries:")
    for user in missing_dashboard_users:
        print(f"   • {user['name']} ({user['email']}) - {user['user_id']}")
    
    if not missing_dashboard_users:
        print("✅ All users have dashboard entries!")
        return
    
    # Create dashboard entries for missing users
    print(f"\n📊 Creating dashboard entries...")
    for user in missing_dashboard_users:
        new_dashboard_entry = {
            "attributes": {
                "id": str(uuid.uuid4()),
                "user_id": user['user_id'],
                "modules_completed": 0,
                "overall_progress_percent": 0.0,
                "time_invested_minutes": 0,
                "quiz_average_percent": 0.0,
                "last_accessed_at": user['created_at']
            }
        }
        dashboard_data.append(new_dashboard_entry)
        print(f"   ✓ Created dashboard for {user['name']} ({user['user_id']})")
    
    # Save updated dashboard data
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"\n🎉 Successfully created {len(missing_dashboard_users)} dashboard entries!")
    print("All users should now be able to access their dashboards.")

if __name__ == "__main__":
    main()
