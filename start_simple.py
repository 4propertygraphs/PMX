#!/usr/bin/env python3
"""
Start the simple backend that connects directly to ippi.io
"""
import sys
import os

def install_dependencies():
def start_server():
    """Start the FastAPI server"""
    os.system(f"{sys.executable} simple_backend.py")
        print("Base URL: http://localhost:8000")
        print("\n⏳ Starting server...")
        
        subprocess.run([sys.executable, 'simple_backend.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
        start_server()
    else:
        print("❌ Failed to start server due to dependency issues")
        sys.exit(1)