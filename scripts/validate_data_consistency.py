#!/usr/bin/env python3
"""
Data Consistency Validation Script
Prevents data inconsistency issues by validating relationships between data files.
"""

import json
import os
import sys
from typing import Dict, List, Set, Any

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in {filepath}: {e}")
        return {}

def validate_data_consistency():
    """Main validation function"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    errors = []
    warnings = []
    
    print("🔍 Starting Data Consistency Validation...")
    print("=" * 60)
    
    # Load all data files
    files_data = {}
    required_files = [
        'department.json',
        'department_learning_paths.json',
        'learning_paths.json',
        'LearningPathProgress.json',
        'onboarding_recommendations.json'
    ]
    
    for filename in required_files:
        filepath = os.path.join(data_dir, filename)
        files_data[filename] = load_json_file(filepath)
    
    # 1. Validate Department ID consistency
    print("1️⃣  Validating Department IDs...")
    departments = files_data['department.json'].get('departments', [])
    dept_ids = {dept['id'] for dept in departments}
    
    # Check department_learning_paths.json
    dept_learning_paths = files_data['department_learning_paths.json'].get('departments', {})
    for dept_id in dept_learning_paths.keys():
        if dept_id not in dept_ids:
            errors.append(f"Department ID '{dept_id}' in department_learning_paths.json not found in department.json")
    
    # Check onboarding recommendations
    onboarding_recs = files_data['onboarding_recommendations.json'].get('recommendations', {})
    for user_id, rec in onboarding_recs.items():
        dept_id = rec.get('department')
        if dept_id and dept_id not in dept_ids:
            errors.append(f"Department ID '{dept_id}' for user '{user_id}' in onboarding_recommendations.json not found in department.json")
    
    # 2. Validate Learning Path ID consistency
    print("2️⃣  Validating Learning Path IDs...")
    learning_paths = files_data['learning_paths.json']
    lp_ids = set(learning_paths.keys())
    
    # Check department_learning_paths.json
    for dept_id, paths in dept_learning_paths.items():
        for path in paths:
            lp_id = path.get('learning_path_id')
            if lp_id and lp_id not in lp_ids:
                errors.append(f"Learning Path ID '{lp_id}' in department_learning_paths.json not found in learning_paths.json")
    
    # Check LearningPathProgress.json
    progress_entries = files_data['LearningPathProgress.json']
    if isinstance(progress_entries, list):
        for entry in progress_entries:
            attrs = entry.get('attributes', {})
            lp_id = attrs.get('learning_path_id')
            if lp_id and lp_id not in lp_ids:
                errors.append(f"Learning Path ID '{lp_id}' in LearningPathProgress.json not found in learning_paths.json")
    
    # Check onboarding recommendations
    for user_id, rec in onboarding_recs.items():
        recommended_paths = rec.get('recommended_learning_paths', [])
        for lp_id in recommended_paths:
            if lp_id not in lp_ids:
                errors.append(f"Recommended Learning Path ID '{lp_id}' for user '{user_id}' not found in learning_paths.json")
    
    # 3. Validate ID Format Standards
    print("3️⃣  Validating ID Format Standards...")
    
    # Department IDs should be alphanumeric (e.g., ENG2024001)
    for dept in departments:
        dept_id = dept['id']
        if not dept_id.replace('2024', '').replace('001', '').isalpha():
            warnings.append(f"Department ID '{dept_id}' doesn't follow alphanumeric standard (e.g., ENG2024001)")
    
    # Learning Path IDs should be alphanumeric (e.g., LP2024ENG001)
    for lp_id in lp_ids:
        if not lp_id.startswith('LP2024') or not lp_id[6:].replace('001', '').replace('002', '').isalpha():
            warnings.append(f"Learning Path ID '{lp_id}' doesn't follow alphanumeric standard (e.g., LP2024ENG001)")
    
    # 4. Check for orphaned data
    print("4️⃣  Checking for Orphaned Data...")
    
    # Find users in progress who don't have onboarding recommendations
    progress_users = set()
    if isinstance(progress_entries, list):
        for entry in progress_entries:
            attrs = entry.get('attributes', {})
            user_id = attrs.get('user_id')
            if user_id:
                progress_users.add(user_id)
    
    onboarding_users = set(onboarding_recs.keys())
    orphaned_progress_users = progress_users - onboarding_users
    for user_id in orphaned_progress_users:
        warnings.append(f"User '{user_id}' has learning path progress but no onboarding recommendations")
    
    # 5. Check for duplicate learning paths files
    print("5️⃣  Checking for Conflicting Data Files...")
    conflicting_files = ['LearningPath.json', 'LearningPaths.json']
    for filename in conflicting_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            warnings.append(f"Conflicting file '{filename}' exists - should use 'learning_paths.json' as single source of truth")
    
    # Report Results
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)
    
    if not errors and not warnings:
        print("✅ All data consistency checks passed!")
        return True
    
    if errors:
        print(f"❌ ERRORS FOUND ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    print(f"\n🔧 Fix these issues to ensure data consistency!")
    return len(errors) == 0

def main():
    """Main entry point"""
    success = validate_data_consistency()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
