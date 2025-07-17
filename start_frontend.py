#!/usr/bin/env python3
"""
Spuštění React frontendu
"""
import subprocess
import sys

def main():
    print("🎨 Spouštím React frontend...")
    print("🌐 Frontend běží na: http://localhost:5173")
    print("⏹️  Pro zastavení stiskni Ctrl+C")
    print("=" * 50)
    
    try:
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print("\n👋 Frontend zastaven")
    except Exception as e:
        print(f"❌ Chyba: {e}")

if __name__ == "__main__":
    main()