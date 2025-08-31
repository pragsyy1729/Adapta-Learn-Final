#!/usr/bin/env python3
"""
Test script for the comprehensive recommendations system
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_recommendations_system():
    """Test the comprehensive recommendations system"""

    print("🧪 Testing Comprehensive Recommendations System")
    print("=" * 50)

    # Test user ID for testing
    test_user_id = "test_user_001"

    # 1. Test getting user recommendations (should be empty initially)
    print("\n1. Testing GET /api/recommendations/user/{user_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/recommendations/user/{test_user_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully retrieved user recommendations")
            print(f"   Total recommendations: {data.get('total_count', 0)}")
            print(f"   AI: {data.get('counts_by_source', {}).get('ai', 0)}")
            print(f"   HR: {data.get('counts_by_source', {}).get('hr', 0)}")
            print(f"   Admin: {data.get('counts_by_source', {}).get('admin', 0)}")
        else:
            print(f"❌ Failed to get recommendations: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")

    # 2. Test adding HR recommendation
    print("\n2. Testing POST /api/recommendations/hr/add")
    hr_rec_data = {
        "user_id": test_user_id,
        "title": "Leadership Development Program",
        "description": "Advanced leadership skills training for senior roles",
        "reason": "Based on performance review and career progression plan",
        "priority": "high",
        "content_id": "LP_LEADERSHIP_001",
        "content_type": "learning_path",
        "assigned_by": "hr_manager@example.com",
        "due_date": "2024-12-31"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/recommendations/hr/add",
                               json=hr_rec_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 201:
            data = response.json()
            print("✅ Successfully added HR recommendation")
            print(f"   Recommendation ID: {data.get('recommendation', {}).get('id')}")
        else:
            print(f"❌ Failed to add HR recommendation: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error adding HR recommendation: {e}")

    # 3. Test adding Admin recommendation
    print("\n3. Testing POST /api/recommendations/admin/add")
    admin_rec_data = {
        "user_id": test_user_id,
        "title": "Compliance Training Update",
        "description": "Mandatory compliance training for all employees",
        "reason": "New regulatory requirements",
        "priority": "high",
        "content_id": "MODULE_COMPLIANCE_2024",
        "content_type": "module",
        "assigned_by": "admin@example.com",
        "target_audience": "all_employees"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/recommendations/admin/add",
                               json=admin_rec_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 201:
            data = response.json()
            print("✅ Successfully added Admin recommendation")
            print(f"   Recommendation ID: {data.get('recommendation', {}).get('id')}")
        else:
            print(f"❌ Failed to add Admin recommendation: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error adding Admin recommendation: {e}")

    # 4. Test generating AI recommendations
    print("\n4. Testing POST /api/recommendations/ai/generate/{user_id}")
    try:
        response = requests.post(f"{BASE_URL}/api/recommendations/ai/generate/{test_user_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully generated AI recommendations")
            print(f"   Generated {data.get('count', 0)} recommendations")
        else:
            print(f"❌ Failed to generate AI recommendations: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error generating AI recommendations: {e}")

    # 5. Test getting updated recommendations
    print("\n5. Testing updated GET /api/recommendations/user/{user_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/recommendations/user/{test_user_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully retrieved updated recommendations")
            print(f"   Total recommendations: {data.get('total_count', 0)}")
            print(f"   AI: {data.get('counts_by_source', {}).get('ai', 0)}")
            print(f"   HR: {data.get('counts_by_source', {}).get('hr', 0)}")
            print(f"   Admin: {data.get('counts_by_source', {}).get('admin', 0)}")

            # Show sample recommendations
            all_recs = data.get('recommendations', {}).get('all', [])
            if all_recs:
                print("\n   Sample recommendations:")
                for i, rec in enumerate(all_recs[:3]):  # Show first 3
                    print(f"   {i+1}. [{rec.get('source', '').upper()}] {rec.get('title', '')}")
                    print(f"      Priority: {rec.get('priority', 'low')}")
        else:
            print(f"❌ Failed to get updated recommendations: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting updated recommendations: {e}")

    # 6. Test tracking interaction
    print("\n6. Testing POST /api/recommendations/user/{user_id}/interaction/{rec_id}")
    try:
        # Get first recommendation ID for testing
        response = requests.get(f"{BASE_URL}/api/recommendations/user/{test_user_id}")
        if response.status_code == 200:
            data = response.json()
            all_recs = data.get('recommendations', {}).get('all', [])
            if all_recs:
                first_rec_id = all_recs[0].get('id')
                interaction_data = {
                    "interaction_type": "viewed"
                }

                response = requests.post(f"{BASE_URL}/api/recommendations/user/{test_user_id}/interaction/{first_rec_id}",
                                       json=interaction_data,
                                       headers={'Content-Type': 'application/json'})
                if response.status_code == 200:
                    print("✅ Successfully tracked recommendation interaction")
                else:
                    print(f"❌ Failed to track interaction: {response.status_code}")
            else:
                print("⚠️  No recommendations found to test interaction tracking")
        else:
            print("⚠️  Could not get recommendations for interaction test")
    except Exception as e:
        print(f"❌ Error tracking interaction: {e}")

    # 7. Test analytics
    print("\n7. Testing GET /api/recommendations/analytics")
    try:
        response = requests.get(f"{BASE_URL}/api/recommendations/analytics")
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully retrieved recommendations analytics")
            print(f"   Total recommendations: {data.get('total_recommendations', 0)}")
            print(f"   Users with recommendations: {data.get('users_with_recommendations', 0)}")
            print(f"   By source: {data.get('recommendations_by_source', {})}")
        else:
            print(f"❌ Failed to get analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting analytics: {e}")

    print("\n" + "=" * 50)
    print("🎉 Recommendations system testing completed!")
    print("\n📋 Summary of endpoints tested:")
    print("   • GET /api/recommendations/user/{user_id}")
    print("   • POST /api/recommendations/hr/add")
    print("   • POST /api/recommendations/admin/add")
    print("   • POST /api/recommendations/ai/generate/{user_id}")
    print("   • POST /api/recommendations/user/{user_id}/interaction/{rec_id}")
    print("   • GET /api/recommendations/analytics")

if __name__ == "__main__":
    print("🚀 Starting recommendations system tests...")
    print("⚠️  Make sure the Flask server is running on http://localhost:5000")
    print("   Run: python backend/run.py")
    print()

    # Wait a moment for user to start server if needed
    input("Press Enter when server is ready...")

    test_recommendations_system()
