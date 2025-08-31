#!/usr/bin/env python3
"""
Test script for learning style API endpoints
"""
import requests
import json

def test_learning_style_api():
    """Test the learning style API endpoints"""

    print("Testing Learning Style API Endpoints")
    print("=" * 50)

    base_url = "http://localhost:5000"

    # Test data
    test_user_id = "user_002"
    vark_scores = {
        "Visual": 12,
        "Auditory": 15,
        "Read/Write": 8,
        "Kinesthetic": 10
    }

    # Test 1: Save learning style
    print("\n1. Testing POST /api/user_auth/learning-style")
    payload = {
        "user_id": test_user_id,
        "learning_style": "Auditory",
        "vark_scores": vark_scores,
        "quiz_date": "2024-01-15T10:00:00Z"
    }

    try:
        response = requests.post(f"{base_url}/api/user_auth/learning-style", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✓ Learning style saved successfully")
            print(f"Response: {result}")
        else:
            print(f"✗ Failed to save learning style: {response.text}")
    except Exception as e:
        print(f"✗ API call failed: {e}")

    # Test 2: Get learning materials
    print("\n2. Testing GET /api/user_auth/learning-materials/{user_id}")
    try:
        response = requests.get(f"{base_url}/api/user_auth/learning-materials/{test_user_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✓ Learning materials retrieved successfully")
            print(f"Learning Style: {result.get('learning_style')}")
            print(f"VARK Scores: {result.get('vark_scores')}")
            materials = result.get('materials', {})
            print(f"Number of learning paths with materials: {len(materials)}")
            for lp_id, lp_data in materials.items():
                print(f"  {lp_id}: {lp_data.get('preferred_styles', [])}")
                materials_count = sum(len(mats) for mats in lp_data.get('materials', {}).values())
                print(f"    Total materials: {materials_count}")
        else:
            print(f"✗ Failed to get learning materials: {response.text}")
    except Exception as e:
        print(f"✗ API call failed: {e}")

    # Test 3: Get user by ID
    print("\n3. Testing GET /api/user_auth/user/{user_id}")
    try:
        response = requests.get(f"{base_url}/api/user_auth/user/{test_user_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                user = result.get('user', {})
                print("✓ User retrieved successfully")
                print(f"User ID: {user.get('user_id')}")
                print(f"Name: {user.get('name')}")
                print(f"Role: {user.get('role')}")
                print(f"Department: {user.get('department')}")
            else:
                print(f"✗ Failed to get user: {result.get('error')}")
        else:
            print(f"✗ API call failed: {response.text}")
    except Exception as e:
        print(f"✗ API call failed: {e}")

    print("\nAPI Testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_learning_style_api()
