
from flask import Blueprint, jsonify, request
import os
import uuid
import sys
from datetime import datetime
from werkzeug.utils import secure_filename
from ..services.data_access import (
    load_learning_paths, save_learning_paths, 
    load_modules, save_modules,
    load_users, save_users,
    load_journeys, load_departments, save_departments,
    get_data_file_path
)

# Import sync utility
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from utils.sync_learning_paths import update_learning_path_module_count, sync_learning_path_module_counts
except ImportError:
    # Fallback if import fails
    def update_learning_path_module_count(learning_path_id): return 0
    def sync_learning_path_module_counts(): return {}

admin_bp = Blueprint('admin', __name__)

# Use consistent file paths
LEARNING_PATHS_FILE = get_data_file_path('learning_paths.json')
MODULES_FILE = get_data_file_path('Module.json')

# --- Admin: Stats ---
@admin_bp.route('/stats/new-joiners', methods=['GET'])
def admin_stats_new_joiners():
    users = load_users()
    total = 0
    this_month = 0
    now = datetime.utcnow()
    for u in users.values():
        if str(u.get("newJoiner", "")).strip().lower() in ("yes", "y", "true", "1"):
            total += 1
            doj = u.get("dateOfJoining")
            if doj:
                try:
                    doj_date = datetime.strptime(doj[:10], "%Y-%m-%d")
                    if doj_date.year == now.year and doj_date.month == now.month:
                        this_month += 1
                except Exception:
                    pass
    return jsonify({"total_new_joiners": total, "joined_this_month": this_month})

@admin_bp.route('/stats/active-enrollments', methods=['GET'])
def admin_stats_active_enrollments():
    users = load_users()
    count = 0

    for user_email, user_data in users.items():
        try:
            profile = user_data.get('profile', {})

            # Check if user has learning paths assigned
            learning_paths = profile.get('learning_paths', [])
            enrollments = profile.get('enrollments', [])

            # Also check for learning_path_materials (alternative format)
            learning_path_materials = profile.get('learning_path_materials', {})

            # Count as enrolled if they have any learning paths or enrollments
            if (learning_paths or enrollments or learning_path_materials):
                count += 1

        except Exception as e:
            # Skip malformed user data
            continue

    return jsonify({"active_enrollments": count})

@admin_bp.route('/stats/onboarding-analytics', methods=['GET'])
def get_onboarding_analytics():
    """Get onboarding analytics data"""
    try:
        # Load onboarding recommendations
        recommendations_file = get_data_file_path('onboarding_recommendations.json')
        import json
        try:
            with open(recommendations_file, 'r') as f:
                recommendations_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            recommendations_data = {"recommendations": {}}
        
        # Calculate basic analytics
        total_recommendations = len(recommendations_data.get("recommendations", {}))
        
        # Mock analytics data for now
        analytics = {
            "total_onboarded": total_recommendations,
            "average_completion_time": 8.5,  # weeks
            "success_rate": 92  # percentage
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Admin: Learning Path Management ---
@admin_bp.route('/learning-paths', methods=['GET', 'POST'])
def admin_learning_paths():
    if request.method == "GET":
        try:
            # Load learning paths with consistent structure handling
            paths_data = load_learning_paths()
            users_data = load_users()
            
            # Convert to list format for API response
            learning_paths_list = []
            if isinstance(paths_data, dict):
                for path_id, path_data in paths_data.items():
                    if isinstance(path_data, dict):
                        path_data['id'] = path_data.get('id', path_id)
                        learning_paths_list.append(path_data)
            else:
                learning_paths_list = paths_data
            
            # Calculate enrollment counts for each learning path
            for path_data in learning_paths_list:
                path_id = path_data.get('id')
                if not path_id:
                    continue
                    
                enrolled_count = 0
                for user_email, user_data in users_data.items():
                    try:
                        profile = user_data.get('profile', {})
                        learning_paths = profile.get('learning_paths', [])
                        enrollments = profile.get('enrollments', [])
                        
                        # Check if user is enrolled in this learning path
                        is_enrolled = False
                        
                        # Check direct learning_paths array
                        if path_id in learning_paths:
                            is_enrolled = True
                        
                        # Check enrollments array
                        if not is_enrolled:
                            for enrollment in enrollments:
                                if isinstance(enrollment, dict) and enrollment.get('learning_path_id') == path_id:
                                    is_enrolled = True
                                    break
                        
                        if is_enrolled:
                            enrolled_count += 1
                    except Exception:
                        continue
                
                path_data['enrolledUsers'] = enrolled_count
            
            return jsonify(learning_paths_list)
        except Exception as e:
            print(f"Error in admin learning paths GET: {e}")
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":
        try:
            paths = load_learning_paths()
            payload = request.get_json(force=True) or {}
            path_id = payload.get("id") or uuid.uuid4().hex
            payload["id"] = path_id
            if not payload.get("status"):
                payload["status"] = "active"
            if "department" in payload:
                payload["department"] = payload["department"]
            paths[path_id] = payload
            save_learning_paths(LEARNING_PATHS_FILE, paths)
            return jsonify({"success": True, "id": path_id, "department": payload.get("department")})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@admin_bp.route('/learning-paths/<path_id>', methods=['PUT', 'DELETE'])
def admin_learning_path_detail(path_id):
    if request.method == "PUT":
        try:
            paths = load_learning_paths()
            payload = request.get_json(force=True) or {}
            payload["id"] = path_id
            paths[path_id] = payload
            save_learning_paths(LEARNING_PATHS_FILE, paths)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "DELETE":
        try:
            paths = load_learning_paths()
            if path_id in paths:
                del paths[path_id]
                save_learning_paths(LEARNING_PATHS_FILE, paths)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# --- Admin: User Management ---
@admin_bp.route('/users', methods=['GET', 'POST'])
def admin_users():
    if request.method == "GET":
        try:
            users = load_users()
            return jsonify(list(users.values()))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":
        try:
            users = load_users()
            payload = request.get_json(force=True) or {}
            email = payload.get("email", "").strip().lower()
            if not email:
                return jsonify({"error": "email required"}), 400
            users[email] = payload
            save_users(get_data_file_path('users.json'), users)
            return jsonify({"success": True, "email": email})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@admin_bp.route('/users/<email>', methods=['PUT', 'DELETE'])
def admin_user_detail(email):
    try:
        users = load_users()
        email = email.strip().lower()
        if request.method == "PUT":
            payload = request.get_json(force=True) or {}
            users[email] = payload
            save_users(get_data_file_path('users.json'), users)
            return jsonify({"success": True})
        elif request.method == "DELETE":
            if email in users:
                del users[email]
                save_users(get_data_file_path('users.json'), users)
            return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Admin: Module Management ---
@admin_bp.route('/modules', methods=['GET', 'POST'])
def admin_modules():
    if request.method == "GET":
        try:
            modules = load_modules()
            
            # Load learning materials to calculate actual chapter counts
            materials_file = get_data_file_path('learning_materials.json')
            import json
            try:
                with open(materials_file, 'r') as f:
                    all_materials = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                all_materials = []
            
            # Calculate chapter counts per module
            module_chapter_counts = {}
            for material in all_materials:
                module_id = material.get('module_id')
                chapter_id = material.get('chapter_id')
                if module_id and chapter_id:
                    if module_id not in module_chapter_counts:
                        module_chapter_counts[module_id] = set()
                    module_chapter_counts[module_id].add(chapter_id)
            
            # Convert Module.json format to admin-friendly format
            admin_modules = []
            for m in modules:
                if isinstance(m, dict) and 'attributes' in m:
                    module_data = m['attributes'].copy()
                    module_data.pop('type', None)
                    admin_modules.append(module_data)
                else:
                    # Handle legacy format
                    if isinstance(m, dict):
                        m.pop('type', None)
                        admin_modules.append(m)
            
            # Update chapter counts with actual calculated values
            for module in admin_modules:
                module_id = module.get('id')
                if module_id in module_chapter_counts:
                    actual_chapter_count = len(module_chapter_counts[module_id])
                    module['chapter_count'] = actual_chapter_count
                    print(f"Updated {module_id}: chapter_count = {actual_chapter_count}")
                else:
                    # If no chapters found, set to 0
                    module['chapter_count'] = 0
                    print(f"No chapters found for {module_id}, setting chapter_count = 0")
            
            return jsonify(admin_modules)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "POST":
        try:
            modules = load_modules()
            data = request.get_json(force=True) or {}
            module_id = data.get("id") or uuid.uuid4().hex
            data["id"] = module_id
            
            # Initialize chapter_count to 0 for new modules
            if 'chapter_count' not in data:
                data['chapter_count'] = 0
            
            # Convert to Module.json format with attributes wrapper
            new_module = {"attributes": data}
            
            # Remove existing module with same id and add new one
            modules = [m for m in modules if m.get('attributes', {}).get("id") != module_id and m.get("id") != module_id]
            modules.append(new_module)
            save_modules(MODULES_FILE, modules)
            
            # Auto-sync module counts for affected learning path
            learning_path_id = data.get('learning_path_id')
            if learning_path_id:
                try:
                    update_learning_path_module_count(learning_path_id)
                except Exception as e:
                    print(f"Warning: Failed to sync module count for {learning_path_id}: {e}")
            
            return jsonify({"success": True, "id": module_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# --- Admin: Department Management ---

# Get all departments (full objects)
@admin_bp.route('/departments', methods=['GET'])
def get_departments():
    """Get all departments (full objects) for admin management"""
    departments_file = get_data_file_path('department.json')
    departments_data = load_departments(departments_file)
    return jsonify(departments_data.get("departments", []))

# Add or update documentation for a department
@admin_bp.route('/departments/<dept_id>/documentation', methods=['POST', 'PUT'])
def add_update_department_documentation(dept_id):
    """Add or update documentation for a department. Payload: {"name": str, "content": str}"""
    departments_file = get_data_file_path('department.json')
    departments_data = load_departments(departments_file)
    departments = departments_data.get("departments", [])
    payload = request.get_json(force=True) or {}
    doc_name = payload.get("name", "").strip()
    doc_content = payload.get("document_content", "").strip()
    if not doc_name or not doc_content:
        return jsonify({"error": "Both 'name' and 'document_content' are required."}), 400
    updated = False
    for dept in departments:
        if dept.get("id") == dept_id:
            if "documentation" not in dept or not isinstance(dept["documentation"], list):
                dept["documentation"] = []
            # Check if doc with same name exists
            for doc in dept["documentation"]:
                if doc.get("name") == doc_name:
                    doc["document_content"] = doc_content
                    updated = True
                    break
            if not updated:
                dept["documentation"].append({"name": doc_name, "document_content": doc_content})
            save_departments(departments_file, departments_data)
            return jsonify({"success": True, "updated": updated})
    return jsonify({"error": "Department not found"}), 404

# Get documentation for a department
@admin_bp.route('/departments/<dept_id>/documentation', methods=['GET'])
def get_department_documentation(dept_id):
    departments_file = get_data_file_path('department.json')
    departments_data = load_departments(departments_file)
    departments = departments_data.get("departments", [])
    for dept in departments:
        if dept.get("id") == dept_id:
            return jsonify(dept.get("documentation", []))
    return jsonify([])

@admin_bp.route('/modules/<module_id>', methods=['PUT', 'DELETE'])
def admin_module_detail(module_id):
    if request.method == "PUT":
        try:
            modules = load_modules()
            data = request.get_json(force=True) or {}
            data["id"] = module_id
            found = False
            learning_path_id = data.get('learning_path_id')
            
            # Don't override chapter_count if it's not provided in the update
            # The GET endpoint will calculate the actual count dynamically
            
            for idx, m in enumerate(modules):
                # Check both new format (attributes) and legacy format
                m_id = m.get('attributes', {}).get("id") or m.get("id")
                if m_id == module_id:
                    # Preserve existing chapter_count if not provided in update
                    existing_chapter_count = m.get('attributes', {}).get('chapter_count') or m.get('chapter_count')
                    if 'chapter_count' not in data and existing_chapter_count is not None:
                        data['chapter_count'] = existing_chapter_count
                    
                    # Update in Module.json format
                    modules[idx] = {"attributes": data}
                    found = True
                    break
            if not found:
                # Add new module in Module.json format
                modules.append({"attributes": data})
            save_modules(MODULES_FILE, modules)
            
            # Auto-sync module counts for affected learning path
            if learning_path_id:
                try:
                    update_learning_path_module_count(learning_path_id)
                except Exception as e:
                    print(f"Warning: Failed to sync module count for {learning_path_id}: {e}")
            
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "DELETE":
        try:
            modules = load_modules()
            # Get the learning_path_id before deleting for sync
            deleted_learning_path_ids = set()
            for m in modules:
                m_id = m.get('attributes', {}).get("id") or m.get("id")
                if m_id == module_id:
                    learning_path_id = m.get('attributes', {}).get('learning_path_id') or m.get('learning_path_id')
                    if learning_path_id:
                        deleted_learning_path_ids.add(learning_path_id)
            
            # Remove module checking both formats
            new_modules = [m for m in modules if 
                          m.get('attributes', {}).get("id") != module_id and 
                          m.get("id") != module_id]
            save_modules(MODULES_FILE, new_modules)
            
            # Auto-sync module counts for affected learning paths
            for learning_path_id in deleted_learning_path_ids:
                try:
                    update_learning_path_module_count(learning_path_id)
                except Exception as e:
                    print(f"Warning: Failed to sync module count for {learning_path_id}: {e}")
            
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@admin_bp.route('/sync-module-counts', methods=['POST'])
def sync_all_module_counts():
    """Manually trigger sync of all learning path module counts"""
    try:
        counts = sync_learning_path_module_counts()
        return jsonify({
            "success": True, 
            "message": f"Synced module counts for {len(counts)} learning paths",
            "counts": counts
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Admin: Module Materials Management ---
@admin_bp.route('/modules/<module_id>/chapters', methods=['GET', 'POST'])
def admin_module_chapters(module_id):
    """Get or create chapters for a module"""
    if request.method == "GET":
        try:
            # Load learning materials for this module
            materials_file = get_data_file_path('learning_materials.json')
            import json
            try:
                with open(materials_file, 'r') as f:
                    all_materials = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                all_materials = []

            # Filter materials for this module
            module_materials = [m for m in all_materials if m.get('module_id') == module_id]

            # Group by chapter
            chapters = {}
            for material in module_materials:
                chapter_id = material.get('chapter_id')
                # If chapter_id is None or missing, generate one
                if not chapter_id:
                    chapter_id = f"CH_{module_id}_{uuid.uuid4().hex[:8]}"
                    # Update the material with the new chapter_id
                    material['chapter_id'] = chapter_id

                if chapter_id not in chapters:
                    chapters[chapter_id] = {
                        'id': chapter_id,
                        'title': material.get('title', f'Chapter {chapter_id}'),
                        'materials': {
                            'visual': [],
                            'auditory': [],
                            'reading_writing': []
                        }
                    }

                # Add material to appropriate learning style category
                materials_dict = material.get('materials', {})
                for style, style_materials in materials_dict.items():
                    if style in chapters[chapter_id]['materials']:
                        chapters[chapter_id]['materials'][style].extend(style_materials)

            # Save updated materials back to file if any chapter_ids were fixed
            with open(materials_file, 'w') as f:
                json.dump(all_materials, f, indent=2)

            return jsonify({
                'module_id': module_id,
                'chapters': list(chapters.values())
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        try:
            data = request.get_json(force=True) or {}
            chapter_id = data.get('id') or f"CH_{module_id}_{uuid.uuid4().hex[:8]}"
            title = data.get('title', f'Chapter {chapter_id}')

            # Create new chapter structure
            new_chapter = {
                'id': chapter_id,
                'module_id': module_id,
                'title': title,
                'materials': {
                    'visual': [],
                    'auditory': [],
                    'reading_writing': []
                }
            }

            # Load existing materials
            materials_file = get_data_file_path('learning_materials.json')
            import json
            try:
                with open(materials_file, 'r') as f:
                    all_materials = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                all_materials = []

            # Add new chapter
            all_materials.append(new_chapter)

            # Save back
            with open(materials_file, 'w') as f:
                json.dump(all_materials, f, indent=2)

            return jsonify({"success": True, "chapter_id": chapter_id})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

@admin_bp.route('/modules/<module_id>/chapters/<chapter_id>/materials', methods=['POST'])
def admin_upload_material(module_id, chapter_id):
    """Upload material for a specific chapter - supports PDF files, MP4 videos, and PDF use cases"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Get form data
        material_type = request.form.get('material_type')  # 'pdf_reading', 'mp4_video', 'pdf_usecase'
        learning_style = request.form.get('learning_style')  # 'visual', 'auditory', 'reading_writing'
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')

        if not material_type or not learning_style:
            return jsonify({"error": "material_type and learning_style are required"}), 400

        # Validate file types based on material type
        allowed_extensions = {
            'pdf_reading': ['.pdf'],
            'mp4_video': ['.mp4', '.avi', '.mov', '.wmv'],
            'pdf_usecase': ['.pdf']
        }

        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if f'.{file_extension}' not in allowed_extensions.get(material_type, []):
            return jsonify({
                "error": f"Invalid file type for {material_type}. Allowed: {', '.join(allowed_extensions[material_type])}"
            }), 400

        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(get_data_file_path('')), 'uploads', 'materials')
        os.makedirs(uploads_dir, exist_ok=True)

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(uploads_dir, f"{uuid.uuid4().hex}_{filename}")
        file.save(file_path)

        # Create relative URL for frontend access
        relative_url = f"/uploads/materials/{os.path.basename(file_path)}"

        # Map material type to learning style structure
        material_entry = None
        if material_type == 'pdf_reading':
            material_entry = {
                'type': 'pdf',
                'title': title,
                'url': relative_url,
                'description': description,
                'pages': request.form.get('pages', 0),
                'material_type': 'reading_material'
            }
        elif material_type == 'mp4_video':
            material_entry = {
                'type': 'video',
                'title': title,
                'url': relative_url,
                'description': description,
                'duration': request.form.get('duration', '0 minutes'),
                'material_type': 'video_content'
            }
        elif material_type == 'pdf_usecase':
            material_entry = {
                'type': 'pdf',
                'title': title,
                'url': relative_url,
                'description': description,
                'pages': request.form.get('pages', 0),
                'material_type': 'use_case_study'
            }

        if not material_entry:
            return jsonify({"error": "Invalid material type"}), 400

        # Load existing materials
        materials_file = get_data_file_path('learning_materials.json')
        import json
        try:
            with open(materials_file, 'r') as f:
                all_materials = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_materials = []

        # Find or create chapter entry
        chapter_entry = None
        for material in all_materials:
            if (material.get('module_id') == module_id and
                material.get('chapter_id') == chapter_id):
                chapter_entry = material
                break

        if not chapter_entry:
            chapter_entry = {
                'id': f"MAT_{uuid.uuid4().hex[:8]}",
                'module_id': module_id,
                'chapter_id': chapter_id,
                'title': f'Chapter {chapter_id}',
                'materials': {
                    'visual': [],
                    'auditory': [],
                    'reading_writing': []
                }
            }
            all_materials.append(chapter_entry)

        # Add material to appropriate learning style
        if learning_style not in chapter_entry['materials']:
            chapter_entry['materials'][learning_style] = []

        chapter_entry['materials'][learning_style].append(material_entry)

        # Save back
        with open(materials_file, 'w') as f:
            json.dump(all_materials, f, indent=2)

        return jsonify({
            "success": True,
            "material_id": len(chapter_entry['materials'][learning_style]) - 1,
            "url": relative_url,
            "material_type": material_type,
            "learning_style": learning_style
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/modules/<module_id>/chapters/<chapter_id>/quizzes', methods=['POST'])
def admin_create_quiz(module_id, chapter_id):
    """Create a quiz for a specific chapter with difficulty level. Supports both JSON data and TXT file upload."""
    try:
        print(f"Request content type: {request.content_type}")
        print(f"Request method: {request.method}")
        print(f"Request files: {list(request.files.keys()) if request.files else 'No files'}")
        print(f"Request form: {dict(request.form) if request.form else 'No form data'}")

        # Check if this is a file upload (multipart form data) or JSON request
        if request.files or (request.content_type and 'multipart/form-data' in request.content_type):
            print("Handling as multipart form data")
            # Handle file upload
            difficulty = request.form.get('difficulty', 'intermediate')
            title = request.form.get('title', f'Intermediate Quiz - Chapter {chapter_id}')
            questions = []

            # Check if a TXT file was uploaded for quiz generation
            if 'quiz_file' in request.files:
                quiz_file = request.files['quiz_file']
                if quiz_file.filename == '':
                    return jsonify({"error": "No quiz file selected"}), 400

                # Validate file type
                if not quiz_file.filename.lower().endswith('.txt'):
                    return jsonify({"error": "Only TXT files are supported for quiz generation"}), 400

                # Read and parse the TXT file
                file_content = quiz_file.read().decode('utf-8')
                questions = parse_quiz_from_txt(file_content)

                if not questions:
                    return jsonify({"error": "No valid questions found in the TXT file"}), 400

                # Update title if not provided
                if not title or title == f'Intermediate Quiz - Chapter {chapter_id}':
                    title = f'{difficulty.title()} Quiz from File - Chapter {chapter_id}'
        elif request.is_json:
            print("Handling as JSON request with file content")
            # Handle JSON request with file content
            data = request.get_json(force=True) or {}
            difficulty = data.get('difficulty', 'intermediate')
            title = data.get('title', f'{difficulty.title()} Quiz - Chapter {chapter_id}')

            # Check if file content is provided
            file_content = data.get('file_content')
            if file_content:
                questions = parse_quiz_from_txt(file_content)
                if not questions:
                    return jsonify({"error": "No valid questions found in the file content"}), 400
                # Update title if not provided
                if not title or title == f'{difficulty.title()} Quiz - Chapter {chapter_id}':
                    title = f'{difficulty.title()} Quiz from File - Chapter {chapter_id}'
            else:
                # Manual quiz creation
                questions = data.get('questions', [])
        else:
            return jsonify({"error": "Invalid request format"}), 400

        print(f"Final data - difficulty: {difficulty}, title: {title}, questions: {len(questions)}")

        # Load quizzes data
        quizzes_file = get_data_file_path('quizzes.json')
        import json
        try:
            with open(quizzes_file, 'r') as f:
                all_quizzes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_quizzes = []

        # Create new quiz
        quiz_id = f"QUIZ_{module_id}_{chapter_id}_{difficulty}_{uuid.uuid4().hex[:8]}"
        new_quiz = {
            'id': quiz_id,
            'module_id': module_id,
            'chapter_id': chapter_id,
            'difficulty': difficulty,
            'title': title,
            'description': f'Quiz for {difficulty} level understanding of chapter {chapter_id}',
            'questions': questions,
            'passing_score': 70 if difficulty == 'beginner' else 75 if difficulty == 'intermediate' else 80,
            'time_limit_minutes': 10 if difficulty == 'beginner' else 15 if difficulty == 'intermediate' else 20,
            'created_by': 'admin',
            'created_at': datetime.now().isoformat() + 'Z'
        }

        all_quizzes.append(new_quiz)

        # Save back
        with open(quizzes_file, 'w') as f:
            json.dump(all_quizzes, f, indent=2)

        return jsonify({"success": True, "quiz_id": quiz_id, "questions_count": len(questions)})

    except Exception as e:
        print(f"Error in admin_create_quiz: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def parse_quiz_from_txt(file_content):
    """Parse quiz questions from TXT file content.
    Expected format:
    Question: What is the capital of France?
    A) London
    B) Paris
    C) Berlin
    D) Madrid
    Answer: B

    Question: What is 2 + 2?
    A) 3
    B) 4
    C) 5
    D) 6
    Answer: B
    """
    questions = []
    lines = file_content.strip().split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Look for question start
        if line.startswith('Question:') or line.startswith('Q:'):
            question_text = line.replace('Question:', '').replace('Q:', '').strip()

            # Collect options
            options = []
            i += 1
            while i < len(lines) and (lines[i].strip().startswith(('A)', 'B)', 'C)', 'D)', 'a)', 'b)', 'c)', 'd)'))):
                option_text = lines[i].strip()[2:].strip()  # Remove A) etc.
                options.append(option_text)
                i += 1

            # Look for answer
            correct_answer = None
            if i < len(lines) and (lines[i].strip().startswith('Answer:') or lines[i].strip().startswith('Correct:')):
                answer_line = lines[i].strip()
                if 'Answer:' in answer_line:
                    answer_text = answer_line.replace('Answer:', '').strip().upper()
                elif 'Correct:' in answer_line:
                    answer_text = answer_line.replace('Correct:', '').strip().upper()

                # Convert letter to index
                if answer_text in ['A', 'B', 'C', 'D']:
                    correct_answer = ord(answer_text) - ord('A')
                i += 1

            # Skip empty lines
            while i < len(lines) and lines[i].strip() == '':
                i += 1

            # Create question if we have valid data
            if question_text and len(options) >= 2 and correct_answer is not None and correct_answer < len(options):
                question = {
                    'id': f'Q_{uuid.uuid4().hex[:8]}',
                    'question': question_text,
                    'type': 'multiple_choice',
                    'options': options,
                    'correct_answer': correct_answer,
                    'explanation': f'Correct answer is option {chr(ord("A") + correct_answer)}'
                }
                questions.append(question)

        else:
            i += 1

    return questions

# --- Admin: Content Library Statistics ---
@admin_bp.route('/content/stats', methods=['GET'])
def admin_content_stats():
    """Get content library statistics based on uploaded materials"""
    try:
        # Load learning materials
        materials_file = get_data_file_path('learning_materials.json')
        import json
        try:
            with open(materials_file, 'r') as f:
                all_materials = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_materials = []

        # Initialize counters
        stats = {
            'video_count': 0,
            'assessment_count': 0,
            'resource_count': 0,
            'audio_count': 0,
            'text_count': 0,
            'slides_count': 0,
            'pdf_count': 0,
            'total_materials': 0
        }

        # Count materials by type and learning style
        for material in all_materials:
            if 'materials' in material:
                materials_dict = material['materials']
                for style, style_materials in materials_dict.items():
                    for item in style_materials:
                        stats['total_materials'] += 1
                        material_type = item.get('type', '')

                        if material_type == 'video':
                            stats['video_count'] += 1
                        elif material_type == 'pdf':
                            stats['pdf_count'] += 1
                            # PDFs can be resources or text materials
                            if 'usecase' in item.get('title', '').lower() or 'case' in item.get('title', '').lower():
                                stats['resource_count'] += 1
                            else:
                                stats['text_count'] += 1
                        elif material_type == 'audio':
                            stats['audio_count'] += 1
                        elif material_type == 'slides':
                            stats['slides_count'] += 1

        # Load quizzes for assessment count
        quizzes_file = get_data_file_path('quizzes.json')
        try:
            with open(quizzes_file, 'r') as f:
                all_quizzes = json.load(f)
            stats['assessment_count'] = len(all_quizzes)
        except (FileNotFoundError, json.JSONDecodeError):
            stats['assessment_count'] = 0

        return jsonify(stats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Admin: Departments ---
