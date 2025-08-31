from flask import Blueprint, request, jsonify
from ..services.conversation_agent import conversation_agent
import traceback
import json
import os

conversation_bp = Blueprint('conversation', __name__)

def load_users() -> dict:
    """Load users from JSON file."""
    users_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'users.json')
    try:
        with open(users_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def load_departments() -> dict:
    """Load departments from JSON file."""
    departments_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'department.json')
    try:
        with open(departments_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading departments: {e}")
        return {"departments": []}

def get_user_department(user_id: str) -> dict:
    """
    Get user's department information by user_id.
    Returns: {'name': str, 'id': str, 'found': bool}
    """
    try:
        users = load_users()
        departments = load_departments()

        # Find user by user_id
        user_data = None
        for email, data in users.items():
            if data.get('user_id') == user_id:
                user_data = data
                break

        if not user_data:
            print(f"WARNING: User {user_id} not found in users.json")
            return {'name': '', 'id': '', 'found': False}

        # Get department from profile
        department_name = user_data.get('profile', {}).get('department', '')

        if not department_name:
            print(f"WARNING: No department assigned for user {user_id}")
            return {'name': '', 'id': '', 'found': False}

        # Map department name to department ID
        department_id_mapping = {
            'KYC': 'KYC2024001',
            'Engineering': 'ENG2024001', 
            'Data Science': 'DS2024001',
            'Product Management': 'PM2024001',
            'Design': 'DES2024001',
            'Marketing': 'MKT2024001',
            'IT': 'IT2024001'
        }

        # Check if department_name is already a full department ID (ends with year pattern like 2024001)
        if department_name.endswith('2024001') or department_name.endswith('2024002'):
            department_id = department_name
        else:
            # Otherwise map from name to ID
            department_id = department_id_mapping.get(department_name, department_name)        # Validate department exists
        dept_exists = any(dept['id'] == department_id for dept in departments.get('departments', []))

        if not dept_exists:
            print(f"WARNING: Department {department_id} not found in department.json")
            return {'name': department_name, 'id': department_id, 'found': False}

        print(f"SUCCESS: User {user_id} -> Department: {department_name} (ID: {department_id})")
        return {'name': department_name, 'id': department_id, 'found': True}

    except Exception as e:
        print(f"ERROR: Exception getting user department: {e}")
        return {'name': '', 'id': '', 'found': False}

def get_department_fallback_options() -> list:
    """Get list of available departments for fallback selection."""
    try:
        departments = load_departments()
        return [
            {
                'id': dept['id'],
                'name': dept['name'],
                'description': dept['description']
            }
            for dept in departments.get('departments', [])
        ]
    except Exception as e:
        print(f"Error getting department options: {e}")
        return []

@conversation_bp.route('/ask', methods=['POST'])
def ask_question():
    """Handle conversation agent questions."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        question = data.get('question', '').strip()
        user_id = data.get('user_id', '').strip()

        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID is required'
            }), 400

        print(f"DEBUG: Processing question: {question}")
        print(f"DEBUG: User ID: {user_id}")

        # Get user's department information
        dept_info = get_user_department(user_id)

        if not dept_info['found']:
            if not dept_info['name']:
                # User not found or no department assigned
                fallback_options = get_department_fallback_options()
                return jsonify({
                    'success': False,
                    'error': 'Department not assigned',
                    'answer': 'Your profile doesn\'t have a department assigned. Please contact your administrator to update your profile with department information.',
                    'user_id': user_id,
                    'fallback_options': fallback_options
                }), 400
            else:
                # Department found but not in department.json
                print(f"WARNING: Department {dept_info['name']} exists but not in department.json")

        department_name = dept_info['name']
        department_id = dept_info['id']

        print(f"DEBUG: User {user_id} | Dept: {department_name} | ID: {department_id} | Question: {question[:50]}...")

        # Process the question using the conversation agent
        result = conversation_agent.process_question(
            question=question,
            department_id=department_id,
            department_name=department_name
        )

        if 'error' in result:
            print(f"ERROR: Conversation agent failed for user {user_id}: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error'],
                'answer': result.get('answer', 'An error occurred while processing your question.')
            }), 500

        print(f"SUCCESS: User {user_id} | Chunks: {result.get('chunks_found', 0)} | Response: {len(result.get('answer', ''))} chars")
        return jsonify({
            'success': True,
            'answer': result.get('answer', ''),
            'chunks_found': result.get('chunks_found', 0),
            'department': result.get('department', department_name),
            'department_id': department_id,
            'context_summary': result.get('context_summary', '')
        })

    except Exception as e:
        print(f"Error in conversation ask endpoint: {e}")
        print(f"Traceback: {traceback.format_exc()}")

        return jsonify({
            'success': False,
            'error': str(e),
            'answer': 'I apologize, but I encountered an error while processing your question. Please try again.'
        }), 500

@conversation_bp.route('/health', methods=['GET'])
def conversation_health():
    """Health check for conversation service."""
    try:
        from ..services.job_queue import job_queue

        # Get job queue stats
        total_jobs = len(job_queue.jobs)
        active_jobs = len([j for j in job_queue.jobs.values() if j.status == 'processing'])
        pending_jobs = job_queue.job_queue.qsize()

        return jsonify({
            'status': 'healthy',
            'service': 'conversation_agent',
            'message': 'Conversation agent is running',
            'job_queue': {
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'pending_jobs': pending_jobs,
                'worker_running': job_queue.worker_thread.is_alive() if job_queue.worker_thread else False
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'conversation_agent',
            'error': str(e)
        }), 500

@conversation_bp.route('/stats/<department_id>', methods=['GET'])
def get_department_stats(department_id):
    """Get statistics about a department's knowledge base."""
    try:
        from ..services.document_processor import document_processor

        stats = document_processor.get_department_stats(department_id)

        return jsonify({
            'success': True,
            'department_id': department_id,
            'stats': stats
        })

    except Exception as e:
        print(f"Error getting department stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@conversation_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document for a department asynchronously."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        department_id = request.form.get('department_id', '').strip()
        user_id = request.form.get('user_id', '').strip()

        if not file or not department_id:
            return jsonify({
                'success': False,
                'error': 'File and department_id are required'
            }), 400

        # Save file temporarily (don't delete it yet - job queue will handle cleanup)
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            # Import job queue service
            from ..services.job_queue import job_queue

            # Submit job to queue
            job_id = job_queue.submit_job(
                department_id=department_id,
                filename=file.filename,
                file_path=temp_path,
                user_id=user_id
            )

            return jsonify({
                'success': True,
                'message': f'Document {file.filename} queued for processing',
                'job_id': job_id,
                'department_id': department_id
            })

        except Exception as e:
            # Clean up temp file if job submission failed
            try:
                os.unlink(temp_path)
            except:
                pass
            raise e

    except Exception as e:
        print(f"Error uploading document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@conversation_bp.route('/departments/<department_id>/processing', methods=['GET'])
def get_department_processing_jobs(department_id):
    """Get processing jobs for a specific department."""
    try:
        from ..services.job_queue import job_queue

        jobs = job_queue.get_department_jobs(department_id)
        job_dicts = [job.to_dict() for job in jobs]

        return jsonify({
            'success': True,
            'processing_jobs': job_dicts
        })
    except Exception as e:
        print(f"Error getting processing jobs for department {department_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@conversation_bp.route('/processing/<processing_id>/status', methods=['GET'])
def get_processing_status(processing_id):
    """Get status of a specific processing job."""
    try:
        from ..services.job_queue import job_queue

        job = job_queue.get_job(processing_id)

        if not job:
            return jsonify({
                'success': False,
                'error': f'Job {processing_id} not found'
            }), 404

        job_data = job.to_dict()

        return jsonify({
            'success': True,
            'processing_id': processing_id,
            'status': job_data['status'],
            'progress': job_data['progress'],
            'current_step': job_data['current_step'],
            'total_steps': job_data['total_steps'],
            'completed_steps': job_data['completed_steps'],
            'elapsed_time': job_data['elapsed_time'],
            'message': f"Document processing {job_data['status']}",
            'processing_details': job_data['processing_details'],
            'created_at': job_data['created_at'],
            'started_at': job_data['started_at'],
            'completed_at': job_data['completed_at']
        })
    except Exception as e:
        print(f"Error getting processing status for {processing_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@conversation_bp.route('/jobs/cleanup', methods=['POST'])
def cleanup_old_jobs():
    """Clean up old completed/failed jobs."""
    try:
        from ..services.job_queue import job_queue

        # Default to 24 hours, but allow custom max_age_hours
        max_age_hours = int(request.args.get('max_age_hours', 24))

        job_queue.cleanup_old_jobs(max_age_hours)

        return jsonify({
            'success': True,
            'message': f'Cleaned up jobs older than {max_age_hours} hours'
        })
    except Exception as e:
        print(f"Error cleaning up old jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@conversation_bp.route('/departments', methods=['GET'])
def get_departments():
    """Get list of all available departments."""
    try:
        departments = load_departments()
        return jsonify({
            'success': True,
            'departments': departments.get('departments', [])
        })
    except Exception as e:
        print(f"Error getting departments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
