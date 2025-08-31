#!/usr/bin/env python3
"""
Test script for the conversation agent system.
This script tests the document upload and Q&A functionality.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_conversation_agent():
    """Test the conversation agent endpoints."""

    base_url = "http://localhost:5000"

    print("🧪 Testing Conversation Agent System")
    print("=" * 50)

    # Test 1: Check department status
    print("\n1. Testing department status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/conversation/departments/ENG2024001/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Department status: {data}")
        else:
            print(f"❌ Department status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Department status error: {e}")

    # Test 2: Test Q&A with existing documents (if any)
    print("\n2. Testing Q&A endpoint...")
    test_question = "What is the main purpose of this department?"

    try:
        response = requests.post(f"{base_url}/api/conversation/ask", json={
            "question": test_question,
            "department_id": "ENG2024001",
            "user_id": "test_user"
        })

        if response.status_code == 200:
            data = response.json()
            print("✅ Q&A Response:")
            print(f"   Answer: {data.get('answer', 'N/A')}")
            print(f"   Chunks found: {data.get('chunks_found', 0)}")
            print(f"   Department: {data.get('department', 'N/A')}")
        else:
            print(f"❌ Q&A failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Q&A error: {e}")

    # Test 3: Test document upload and processing status
    print("\n3. Testing document upload and processing status...")
    test_file_path = "test_document.txt"

    # Create a simple test document
    test_content = """
    Welcome to the Engineering Department!

    This department focuses on software development and technical solutions.
    We build scalable applications and work with cutting-edge technologies.

    Key Responsibilities:
    - Develop user interfaces and client-side applications
    - Build robust backend systems and APIs
    - Ensure code quality and maintainability
    - Collaborate with cross-functional teams

    Technologies we use:
    - React for frontend development
    - Python and Node.js for backend
    - Docker for containerization
    - AWS for cloud infrastructure
    """

    processing_id = None
    try:
        with open(test_file_path, 'w') as f:
            f.write(test_content)

        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'department_id': 'ENG2024001'}

            response = requests.post(f"{base_url}/api/conversation/upload",
                                   files=files, data=data)

        if response.status_code == 200:
            data = response.json()
            processing_id = data.get('processing_id')
            print("✅ Document upload successful:")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Processing ID: {processing_id}")
            print(f"   Status: {data.get('status', 'N/A')}")
            
            # Test processing status if we got a processing ID
            if processing_id:
                print("\n   Testing processing status...")
                import time
                max_attempts = 10
                for attempt in range(max_attempts):
                    response = requests.get(f"{base_url}/api/conversation/processing/{processing_id}/status")
                    if response.status_code == 200:
                        status_data = response.json()
                        status = status_data.get('status')
                        progress = status_data.get('progress', 0)
                        print(f"   Attempt {attempt + 1}: Status={status}, Progress={progress}%")
                        
                        if status in ['completed', 'failed']:
                            break
                    else:
                        print(f"   ❌ Processing status failed: {response.status_code}")
                        break
                    
                    time.sleep(2)  # Wait 2 seconds between checks
            
            # Test department processing jobs
            print("\n   Testing department processing jobs...")
            response = requests.get(f"{base_url}/api/conversation/departments/ENG2024001/processing")
            if response.status_code == 200:
                jobs_data = response.json()
                print("✅ Department processing jobs:")
                print(f"   Total jobs: {jobs_data.get('total_jobs', 0)}")
                print(f"   Active jobs: {jobs_data.get('active_jobs', 0)}")
                print(f"   Completed jobs: {jobs_data.get('completed_jobs', 0)}")
            else:
                print(f"❌ Department processing jobs failed: {response.status_code}")
        else:
            print(f"❌ Document upload failed: {response.status_code} - {response.text}")

        # Clean up test file
        os.remove(test_file_path)

    except Exception as e:
        print(f"❌ Document upload/processing test error: {e}")
        # Clean up test file if it exists
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

    print("\n" + "=" * 50)
    print("🎉 Conversation Agent testing completed!")

if __name__ == "__main__":
    test_conversation_agent()
