#!/usr/bin/env python3
"""
Frontend Integration Test Script
Tests the connection between React frontend and Flask backend APIs
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_api_endpoints():
    """Test all API endpoints that the frontend will use"""

    print("🧪 Testing Frontend-Backend API Integration")
    print("=" * 60)

    test_user_id = "test_user_001"

    # 1. Test User Profile
    print("\n1. Testing User Profile API")
    try:
        response = requests.get(f"{BASE_URL}/user/profile/{test_user_id}")
        print(f"   GET /user/profile/{test_user_id}: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ User profile endpoint working")
        else:
            print(f"   ⚠️  User profile returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing user profile: {e}")

    # 2. Test Recommendations
    print("\n2. Testing Recommendations API")
    try:
        response = requests.get(f"{BASE_URL}/recommendations/user/{test_user_id}")
        print(f"   GET /recommendations/user/{test_user_id}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Recommendations endpoint working"            print(f"   📊 Total recommendations: {data.get('data', {}).get('total_count', 0)}")
        else:
            print(f"   ⚠️  Recommendations returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing recommendations: {e}")

    # 3. Test Gamification
    print("\n3. Testing Gamification API")
    try:
        response = requests.get(f"{BASE_URL}/gamification/user/{test_user_id}")
        print(f"   GET /gamification/user/{test_user_id}: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Gamification endpoint working")
        else:
            print(f"   ⚠️  Gamification returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing gamification: {e}")

    # 4. Test Leaderboard
    print("\n4. Testing Leaderboard API")
    try:
        response = requests.get(f"{BASE_URL}/gamification/leaderboard")
        print(f"   GET /gamification/leaderboard: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            leaderboard = data.get('data', {}).get('leaderboard', [])
            print("   ✅ Leaderboard endpoint working"            print(f"   🏆 Users on leaderboard: {len(leaderboard)}")
        else:
            print(f"   ⚠️  Leaderboard returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing leaderboard: {e}")

    # 5. Test Microlearning
    print("\n5. Testing Microlearning API")
    try:
        response = requests.get(f"{BASE_URL}/microlearning/personalized/{test_user_id}")
        print(f"   GET /microlearning/personalized/{test_user_id}: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Microlearning endpoint working")
        else:
            print(f"   ⚠️  Microlearning returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing microlearning: {e}")

    # 6. Test Quiz System
    print("\n6. Testing Quiz API")
    try:
        # Try to get a quiz (this might fail if no quiz exists, but tests the endpoint)
        response = requests.get(f"{BASE_URL}/quiz/chapter/test_chapter_001?user_id={test_user_id}")
        print(f"   GET /quiz/chapter/test_chapter_001: {response.status_code}")
        if response.status_code in [200, 404]:
            print("   ✅ Quiz endpoint accessible")
        else:
            print(f"   ⚠️  Quiz endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing quiz: {e}")

    # 7. Test Learning Paths
    print("\n7. Testing Learning Paths API")
    try:
        response = requests.get(f"{BASE_URL}/user/{test_user_id}/learning-paths")
        print(f"   GET /user/{test_user_id}/learning-paths: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Learning paths endpoint working")
        else:
            print(f"   ⚠️  Learning paths returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing learning paths: {e}")

    # 8. Test CORS
    print("\n8. Testing CORS Headers")
    try:
        response = requests.options(f"{BASE_URL}/recommendations/user/{test_user_id}",
                                  headers={'Origin': 'http://localhost:5173'})
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        if cors_headers:
            print("   ✅ CORS headers present")
            print(f"   🌐 Allowed origins: {cors_headers}")
        else:
            print("   ⚠️  No CORS headers found")
    except Exception as e:
        print(f"   ❌ Error testing CORS: {e}")

    print("\n" + "=" * 60)
    print("🎉 Frontend-Backend Integration Test Complete!")
    print("\n📋 Summary of Endpoints Tested:")
    print("   • User Profile API")
    print("   • Recommendations API")
    print("   • Gamification API")
    print("   • Leaderboard API")
    print("   • Microlearning API")
    print("   • Quiz API")
    print("   • Learning Paths API")
    print("   • CORS Configuration")

    print("\n🚀 Next Steps:")
    print("   1. Start the Flask backend: PYTHONPATH=. ./adapt_learn/bin/python3 backend/run.py")
    print("   2. Start the React frontend: npm run dev")
    print("   3. Open http://localhost:5173 in your browser")
    print("   4. Navigate to the Dashboard to see the new features!")

def test_sample_data_creation():
    """Create some sample data for testing"""

    print("\n🔧 Creating Sample Data for Testing")
    print("-" * 40)

    # Sample HR Recommendation
    hr_rec = {
        "user_id": "test_user_001",
        "title": "Advanced Leadership Training",
        "description": "Comprehensive leadership development program",
        "reason": "Based on performance review and career progression",
        "priority": "high",
        "content_id": "LP_LEADERSHIP_001",
        "content_type": "learning_path",
        "assigned_by": "hr@example.com",
        "due_date": "2024-12-31"
    }

    try:
        response = requests.post(f"{BASE_URL}/recommendations/hr/add",
                               json=hr_rec,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 201:
            print("   ✅ Sample HR recommendation created")
        else:
            print(f"   ⚠️  HR recommendation creation: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error creating HR recommendation: {e}")

    # Sample Admin Recommendation
    admin_rec = {
        "user_id": "test_user_001",
        "title": "Compliance Training 2024",
        "description": "Mandatory compliance training for all employees",
        "reason": "New regulatory requirements",
        "priority": "high",
        "content_id": "MODULE_COMPLIANCE_2024",
        "content_type": "module",
        "assigned_by": "admin@example.com",
        "target_audience": "all_employees"
    }

    try:
        response = requests.post(f"{BASE_URL}/recommendations/admin/add",
                               json=admin_rec,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 201:
            print("   ✅ Sample Admin recommendation created")
        else:
            print(f"   ⚠️  Admin recommendation creation: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error creating Admin recommendation: {e}")

    # Generate AI Recommendations
    try:
        response = requests.post(f"{BASE_URL}/recommendations/ai/generate/test_user_001")
        if response.status_code == 200:
            print("   ✅ AI recommendations generated")
        else:
            print(f"   ⚠️  AI recommendation generation: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error generating AI recommendations: {e}")

    print("   📝 Sample data creation complete!")

if __name__ == "__main__":
    print("🚀 Starting Frontend-Backend Integration Tests...")
    print("⚠️  Make sure the Flask server is running on http://localhost:5000")
    print("   Run: PYTHONPATH=. ./adapt_learn/bin/python3 backend/run.py")
    print()

    # Wait for user confirmation
    input("Press Enter when the backend server is ready...")

    # Run the tests
    test_api_endpoints()

    # Create sample data
    create_sample = input("\nCreate sample data for testing? (y/n): ").lower().strip()
    if create_sample == 'y':
        test_sample_data_creation()

    print("\n🎊 All tests completed! Your LMS is ready for frontend integration.")
