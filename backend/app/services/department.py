import os
import uuid
from typing import Any, Dict, List, Optional
from .data_access import get_data_file_path, _read_json, _write_json


DEPT_FILE = get_data_file_path('department.json')


def load_departments() -> Dict[str, Any]:
    return _read_json(DEPT_FILE, {"departments": []})


def save_departments(data: Dict[str, Any]) -> None:
    _write_json(DEPT_FILE, data)


def find_department_by_name(name: str) -> Optional[Dict[str, Any]]:
    if not name:
        return None
    depts = load_departments().get('departments', [])
    lower = name.strip().lower()
    for d in depts:
        if (d.get('name') or '').strip().lower() == lower or (d.get('id') or '').strip().lower() == lower:
            return d
    return None


def get_department_by_id(dept_id: str) -> Optional[Dict[str, Any]]:
    if not dept_id:
        return None
    depts = load_departments().get('departments', [])
    target = dept_id.strip().lower()
    for d in depts:
        if (d.get('id') or '').strip().lower() == target:
            return d
    return None


def list_departments() -> List[Dict[str, Any]]:
    return load_departments().get('departments', [])


def create_department(dept_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new department record. If `id` is not provided, a UUID-based id is generated."""
    data = load_departments()
    depts = data.get('departments', [])

    # Ensure id
    if not dept_data.get('id'):
        dept_data['id'] = f"dept_{str(uuid.uuid4())[:8]}"

    # Ensure managers array exists
    if 'managers' not in dept_data or not isinstance(dept_data['managers'], list):
        dept_data['managers'] = []

    depts.append(dept_data)
    data['departments'] = depts
    save_departments(data)
    return dept_data


def update_department(dept_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = load_departments()
    modified = False
    for idx, d in enumerate(data.get('departments', [])):
        if (d.get('id') or '').strip().lower() == (dept_id or '').strip().lower():
            # merge updates shallowly
            for k, v in updates.items():
                if k == 'managers' and not isinstance(v, list):
                    continue
                d[k] = v
            data['departments'][idx] = d
            modified = True
            break

    if modified:
        save_departments(data)
        return d
    return None


def delete_department(dept_id: str) -> bool:
    data = load_departments()
    original_len = len(data.get('departments', []))
    data['departments'] = [d for d in data.get('departments', []) if (d.get('id') or '').strip().lower() != (dept_id or '').strip().lower()]
    if len(data['departments']) < original_len:
        save_departments(data)
        return True
    return False


def add_manager_to_department(department_name: str, manager_name: str) -> bool:
    """Append manager_name to the department.managers array if not present.
    Returns True if modified, False otherwise.
    """
    if not department_name or not manager_name:
        return False
    data = load_departments()
    modified = False
    for d in data.get('departments', []):
        if (d.get('name') or '').strip().lower() == department_name.strip().lower() or (d.get('id') or '').strip().lower() == department_name.strip().lower():
            if 'managers' not in d or not isinstance(d['managers'], list):
                d['managers'] = []
            # Avoid duplicates (compare normalized)
            existing = [m.strip().lower() for m in d['managers'] if isinstance(m, str)]
            if manager_name.strip().lower() not in existing:
                d['managers'].append(manager_name)
                modified = True
            break

    if modified:
        save_departments(data)

    return modified


def remove_manager_from_department(department_name: str, manager_name: str) -> bool:
    """Remove manager_name from department.managers array. Returns True if removed."""
    if not department_name or not manager_name:
        return False
    data = load_departments()
    modified = False
    for d in data.get('departments', []):
        if (d.get('name') or '').strip().lower() == department_name.strip().lower() or (d.get('id') or '').strip().lower() == department_name.strip().lower():
            if 'managers' in d and isinstance(d['managers'], list):
                before = len(d['managers'])
                d['managers'] = [m for m in d['managers'] if (m or '').strip().lower() != manager_name.strip().lower()]
                if len(d['managers']) < before:
                    modified = True
            break

    if modified:
        save_departments(data)

    return modified


def list_managers(department_name: str) -> List[str]:
    d = find_department_by_name(department_name)
    if not d:
        return []
    return d.get('managers', [])
