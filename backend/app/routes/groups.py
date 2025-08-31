from flask import Blueprint, jsonify, request
import json
import uuid
from datetime import datetime
from ..services.data_access import get_data_file_path

groups_bp = Blueprint('groups', __name__)

# File paths
GROUPS_FILE = get_data_file_path('groups.json')
GROUP_INVITES_FILE = get_data_file_path('group_invites.json')

def load_groups():
    """Load groups data from file"""
    try:
        with open(GROUPS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"groups": {}}

def save_groups(data):
    """Save groups data to file"""
    with open(GROUPS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_group_invites():
    """Load group invites data from file"""
    try:
        with open(GROUP_INVITES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"invites": {}}

def save_group_invites(data):
    """Save group invites data to file"""
    with open(GROUP_INVITES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@groups_bp.route('', methods=['GET', 'POST'])
def groups():
    """Get all groups or create a new group"""
    if request.method == 'GET':
        try:
            groups_data = load_groups()
            # Return groups where current user is a member
            user_id = request.args.get('user_id')
            if user_id:
                user_groups = []
                for group_id, group in groups_data.get("groups", {}).items():
                    if user_id in group.get("members", []):
                        user_groups.append(group)
                return jsonify(user_groups)
            else:
                return jsonify(list(groups_data.get("groups", {}).values()))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json() or {}
            groups_data = load_groups()
            invites_data = load_group_invites()

            # Create new group
            group_id = str(uuid.uuid4())
            group = {
                "id": group_id,
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "created_by": data.get("created_by", ""),
                "members": [data.get("created_by", "")],  # Creator is automatically a member
                "pending_invites": [],
                "created_at": datetime.now().isoformat(),
                "category": data.get("category", "general")
            }

            # Save group
            groups_data["groups"][group_id] = group
            save_groups(groups_data)

            # Create invites for specified emails
            invite_emails = data.get("invite_emails", [])
            for email in invite_emails:
                if email.strip():
                    invite_id = str(uuid.uuid4())
                    invite = {
                        "id": invite_id,
                        "group_id": group_id,
                        "group_name": group["name"],
                        "invited_by": data.get("created_by", ""),
                        "invited_user": email.strip(),
                        "status": "pending",
                        "created_at": datetime.now().isoformat()
                    }
                    invites_data["invites"][invite_id] = invite

                    # Add to group's pending invites
                    group["pending_invites"].append(email.strip())

            # Save updated group and invites
            save_groups(groups_data)
            save_group_invites(invites_data)

            return jsonify({
                "success": True,
                "group": group,
                "invites_sent": len(invite_emails)
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

@groups_bp.route('/<group_id>', methods=['GET', 'PUT', 'DELETE'])
def group_detail(group_id):
    """Get, update, or delete a specific group"""
    try:
        groups_data = load_groups()

        if request.method == 'GET':
            group = groups_data.get("groups", {}).get(group_id)
            if not group:
                return jsonify({"error": "Group not found"}), 404
            return jsonify(group)

        elif request.method == 'PUT':
            data = request.get_json() or {}
            if group_id not in groups_data.get("groups", {}):
                return jsonify({"error": "Group not found"}), 404

            # Update group data
            groups_data["groups"][group_id].update(data)
            save_groups(groups_data)
            return jsonify({"success": True})

        elif request.method == 'DELETE':
            if group_id in groups_data.get("groups", {}):
                del groups_data["groups"][group_id]
                save_groups(groups_data)
            return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@groups_bp.route('/invites/<user_identifier>', methods=['GET'])
def get_user_invites(user_identifier):
    """Get pending invites for a user (by user_id or email)"""
    try:
        invites_data = load_group_invites()
        user_invites = []

        for invite_id, invite in invites_data.get("invites", {}).items():
            # Check if user_identifier matches either user_id or email
            invited_user = invite.get("invited_user", "")
            if (invited_user == user_identifier and
                invite.get("status") == "pending"):
                user_invites.append(invite)

        return jsonify(user_invites)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@groups_bp.route('/invites/<invite_id>', methods=['POST'])
def respond_to_invite(invite_id):
    """Accept or decline a group invite"""
    try:
        data = request.get_json() or {}
        accept = data.get("accept", False)

        invites_data = load_group_invites()
        groups_data = load_groups()

        invite = invites_data.get("invites", {}).get(invite_id)
        if not invite:
            return jsonify({"error": "Invite not found"}), 404

        if accept:
            # Add user to group members
            group_id = invite.get("group_id")
            user_id = invite.get("invited_user")

            if group_id in groups_data.get("groups", {}):
                group = groups_data["groups"][group_id]
                if user_id not in group.get("members", []):
                    group["members"].append(user_id)

                # Remove from pending invites
                if user_id in group.get("pending_invites", []):
                    group["pending_invites"].remove(user_id)

                save_groups(groups_data)

            invite["status"] = "accepted"
        else:
            invite["status"] = "declined"

        save_group_invites(invites_data)

        return jsonify({"success": True, "action": "accepted" if accept else "declined"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@groups_bp.route('/<group_id>/members', methods=['POST'])
def add_group_member(group_id):
    """Add a member to a group"""
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "user_id required"}), 400

        groups_data = load_groups()

        if group_id not in groups_data.get("groups", {}):
            return jsonify({"error": "Group not found"}), 404

        group = groups_data["groups"][group_id]
        if user_id not in group.get("members", []):
            group["members"].append(user_id)
            save_groups(groups_data)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@groups_bp.route('/<group_id>/invite', methods=['POST'])
def invite_to_group(group_id):
    """Send invites to join a group"""
    try:
        data = request.get_json() or {}
        emails = data.get("emails", [])
        invited_by = data.get("invited_by", "")

        if not emails or not invited_by:
            return jsonify({"error": "emails and invited_by required"}), 400

        groups_data = load_groups()
        invites_data = load_group_invites()

        if group_id not in groups_data.get("groups", {}):
            return jsonify({"error": "Group not found"}), 404

        group = groups_data["groups"][group_id]
        sent_invites = []

        for email in emails:
            if email.strip():
                # Check if user is already a member
                if email.strip() in group.get("members", []):
                    continue

                # Check if invite already exists
                existing_invite = None
                for invite_id, invite in invites_data.get("invites", {}).items():
                    if (invite.get("group_id") == group_id and
                        invite.get("invited_user") == email.strip() and
                        invite.get("status") == "pending"):
                        existing_invite = invite
                        break

                if existing_invite:
                    continue

                # Create new invite
                invite_id = str(uuid.uuid4())
                invite = {
                    "id": invite_id,
                    "group_id": group_id,
                    "group_name": group["name"],
                    "invited_by": invited_by,
                    "invited_user": email.strip(),
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                }

                invites_data["invites"][invite_id] = invite
                group["pending_invites"].append(email.strip())
                sent_invites.append(invite)

        save_groups(groups_data)
        save_group_invites(invites_data)

        return jsonify({
            "success": True,
            "invites_sent": len(sent_invites),
            "invites": sent_invites
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
