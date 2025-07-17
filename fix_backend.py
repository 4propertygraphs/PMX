#!/usr/bin/env python3
"""
Diagnostika a oprava backend problémů
"""
import subprocess
import sys
import os

def check_dependencies():
    """Zkontroluj a nainstaluj závislosti"""
    print("🔍 Kontroluji závislosti...")
    
    required = [
        'fastapi==0.104.1',
        'uvicorn==0.24.0.post1', 
        'requests==2.31.0',
        'pandas==2.1.3',
        'python-dateutil==2.8.2'
    ]
    
    for dep in required:
        try:
            print(f"📦 Instaluji {dep}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True, text=True, check=True)
            print(f"✅ {dep} - OK")
        except subprocess.CalledProcessError as e:
            print(f"❌ Chyba při instalaci {dep}: {e.stderr}")
            return False
    return True

def test_imports():
    """Test importů"""
    print("🧪 Testuji importy...")
    try:
        import fastapi
        import uvicorn
        import requests
        import pandas
        from datetime import datetime
        print("✅ Všechny importy fungují")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_ports():
    """Zkontroluj dostupnost portů"""
    print("🔌 Kontroluji porty...")
    import socket
    
    def is_port_free(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    if not is_port_free(8000):
        print("⚠️ Port 8000 je obsazený - ukončuji procesy...")
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
            else:  # Linux/Mac
                subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
        except:
            pass
    
    if is_port_free(8000):
        print("✅ Port 8000 je volný")
        return True
    else:
        print("❌ Port 8000 stále obsazený")
        return False

def main():
    print("🔧 Diagnostika backend problémů...")
    print("=" * 50)
    
    if not check_dependencies():
        print("❌ Problém se závislostmi")
        return False
        
    if not test_imports():
        print("❌ Problém s importy")
        return False
        
    if not check_ports():
        print("❌ Problém s porty")
        return False
    
    print("✅ Všechny kontroly prošly!")
    print("\n📋 Zkus nyní:")
    print("python working_backend.py")
    return True

if __name__ == "__main__":
    main()