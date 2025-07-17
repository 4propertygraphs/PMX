#!/usr/bin/env python3
"""
Spuštění jednoduchého API serveru s přímým napojením na ippi.io
"""
import sys
import subprocess

def main():
    print("🚀 Spouštím jednoduché API s přímým napojením na ippi.io...")
    print("🌐 Server běží na: http://localhost:8000")
    print("📖 API dokumentace: http://localhost:8000/docs")
    print("\n⚠️  POZOR: Používá přímo ippi.io API - může být pomalejší")
    print("⏹️  Pro zastavení stiskni Ctrl+C")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "simple_backend.py"])
    except KeyboardInterrupt:
        print("\n👋 API server zastaven")
    except Exception as e:
        print(f"❌ Chyba: {e}")

if __name__ == "__main__":
    main()