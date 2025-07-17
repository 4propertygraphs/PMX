#!/usr/bin/env python3
"""
Start the simple backend that connects directly to ippi.io
"""
import sys
import os
import subprocess

def install_dependencies():
    """Install dependencies from requirements.txt"""
    try:
        print("📦 Installing dependencies...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    try:
        print("Base URL: http://localhost:8000")
        print("\n⏳ Starting server...")
        
        subprocess.run([sys.executable, 'simple_backend.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    if install_dependencies():
        start_server()
    else:
        print("❌ Failed to start server due to dependency issues")
        sys.exit(1)

if __name__ == "__main__":
    main()