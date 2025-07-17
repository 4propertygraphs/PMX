#!/usr/bin/env python3
"""
Start the FastAPI backend server
"""
import subprocess
import sys
import os

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting PMX API Backend...")
    
    # Change to PMX-api directory
    api_dir = "Elasticsearch-to-MySQL-master/Elasticsearch-to-MySQL-master/PMX-api"
    
    if not os.path.exists(api_dir):
        print(f"❌ Directory {api_dir} not found!")
        return False
    
    original_dir = os.getcwd()
    
    try:
        os.chdir(api_dir)
        
        # Install dependencies
        print("📦 Installing API dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "../requirements.txt"], check=True)
        
        # Additional dependencies for the API
        additional_deps = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0.post1",
            "sqlalchemy==2.0.23",
            "pymysql==1.1.0",
            "pandas==2.1.3",
            "python-decouple==3.8"
        ]
        
        for dep in additional_deps:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        
        print("✅ Dependencies installed!")
        print("🌐 Starting server on http://localhost:8000")
        print("📖 API docs will be available at http://localhost:8000/docs")
        print("\n🔑 Use these credentials in the frontend:")
        print("API Key: test_api_key_123")
        print("Domain: localhost")
        print("Base URL: http://localhost:8000")
        
        # Start the server
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    start_backend()