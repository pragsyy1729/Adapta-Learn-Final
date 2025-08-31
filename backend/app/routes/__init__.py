def register_routes(app):
    from .admin import admin_bp
    from .user import user_bp
    from .roles import roles_bp
    from .dashboard import dashboard_bp
    from .learning_path import learning_path_bp
    from .recommendation import recommendation_bp
    from .assessment import assessment_bp
    from .profile import profile_bp
    from .events import events_bp
    from .groups import groups_bp
    from .user_auth import user_auth_bp
    from .onboarding import onboarding_bp
    from .enrollment import enrollment_bp
    from .conversation import conversation_bp
    from .learning_warnings import learning_warnings_bp
    from .quiz import quiz_bp
    from .gamification import gamification_bp
    from .comprehensive_recommendations import recommendations_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(roles_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(learning_path_bp, url_prefix='/api')
    app.register_blueprint(recommendation_bp, url_prefix='/api')
    app.register_blueprint(assessment_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(events_bp, url_prefix='/api')
    app.register_blueprint(groups_bp, url_prefix='/api/groups')
    app.register_blueprint(user_auth_bp, url_prefix='/api')
    app.register_blueprint(onboarding_bp, url_prefix='/api/onboarding')
    app.register_blueprint(enrollment_bp, url_prefix='/api')
    app.register_blueprint(conversation_bp, url_prefix='/api/conversation')
    app.register_blueprint(learning_warnings_bp, url_prefix='/api')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
