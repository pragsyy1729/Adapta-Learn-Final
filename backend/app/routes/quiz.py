from flask import Blueprint, jsonify, request
import json
import uuid
from datetime import datetime
from ..services.data_access import get_data_file_path, _read_json, _write_json

quiz_bp = Blueprint('quiz', __name__)

def load_quizzes():
    """Load quiz data"""
    path = get_data_file_path('quizzes.json')
    return _read_json(path, [])

def save_quizzes(data):
    """Save quiz data"""
    path = get_data_file_path('quizzes.json')
    _write_json(path, data)

@quiz_bp.route('/quizzes', methods=['GET'])
def get_quizzes():
    """Get all quizzes with optional filtering"""
    try:
        chapter_id = request.args.get('chapter_id')
        difficulty = request.args.get('difficulty')

        quizzes = load_quizzes()
        filtered_quizzes = []

        for quiz in quizzes:
            if chapter_id and quiz.get('chapter_id') != chapter_id:
                continue
            if difficulty and quiz.get('difficulty') != difficulty:
                continue
            filtered_quizzes.append(quiz)

        return jsonify(filtered_quizzes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/quizzes/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """Get a specific quiz"""
    try:
        quizzes = load_quizzes()
        for quiz in quizzes:
            if quiz.get('id') == quiz_id:
                return jsonify(quiz)

        return jsonify({"error": "Quiz not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/quizzes', methods=['POST'])
def create_quiz():
    """Create a new quiz (Admin only)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['chapter_id', 'difficulty', 'title', 'questions']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Generate quiz ID
        quiz_id = f"QUIZ{str(uuid.uuid4())[:8].upper()}"

        quiz = {
            "id": quiz_id,
            "chapter_id": data['chapter_id'],
            "difficulty": data['difficulty'],
            "title": data['title'],
            "description": data.get('description', ''),
            "questions": data['questions'],
            "passing_score": data.get('passing_score', 70),
            "time_limit_minutes": data.get('time_limit_minutes', 15),
            "created_by": data.get('created_by', 'admin'),
            "created_at": datetime.now().isoformat() + 'Z'
        }

        quizzes = load_quizzes()
        quizzes.append(quiz)
        save_quizzes(quizzes)

        return jsonify(quiz), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/quizzes/<quiz_id>', methods=['PUT'])
def update_quiz(quiz_id):
    """Update a quiz (Admin only)"""
    try:
        data = request.get_json()
        quizzes = load_quizzes()

        for i, quiz in enumerate(quizzes):
            if quiz.get('id') == quiz_id:
                # Update allowed fields
                updatable_fields = ['title', 'description', 'questions', 'passing_score', 'time_limit_minutes']
                for field in updatable_fields:
                    if field in data:
                        quiz[field] = data[field]

                quiz['updated_at'] = datetime.now().isoformat() + 'Z'
                save_quizzes(quizzes)
                return jsonify(quiz)

        return jsonify({"error": "Quiz not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/quizzes/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    """Delete a quiz (Admin only)"""
    try:
        quizzes = load_quizzes()
        for i, quiz in enumerate(quizzes):
            if quiz.get('id') == quiz_id:
                deleted_quiz = quizzes.pop(i)
                save_quizzes(quizzes)
                return jsonify({"message": "Quiz deleted successfully", "quiz": deleted_quiz})

        return jsonify({"error": "Quiz not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/chapters/<chapter_id>/quiz', methods=['GET'])
def get_chapter_quiz(chapter_id):
    """Get appropriate quiz for a chapter based on user proficiency"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Get user's learning progress to determine proficiency
        progress_path = get_data_file_path('LearningPathProgress.json')
        progress_data = _read_json(progress_path, [])

        # Get user's learning style and VARK scores for additional personalization
        users_path = get_data_file_path('users.json')
        users_data = _read_json(users_path, {})

        user_profile = None
        for email, user in users_data.items():
            if user.get('user_id') == user_id:
                user_profile = user
                break

        # Determine user proficiency level
        user_proficiency = "beginner"  # default

        # Calculate proficiency based on learning path progress
        total_progress = 0
        path_count = 0

        for progress in progress_data:
            if progress.get('attributes', {}).get('user_id') == user_id:
                progress_percent = progress.get('attributes', {}).get('progress_percent', 0)
                total_progress += progress_percent
                path_count += 1

        if path_count > 0:
            avg_progress = total_progress / path_count
            if avg_progress > 80:
                user_proficiency = "advanced"
            elif avg_progress > 60:
                user_proficiency = "intermediate"
            elif avg_progress > 30:
                user_proficiency = "beginner"
            else:
                user_proficiency = "novice"

        # Factor in learning style preferences for quiz difficulty adjustment
        learning_style_adjustment = 0
        if user_profile and 'vark_scores' in user_profile.get('profile', {}):
            vark_scores = user_profile['profile']['vark_scores']
            # If user is more visual/auditory, they might perform better on certain quiz types
            visual_score = vark_scores.get('Visual', 0)
            auditory_score = vark_scores.get('Auditory', 0)
            if visual_score > 6 or auditory_score > 6:
                learning_style_adjustment = 1  # Boost difficulty slightly

        # Map proficiency to difficulty with learning style adjustment
        proficiency_map = {
            "novice": 0,
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3
        }

        base_level = proficiency_map.get(user_proficiency, 1)
        adjusted_level = min(3, base_level + learning_style_adjustment)

        difficulty_map = {
            0: "easy",
            1: "easy",
            2: "medium",
            3: "hard"
        }

        target_difficulty = difficulty_map.get(adjusted_level, "easy")

        # Find appropriate quiz
        quizzes = load_quizzes()
        for quiz in quizzes:
            if (quiz.get('chapter_id') == chapter_id and
                quiz.get('difficulty') == target_difficulty):
                return jsonify(quiz)

        # Fallback to easy quiz if target difficulty not found
        for quiz in quizzes:
            if (quiz.get('chapter_id') == chapter_id and
                quiz.get('difficulty') == "easy"):
                return jsonify(quiz)

        return jsonify({"error": "No quiz found for this chapter"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/admin/upload-quiz', methods=['POST'])
def admin_upload_quiz():
    """Admin endpoint to upload quiz for specific chapter and difficulty"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['chapter_id', 'difficulty', 'title', 'questions', 'admin_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate difficulty level
        valid_difficulties = ['easy', 'medium', 'hard']
        if data['difficulty'] not in valid_difficulties:
            return jsonify({"error": f"Invalid difficulty. Must be one of: {valid_difficulties}"}), 400

        # Check if quiz already exists for this chapter and difficulty
        quizzes = load_quizzes()
        for quiz in quizzes:
            if (quiz.get('chapter_id') == data['chapter_id'] and
                quiz.get('difficulty') == data['difficulty']):
                return jsonify({"error": "Quiz already exists for this chapter and difficulty level"}), 400

        # Generate quiz ID
        quiz_id = f"QUIZ{data['chapter_id']}_{data['difficulty'].upper()[:3]}{str(uuid.uuid4())[:4].upper()}"

        quiz = {
            "id": quiz_id,
            "chapter_id": data['chapter_id'],
            "difficulty": data['difficulty'],
            "title": data['title'],
            "description": data.get('description', ''),
            "questions": data['questions'],
            "passing_score": data.get('passing_score', 70),
            "time_limit_minutes": data.get('time_limit_minutes', 15),
            "created_by": data['admin_id'],
            "created_at": datetime.now().isoformat() + 'Z',
            "is_active": True
        }

        quizzes.append(quiz)
        save_quizzes(quizzes)

        return jsonify({
            "success": True,
            "message": "Quiz uploaded successfully",
            "quiz_id": quiz_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/admin/chapter-quizzes/<chapter_id>', methods=['GET'])
def get_chapter_quizzes_admin(chapter_id):
    """Admin endpoint to get all quizzes for a chapter"""
    try:
        quizzes = load_quizzes()
        chapter_quizzes = []

        for quiz in quizzes:
            if quiz.get('chapter_id') == chapter_id:
                chapter_quizzes.append({
                    "id": quiz.get('id'),
                    "difficulty": quiz.get('difficulty'),
                    "title": quiz.get('title'),
                    "question_count": len(quiz.get('questions', [])),
                    "passing_score": quiz.get('passing_score'),
                    "is_active": quiz.get('is_active', True),
                    "created_at": quiz.get('created_at')
                })

        return jsonify({
            "chapter_id": chapter_id,
            "quizzes": chapter_quizzes
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@quiz_bp.route('/quizzes/<quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    """Submit quiz answers and calculate score"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        answers = data.get('answers', {})

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Get quiz
        quizzes = load_quizzes()
        quiz = None
        for q in quizzes:
            if q.get('id') == quiz_id:
                quiz = q
                break

        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404

        # Calculate score
        questions = quiz.get('questions', [])
        correct_answers = 0
        total_questions = len(questions)
        detailed_results = []

        for question in questions:
            q_id = question.get('id')
            user_answer = answers.get(q_id)
            correct_answer = question.get('correct_answer')

            is_correct = user_answer == correct_answer
            if is_correct:
                correct_answers += 1

            detailed_results.append({
                "question_id": q_id,
                "question": question.get('question'),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get('explanation', '')
            })

        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passing_score = quiz.get('passing_score', 70)
        passed = score_percentage >= passing_score

        result = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "score": correct_answers,
            "total_questions": total_questions,
            "score_percentage": round(score_percentage, 2),
            "passing_score": passing_score,
            "passed": passed,
            "submitted_at": datetime.now().isoformat() + 'Z',
            "detailed_results": detailed_results
        }

        # Trigger gamification for quiz completion
        try:
            from ..routes.gamification import award_points

            gamification_result = award_points(user_id, {
                'activity_type': 'quiz_completion',
                'details': {
                    'quiz_id': quiz_id,
                    'score_percentage': round(score_percentage, 2),
                    'time_taken': data.get('time_taken_minutes', 0)
                }
            })
            result['gamification'] = gamification_result
            print(f"Quiz gamification result: {gamification_result}")  # Debug log
        except Exception as e:
            print(f"Gamification error for quiz: {e}")

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
