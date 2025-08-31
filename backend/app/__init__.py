
from flask import Flask
from flask_cors import CORS
from .routes import register_routes
import atexit

def create_app():
    app = Flask(__name__)
    # Allow requests from React dev server and all methods/headers for dev
    CORS(app, origins=["http://localhost:8080"], supports_credentials=True, allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Register routes
    register_routes(app)

    # Initialize job queue service
    from .services.job_queue import job_queue
    print("📋 Job queue service initialized and worker started")

    # Register cleanup function
    def cleanup_job_queue():
        print("🛑 Shutting down job queue service...")
        job_queue.stop_worker()

    atexit.register(cleanup_job_queue)

    return app
