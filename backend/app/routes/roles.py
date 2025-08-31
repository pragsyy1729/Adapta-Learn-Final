from flask import Blueprint, jsonify, request
import json
import os
import uuid

roles_bp = Blueprint('roles', __name__)
ROLES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/roles.json')

def load_roles():
    with open(ROLES_PATH, 'r') as f:
        return json.load(f)

def save_roles(data):
    with open(ROLES_PATH, 'w') as f:
        json.dump(data, f, indent=2)

@roles_bp.route('/roles', methods=['GET'])
def get_roles():
    return jsonify(load_roles()["roles"])

@roles_bp.route('/roles/<role_id>', methods=['GET'])
def get_role(role_id):
    roles = load_roles()["roles"]
    for role in roles:
        if role["id"] == role_id:
            return jsonify(role)
    return jsonify({"error": "Role not found"}), 404

@roles_bp.route('/roles', methods=['POST'])
def add_role():
    data = request.json
    roles_data = load_roles()
    new_role = {
        "id": str(uuid.uuid4()),
        "name": data["name"],
        "skills": data.get("skills", [])
    }
    roles_data["roles"].append(new_role)
    save_roles(roles_data)
    return jsonify(new_role)

@roles_bp.route('/roles/<role_id>', methods=['PUT'])
def edit_role(role_id):
    data = request.json
    roles_data = load_roles()
    for role in roles_data["roles"]:
        if role["id"] == role_id:
            role["name"] = data.get("name", role["name"])
            role["skills"] = data.get("skills", role["skills"])
            save_roles(roles_data)
            return jsonify(role)
    return jsonify({"error": "Role not found"}), 404

@roles_bp.route('/roles/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    roles_data = load_roles()
    roles_data["roles"] = [r for r in roles_data["roles"] if r["id"] != role_id]
    save_roles(roles_data)
    return jsonify({"success": True})

@roles_bp.route('/roles/<role_id>/skills', methods=['POST'])
def add_skill(role_id):
    data = request.json
    roles_data = load_roles()
    for role in roles_data["roles"]:
        if role["id"] == role_id:
            role["skills"].append({"name": data["name"], "proficiency": data["proficiency"]})
            save_roles(roles_data)
            return jsonify(role)
    return jsonify({"error": "Role not found"}), 404

@roles_bp.route('/roles/<role_id>/skills/<skill_name>', methods=['DELETE'])
def delete_skill(role_id, skill_name):
    roles_data = load_roles()
    for role in roles_data["roles"]:
        if role["id"] == role_id:
            role["skills"] = [s for s in role["skills"] if s["name"] != skill_name]
            save_roles(roles_data)
            return jsonify(role)
    return jsonify({"error": "Role not found"}), 404
