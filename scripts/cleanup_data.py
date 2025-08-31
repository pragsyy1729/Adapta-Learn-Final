#!/usr/bin/env python3
"""
Data Cleanup and Migration Script
Removes conflicting data files and ensures single source of truth.
"""

import json
import os
import shutil
from datetime import datetime

def cleanup_conflicting_files():
    """Remove conflicting data files that can cause inconsistencies"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    backup_dir = os.path.join(data_dir, 'backups', datetime.now().strftime('%Y%m%d_%H%M%S'))
    
    print("🧹 Starting Data Cleanup...")
    
    # Files to backup and remove (conflicting with our single sources of truth)
    conflicting_files = [
        'LearningPath.json',  # Conflicts with learning_paths.json
        'LearningPaths.json'  # Conflicts with learning_paths.json
    ]
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    for filename in conflicting_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            # Backup first
            backup_path = os.path.join(backup_dir, filename)
            shutil.copy2(filepath, backup_path)
            print(f"📦 Backed up {filename} to {backup_path}")
            
            # Remove original
            os.remove(filepath)
            print(f"🗑️  Removed conflicting file: {filename}")
        else:
            print(f"✅ File {filename} already doesn't exist")
    
    print(f"\n✅ Cleanup complete. Backups stored in: {backup_dir}")

def main():
    cleanup_conflicting_files()

if __name__ == "__main__":
    main()
