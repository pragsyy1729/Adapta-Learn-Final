#!/usr/bin/env python3
"""
Test script for learning style material assignment functionality
"""
import json
import os
import sys
import requests

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def assign_test_learning_paths(user_id: str):
    """Assign some default learning paths to the test user"""
    try:
        import uuid
        from datetime import datetime
        
        # Load learning path progress data
        progress_file = os.path.join(os.path.dirname(__file__), 'data', 'LearningPathProgress.json')
        progress_data = _read_json(progress_file, [])
        
        # Learning paths to assign
        paths_to_assign = ["LP_SOFT_001", "LP_SOFT_002"]  # Communication and Leadership
        
        for path_id in paths_to_assign:
            # Check if already assigned
            existing = next((p for p in progress_data if p.get('attributes', {}).get('user_id') == user_id and 
                           p.get('attributes', {}).get('learning_path_id') == path_id), None)
            
            if not existing:
                new_progress = {
                    "attributes": {
                        "id": f"lpp_{user_id}_{path_id}_{str(uuid.uuid4())[:8]}",
                        "user_id": user_id,
                        "learning_path_id": path_id,
                        "status": "not_started",
                        "progress_percent": 0.0,
                        "modules_completed_count": 0,
                        "modules_total_count": 3,  # Approximate
                        "time_invested_minutes": 0,
                        "last_accessed_at": None,
                        "started_at": None,
                        "completed_at": None,
                        "current_module_id": None,
                        "enrolled_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                        "is_default": True
                    }
                }
                progress_data.append(new_progress)
                print(f"Assigned learning path {path_id} to user {user_id}")
        
        # Save updated progress data
        _write_json(progress_file, progress_data)
        
    except Exception as e:
        print(f"Error assigning learning paths: {e}")

def _read_json(file_path, default=None):
    """Helper function to read JSON files"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default or []

def _write_json(file_path, data):
    """Helper function to write JSON files"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def test_learning_style_assignment():
    """Test the learning style material assignment feature"""

    print("Testing Learning Style Material Assignment")
    print("=" * 50)

    # Test data - using existing user
    test_user_id = "user_002"  # johndoe@gmail.com from users.json
    test_vark_scores = {
        "Visual": 12,
        "Auditory": 15,
        "Read/Write": 8,
        "Kinesthetic": 10
    }

    print(f"Test User ID: {test_user_id}")
    print(f"VARK Scores: {test_vark_scores}")

    # Determine expected top 2 styles
    style_mapping = {
        'Visual': test_vark_scores.get('Visual', 0),
        'Aural': test_vark_scores.get('Auditory', 0),
        'Read/Write': test_vark_scores.get('Read/Write', 0),
        'Kinesthetic': test_vark_scores.get('Kinesthetic', 0)
    }

    sorted_styles = sorted(style_mapping.items(), key=lambda x: x[1], reverse=True)
    expected_top_2 = [style for style, score in sorted_styles[:2] if score > 0]

    print(f"Expected Top 2 Styles: {expected_top_2}")

    # First, assign some learning paths to the user
    print("\nAssigning learning paths to test user...")
    assign_test_learning_paths(test_user_id)

def test_learning_style_assignment():
    """Test the learning style material assignment feature"""

    print("Testing Learning Style Material Assignment")
    print("=" * 50)

    # Test data - using existing user
    test_user_id = "user_002"  # johndoe@gmail.com from users.json
    test_vark_scores = {
        "Visual": 12,
        "Auditory": 15,
        "Read/Write": 8,
        "Kinesthetic": 10
    }

    print(f"Test User ID: {test_user_id}")
    print(f"VARK Scores: {test_vark_scores}")

    # Determine expected top 2 styles
    style_mapping = {
        'Visual': test_vark_scores.get('Visual', 0),
        'Aural': test_vark_scores.get('Auditory', 0),
        'Read/Write': test_vark_scores.get('Read/Write', 0),
        'Kinesthetic': test_vark_scores.get('Kinesthetic', 0)
    }

    sorted_styles = sorted(style_mapping.items(), key=lambda x: x[1], reverse=True)
    expected_top_2 = [style for style, score in sorted_styles[:2] if score > 0]

    print(f"Expected Top 2 Styles: {expected_top_2}")

    # First, assign some learning paths to the user
    print("\nAssigning learning paths to test user...")
    assign_test_learning_paths(test_user_id)

    # Test the assignment function directly
    try:
        from backend.app.routes.user_auth import assign_learning_materials_based_on_style

        print("\nTesting direct function call...")
        assign_learning_materials_based_on_style(test_user_id, test_vark_scores)
        print("✓ Direct function call completed successfully")

    except Exception as e:
        print(f"✗ Direct function call failed: {e}")

    # Test via API endpoint (if server is running)
    try:
        print("\nTesting API endpoint...")
        payload = {
            "user_id": test_user_id,
            "learning_style": "Auditory",  # Based on highest score
            "vark_scores": test_vark_scores,
            "quiz_date": "2024-01-15T10:00:00Z"
        }

        # This would work if the server is running
        # response = requests.post("http://localhost:5000/user_auth/learning-style", json=payload)
        # print(f"API Response: {response.status_code}")

        print("✓ API payload prepared (server test would require running server)")

    except Exception as e:
        print(f"✗ API test failed: {e}")

    # Check if materials were assigned by reading user data
    try:
        print("\nChecking user data for material assignments...")

        # Load users data
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        users_file = os.path.join(data_dir, 'users.json')

        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users = json.load(f)

            # Find test user
            test_user_found = False
            for email, user_data in users.items():
                if user_data.get('user_id') == test_user_id:
                    test_user_found = True
                    profile = user_data.get('profile', {})

                    print(f"✓ Test user found in users.json")
                    print(f"  Learning Style: {profile.get('learning_style')}")
                    print(f"  VARK Scores: {profile.get('vark_scores')}")

                    lp_materials = profile.get('learning_path_materials', {})
                    if lp_materials:
                        print(f"  Assigned Learning Path Materials: {len(lp_materials)} paths")
                        for lp_id, lp_data in lp_materials.items():
                            print(f"    {lp_id}: {lp_data.get('preferred_styles', [])}")
                    else:
                        print("  No learning path materials assigned yet")

                    break

            if not test_user_found:
                print("✗ Test user not found in users.json")
        else:
            print("✗ users.json file not found")

    except Exception as e:
        print(f"✗ Error checking user data: {e}")

    print("\nTest completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_learning_style_assignment()
