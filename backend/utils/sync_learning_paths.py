"""
Utility functions to sync learning path module counts and ensure data consistency
"""
import json
import os
from typing import Dict, List

def load_json(filepath: str) -> dict:
    """Load JSON data from file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(filepath: str, data: dict) -> None:
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def get_data_dir() -> str:
    """Get the data directory path"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

def sync_learning_path_module_counts() -> Dict[str, int]:
    """
    Sync module counts for all learning paths by counting actual modules
    Returns dict mapping learning_path_id to module count
    """
    data_dir = get_data_dir()
    
    # Load data files
    learning_paths_file = os.path.join(data_dir, 'learning_paths.json')
    modules_file = os.path.join(data_dir, 'Module.json')
    progress_file = os.path.join(data_dir, 'LearningPathProgress.json')
    
    learning_paths = load_json(learning_paths_file)
    modules = load_json(modules_file)
    progress_list = load_json(progress_file)
    
    if not isinstance(modules, list):
        print("Warning: Module.json is not in expected list format")
        return {}
    
    if not isinstance(progress_list, list):
        print("Warning: LearningPathProgress.json is not in expected list format")
        return {}
    
    # Count modules per learning path from both sources
    module_counts = {}
    
    # Method 1: Count from learning_paths.json "modules" array
    for path_id, path_data in learning_paths.items():
        if isinstance(path_data, dict) and 'modules' in path_data:
            module_counts[path_id] = len(path_data['modules'])
    
    # Method 2: Count from Module.json by learning_path_id
    modules_by_path = {}
    for module in modules:
        if isinstance(module, dict) and 'attributes' in module:
            attrs = module['attributes']
            path_id = attrs.get('learning_path_id')
            if path_id:
                if path_id not in modules_by_path:
                    modules_by_path[path_id] = 0
                modules_by_path[path_id] += 1
    
    # Use the maximum count from both methods (in case of discrepancy)
    final_counts = {}
    all_path_ids = set(module_counts.keys()) | set(modules_by_path.keys())
    
    for path_id in all_path_ids:
        count1 = module_counts.get(path_id, 0)
        count2 = modules_by_path.get(path_id, 0)
        final_counts[path_id] = max(count1, count2)
        
        if count1 != count2:
            print(f"Warning: Module count mismatch for {path_id}: learning_paths.json={count1}, Module.json={count2}")
    
    # Update all progress entries with correct module counts
    updated_count = 0
    for progress in progress_list:
        if isinstance(progress, dict) and 'attributes' in progress:
            attrs = progress['attributes']
            path_id = attrs.get('learning_path_id')
            if path_id in final_counts:
                old_count = attrs.get('modules_total_count', 0)
                new_count = final_counts[path_id]
                if old_count != new_count:
                    attrs['modules_total_count'] = new_count
                    updated_count += 1
                    print(f"Updated {path_id} module count: {old_count} -> {new_count}")
    
    # Save updated progress data
    if updated_count > 0:
        save_json(progress_file, progress_list)
        print(f"Updated {updated_count} progress entries with correct module counts")
    
    return final_counts

def update_learning_path_module_count(learning_path_id: str) -> int:
    """
    Update module count for a specific learning path
    Returns the new module count
    """
    data_dir = get_data_dir()
    
    # Load data files
    learning_paths_file = os.path.join(data_dir, 'learning_paths.json')
    modules_file = os.path.join(data_dir, 'Module.json')
    progress_file = os.path.join(data_dir, 'LearningPathProgress.json')
    
    learning_paths = load_json(learning_paths_file)
    modules = load_json(modules_file)
    progress_list = load_json(progress_file)
    
    # Count modules for this learning path
    module_count = 0
    
    # Method 1: Count from learning_paths.json
    if learning_path_id in learning_paths and 'modules' in learning_paths[learning_path_id]:
        module_count = max(module_count, len(learning_paths[learning_path_id]['modules']))
    
    # Method 2: Count from Module.json
    if isinstance(modules, list):
        module_json_count = sum(1 for module in modules 
                               if isinstance(module, dict) and 
                               'attributes' in module and 
                               module['attributes'].get('learning_path_id') == learning_path_id)
        module_count = max(module_count, module_json_count)
    
    # Update all progress entries for this learning path
    updated_count = 0
    if isinstance(progress_list, list):
        for progress in progress_list:
            if (isinstance(progress, dict) and 
                'attributes' in progress and 
                progress['attributes'].get('learning_path_id') == learning_path_id):
                
                old_count = progress['attributes'].get('modules_total_count', 0)
                if old_count != module_count:
                    progress['attributes']['modules_total_count'] = module_count
                    updated_count += 1
        
        if updated_count > 0:
            save_json(progress_file, progress_list)
            print(f"Updated {updated_count} progress entries for learning path {learning_path_id}: module count = {module_count}")
    
    return module_count

if __name__ == "__main__":
    # Run sync when called directly
    print("Syncing learning path module counts...")
    counts = sync_learning_path_module_counts()
    print(f"Synced module counts for {len(counts)} learning paths")
    for path_id, count in counts.items():
        print(f"  {path_id}: {count} modules")
