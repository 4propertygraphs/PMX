#!/usr/bin/env python3
"""
Spuštění celé aplikace najednou
"""
import subprocess
import sys
import time
import threading
import os

def run_api():
    """Spuštění API serveru"""
    print("🚀 Spouštím API server...")
    try:
        subprocess.run([sys.executable, "start_simple_api.py"])
    except KeyboardInterrupt:
        pass

def run_frontend():
    """Spuštění frontendu"""
    print("🎨 Spouštím frontend...")
    time.sleep(3)  # Počkej na API
    try:
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        pass

def main():
    print("🚀 Spouštím kompletní Property Market Dashboard...")
    print("=" * 60)
    print("API: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("⏹️  Pro zastavení stiskni Ctrl+C")
    
    # Spuštění v paralelních vláknech
    api_thread = threading.Thread(target=run_api)
    frontend_thread = threading.Thread(target=run_frontend)
    
    try:
        api_thread.start()
        frontend_thread.start()
        
        # Čekání na dokončení
        api_thread.join()
        frontend_thread.join()
        
    except KeyboardInterrupt:
        print("\n👋 Aplikace zastavena")

if __name__ == "__main__":
    main()