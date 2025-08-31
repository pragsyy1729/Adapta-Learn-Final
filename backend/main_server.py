#!/usr/bin/env python3
"""
Main server that runs all backend services together:
- Authentication Server (port 5003)
- Session Tracking Server (port 5001)
- Main Backend API (port 5000)
"""

import threading
import time
from multiprocessing import Process
import sys
import os

# Add the current directory to Python path so we can import our modules
# Ensure backend folder and repo root are on sys.path so top-level packages like
# `agent` (located at the repository root) can be imported when this script
# is executed from the project root or other working directories.
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(backend_dir, '..'))
# Prefer inserting at front so these local packages shadow any globally installed
# packages with the same names
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_auth_server():
    """Run the authentication server on port 5003"""
    try:
        print("🔐 Starting Authentication Server on port 5003...")
        import auth_server
        auth_server.app.run(host='0.0.0.0', port=5003, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting auth server: {e}")

def run_session_tracking_server():
    """Run the session tracking server on port 5001"""
    try:
        print("📊 Starting Session Tracking Server on port 5001...")
        import session_tracking
        session_tracking.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting session tracking server: {e}")

def run_main_backend_server():
    """Run the main backend server on port 5000"""
    try:
        print("🚀 Starting Main Backend Server on port 5000...")
        from app import create_app
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting main backend server: {e}")
        print("ℹ️  Main backend server is optional - continuing with other servers...")

def main():
    """Start all servers in separate processes"""
    print("🌟 Starting AdaptaLearn Backend Services...")
    print("=" * 60)
    
    # Create processes for each server
    processes = []
    
    # Start Authentication Server
    auth_process = Process(target=run_auth_server, daemon=True)
    auth_process.start()
    processes.append(auth_process)
    time.sleep(1)  # Give it a moment to start
    
    # Start Session Tracking Server
    session_process = Process(target=run_session_tracking_server, daemon=True)
    session_process.start()
    processes.append(session_process)
    time.sleep(1)  # Give it a moment to start
    
    # Start Main Backend Server (optional)
    try:
        main_process = Process(target=run_main_backend_server, daemon=True)
        main_process.start()
        processes.append(main_process)
        time.sleep(1)  # Give it a moment to start
    except:
        pass  # Main backend is optional
    
    print("=" * 60)
    print("✅ All servers started successfully!")
    print()
    print("🔗 Available Services:")
    print("   • Authentication API: http://localhost:5003")
    print("   • Session Tracking API: http://localhost:5001")
    print("   • Main Backend API: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop all servers")
    print("=" * 60)
    
    try:
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if any process has died and restart it
            for i, process in enumerate(processes):
                if not process.is_alive():
                    print(f"⚠️  Process {i} died, restarting...")
                    if i == 0:  # Auth server
                        process = Process(target=run_auth_server, daemon=True)
                    elif i == 1:  # Session tracking
                        process = Process(target=run_session_tracking_server, daemon=True)
                    elif i == 2:  # Main backend
                        process = Process(target=run_main_backend_server, daemon=True)
                    
                    process.start()
                    processes[i] = process
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all servers...")
        for process in processes:
            process.terminate()
            process.join()
        print("✅ All servers stopped successfully!")

if __name__ == "__main__":
    main()
