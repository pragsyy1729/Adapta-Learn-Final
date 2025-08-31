from flask import Blueprint, jsonify, request
from agent import supervisor
import json
from datetime import datetime, timedelta
from ..services.data_access import get_data_file_path

# Handles event-driven endpoints

events_bp = Blueprint('events', __name__)

# File path for events data
EVENTS_FILE = get_data_file_path('events.json')

def load_events():
    """Load events data from file"""
    try:
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"events": []}

def save_events(data):
    """Save events data to file"""
    with open(EVENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@events_bp.route('/events', methods=['GET', 'POST'])
def events():
    """Get upcoming events or create a new event"""
    if request.method == 'GET':
        try:
            events_data = load_events()
            events_list = events_data.get("events", [])

            # Filter for upcoming events (next 30 days)
            now = datetime.now()
            upcoming_events = []
            for event in events_list:
                try:
                    event_date = datetime.fromisoformat(event.get("date", ""))
                    if event_date >= now:
                        upcoming_events.append(event)
                except (ValueError, TypeError):
                    # Include events with invalid dates but mark them
                    event_copy = event.copy()
                    event_copy["date_issue"] = True
                    upcoming_events.append(event_copy)

            # Sort by date
            upcoming_events.sort(key=lambda x: x.get("date", ""), reverse=False)

            return jsonify(upcoming_events[:20])  # Limit to 20 events

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json() or {}
            events_data = load_events()

            # Create new event
            event = {
                "id": data.get("id", f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "date": data.get("date", ""),
                "time": data.get("time", ""),
                "location": data.get("location", ""),
                "organizer": data.get("organizer", ""),
                "attendees": data.get("attendees", []),
                "type": data.get("type", "other"),
                "created_at": datetime.now().isoformat()
            }

            # Add to events list
            events_list = events_data.get("events", [])
            events_list.append(event)
            events_data["events"] = events_list

            save_events(events_data)

            return jsonify({"success": True, "event": event})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

@events_bp.route('/<event_id>', methods=['GET', 'PUT', 'DELETE'])
def event_detail(event_id):
    """Get, update, or delete a specific event"""
    try:
        events_data = load_events()
        events_list = events_data.get("events", [])

        if request.method == 'GET':
            event = next((e for e in events_list if e.get("id") == event_id), None)
            if not event:
                return jsonify({"error": "Event not found"}), 404
            return jsonify(event)

        elif request.method == 'PUT':
            data = request.get_json() or {}
            for i, event in enumerate(events_list):
                if event.get("id") == event_id:
                    events_list[i].update(data)
                    save_events(events_data)
                    return jsonify({"success": True})

            return jsonify({"error": "Event not found"}), 404

        elif request.method == 'DELETE':
            events_list = [e for e in events_list if e.get("id") != event_id]
            events_data["events"] = events_list
            save_events(events_data)
            return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@events_bp.route('/module-completed', methods=['POST'])
def module_completed():
    data = request.get_json(force=True)
    event = {
        "type": "module_completed",
        "user_id": data.get("user_id"),
        "skill": data.get("skill"),
        "target_level": data.get("target_level"),
        "completion_type": data.get("completion_type"),
        "score": data.get("score"),
        "has_assessment": data.get("has_assessment"),
        "pass_threshold": data.get("pass_threshold"),
        "idempotency_key": data.get("idempotency_key")
    }
    result = supervisor.handle_event(event)
    if "error" in result:
        code = result["error"].get("code")
        if code == "MISSING_FIELD":
            return jsonify(result), 400
        elif code == "NOT_FOUND":
            return jsonify(result), 404
        elif code == "DUPLICATE":
            return jsonify(result), 409
        else:
            return jsonify(result), 400
    return jsonify(result)

@events_bp.route('/assessments/submit', methods=['POST'])
def assessment_submit():
    data = request.get_json(force=True)
    event = {
        "type": "assessment_submitted",
        "user_id": data.get("user_id"),
        "assessment_id": data.get("assessment_id"),
        "score": data.get("score"),
        "idempotency_key": data.get("idempotency_key")
    }
    result = supervisor.handle_event(event)
    if "error" in result:
        code = result["error"].get("code")
        if code == "MISSING_FIELD":
            return jsonify(result), 400
        elif code == "NOT_FOUND":
            return jsonify(result), 404
        elif code == "DUPLICATE":
            return jsonify(result), 409
        else:
            return jsonify(result), 400
    return jsonify(result)
