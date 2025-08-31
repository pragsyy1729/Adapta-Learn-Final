#!/usr/bin/env python3
import os
import sys
import tempfile
import shutil
import json
import importlib

repo_root = os.path.abspath(os.getcwd())
print(f"repo_root={repo_root}")

tmp = tempfile.mkdtemp(prefix="adapta_test_data_")
print(f"created temp data dir: {tmp}")

# Files we need
files = [
    'default_learning_paths.json',
    'department_learning_paths.json',
    'users.json',
    'sessions.json',
    'rate_limits.json',
    'LearningPathProgress.json',
    'UserDashboard.json'
]

for fname in files:
    src = os.path.join(repo_root, 'data', fname)
    dst = os.path.join(tmp, fname)
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"copied {fname} -> temp")
    else:
        # create sensible defaults
        if fname.endswith('.json'):
            if fname == 'users.json':
                with open(dst, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            elif fname == 'LearningPathProgress.json' or fname == 'UserDashboard.json':
                with open(dst, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            else:
                with open(dst, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
        print(f"created placeholder for {fname}")

# Ensure repo root is importable
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import the module
import backend.app.routes.user_auth as ua

# Monkeypatch DATA_DIR to temp folder
ua.DATA_DIR = tmp
print(f"patched user_auth.DATA_DIR -> {ua.DATA_DIR}")
# Patch module-level file constants so writes go to the temp data directory as well
ua.USERS_FILE = os.path.join(tmp, 'users.json')
ua.SESSIONS_FILE = os.path.join(tmp, 'sessions.json')
ua.RATE_LIMIT_FILE = os.path.join(tmp, 'rate_limits.json')
print(f"patched user_auth.USERS_FILE -> {ua.USERS_FILE}")

# Helper to read temp data
def read_tmp(fname):
    p = os.path.join(tmp, fname)
    if not os.path.exists(p):
        return None
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

# 1) Create a user with department to exercise both default and department assignment
print('\n=== Creating user1 (department present) via create_user_if_missing ===')
user1 = ua.create_user_if_missing(
    'test.user1@example.com',
    'Password123',
    name='Test User 1',
    roleType='Employee',
    newJoiner='yes',
    dateOfJoining='2025-08-31',
    role='Engineer',
    department='DS2024001',
)
print('created user1:', user1.get('user_id'))

users_after = read_tmp('users.json')
print('user1 profile enrollments:', users_after.get('test.user1@example.com', {}).get('profile', {}).get('enrollments'))

progress_after = read_tmp('LearningPathProgress.json')
print('progress entries count after user1:', len(progress_after))

# 2) Create a user without department to exercise default paths only
print('\n=== Creating user2 (no department) via create_user_if_missing ===')
user2 = ua.create_user_if_missing(
    'test.user2@example.com',
    'Password123',
    name='Test User 2',
    roleType='Employee',
)
print('created user2:', user2.get('user_id'))
users_after = read_tmp('users.json')
print('user2 profile enrollments:', users_after.get('test.user2@example.com', {}).get('profile', {}).get('enrollments'))

progress_after = read_tmp('LearningPathProgress.json')
print('progress entries count after user2:', len(progress_after))

# 3) Explicitly call assign_department_learning_paths for a new user3
print('\n=== Creating user3 (no department) then calling assign_department_learning_paths explicitly ===')
user3 = ua.create_user_if_missing(
    'test.user3@example.com',
    'Password123',
    name='Test User 3',
    roleType='Employee',
)
print('created user3:', user3.get('user_id'))

# Now explicitly call department assignment
ua.assign_department_learning_paths(user3.get('user_id'), 'KYC2024001')
users_after = read_tmp('users.json')
print('user3 enrollments after department assignment:', users_after.get('test.user3@example.com', {}).get('profile', {}).get('enrollments'))

progress_after = read_tmp('LearningPathProgress.json')
print('progress entries count after user3 department assignment:', len(progress_after))

print('\n=== Samples of LearningPathProgress entries (first 5) ===')
for p in progress_after[:5]:
    print(p)

print('\nTemp data dir preserved at:', tmp)
print('You can inspect the files in that temp directory to confirm results.')

# Do not delete temp dir so the user can inspect; print path so they can remove later

