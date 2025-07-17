#!/usr/bin/env python3
"""
Start the simple backend that connects directly to ippi.io
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    try:
        print("🚀 Starting Property Market API...")
        print("📊 Direct connection to ippi.io Elasticsearch")
        print("🌐 Server will run on http://localhost:8000")
        print("📖 API docs will be at http://localhost:8000/docs")
        print("\n🔑 Frontend credentials:")
        print("API Key: (not needed)")
        print("Domain: (not needed)")
        print("Base URL: http://localhost:8000")
        print("\n⏳ Starting server...")
        
        subprocess.run([sys.executable, 'simple_backend.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    if install_dependencies():
        start_server()
    else:
        print("❌ Failed to start server due to dependency issues")
        sys.exit(1)