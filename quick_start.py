#!/usr/bin/env python3
"""
Rychlé spuštění - diagnostika a start
"""
import subprocess
import sys
import os
import time

def main():
    print("🚀 Rychlé spuštění Property Dashboard")
    print("=" * 50)
    
    # 1. Diagnostika
    print("🔧 Spouštím diagnostiku...")
    result = subprocess.run([sys.executable, "fix_backend.py"], capture_output=True, text=True)
    print(result.stdout)
    
    if "✅ Všechny kontroly prošly!" not in result.stdout:
        print("❌ Diagnostika selhala")
        return
    
    # 2. Spuštění backendu
    print("\n🚀 Spouštím backend...")
    try:
        subprocess.run([sys.executable, "working_backend.py"])
    except KeyboardInterrupt:
        print("\n👋 Aplikace zastavena")

if __name__ == "__main__":
    main()