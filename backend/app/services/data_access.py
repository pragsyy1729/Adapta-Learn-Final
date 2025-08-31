import os
import json
from typing import Any, Dict

# Standard data directory resolution
def get_data_dir():
    """Get the consistent path to the data directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up to the project root and then to data directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    data_dir = os.path.join(project_root, 'data')
    return data_dir

def get_data_file_path(filename: str) -> str:
    """Get the full path to a data file"""
    return os.path.join(get_data_dir(), filename)

def _read_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {path}: {e}")
        return default

def _write_json(path: str, data: Any) -> None:
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as e:
        print(f"Error writing JSON file {path}: {e}")
        raise

def load_users(users_file: str = None) -> Dict[str, Any]:
    if users_file is None:
        users_file = get_data_file_path('users.json')
    return _read_json(users_file, {})

def save_users(users_file: str, data: Dict[str, Any]) -> None:
    _write_json(users_file, data)

def load_sessions(sessions_file: str = None) -> Dict[str, Any]:
    if sessions_file is None:
        sessions_file = get_data_file_path('sessions.json')
    return _read_json(sessions_file, {})

def save_sessions(sessions_file: str, data: Dict[str, Any]) -> None:
    _write_json(sessions_file, data)

def load_journeys(journeys_file: str = None) -> Dict[str, Any]:
    if journeys_file is None:
        journeys_file = get_data_file_path('journeys.json')
    return _read_json(journeys_file, {})

def save_journeys(journeys_file: str, data: Dict[str, Any]) -> None:
    _write_json(journeys_file, data)

def load_learning_paths(learning_paths_file: str = None) -> Dict[str, Any]:
    """Load learning paths with consistent structure handling"""
    if learning_paths_file is None:
        learning_paths_file = get_data_file_path('learning_paths.json')
    
    data = _read_json(learning_paths_file, {})
    
    # Ensure consistent dictionary format for internal use
    if isinstance(data, list):
        # Convert list to dictionary format
        converted = {}
        for item in data:
            if isinstance(item, dict) and 'id' in item:
                converted[item['id']] = item
        return converted
    
    return data

def save_learning_paths(learning_paths_file: str, data: Dict[str, Any]) -> None:
    _write_json(learning_paths_file, data)

def load_modules(modules_file: str = None) -> list:
    """Load modules with consistent structure handling"""
    if modules_file is None:
        modules_file = get_data_file_path('Module.json')
    
    data = _read_json(modules_file, [])
    
    # Ensure consistent list format
    if isinstance(data, dict):
        # Convert dictionary to list format
        converted = []
        for key, value in data.items():
            if isinstance(value, dict):
                # Ensure id field exists
                value['id'] = value.get('id', key)
                # Wrap in attributes if not already wrapped
                if 'attributes' not in value:
                    converted.append({'attributes': value})
                else:
                    converted.append(value)
        return converted
    
    return data

def save_modules(modules_file: str, data: list) -> None:
    _write_json(modules_file, data)

def load_departments(departments_file: str = None) -> Dict[str, Any]:
    if departments_file is None:
        departments_file = get_data_file_path('department.json')
    return _read_json(departments_file, {"departments": []})

def save_departments(departments_file: str, data: Dict[str, Any]) -> None:
    _write_json(departments_file, data)
