from flask import Flask
from flask_cors import CORS
import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.routes.user_auth import user_auth_bp

app = Flask(__name__)
CORS(app)

# Register only the user_auth blueprint for testing
app.register_blueprint(user_auth_bp, url_prefix='/api')

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Authentication server is running'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
