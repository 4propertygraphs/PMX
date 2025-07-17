#!/usr/bin/env python3
"""
Spuštění FastAPI serveru s MySQL daty
"""
import sys
import os
import subprocess

def start_mysql_api():
    """Spuštění API s MySQL backend"""
    print("🚀 Spouštím PMX API s MySQL...")
    
    api_dir = "Elasticsearch-to-MySQL-master/Elasticsearch-to-MySQL-master/PMX-api"
    
    if not os.path.exists(api_dir):
        print(f"❌ Adresář {api_dir} nenalezen!")
        return False
    
    original_dir = os.getcwd()
    
    try:
        os.chdir(api_dir)
        
        print("🌐 Server běží na: http://localhost:8000")
        print("📖 API dokumentace: http://localhost:8000/docs")
        print("\n🔑 PŘIHLAŠOVACÍ ÚDAJE:")
        print("API Key: test_api_key_123")
        print("Domain: localhost")
        print("\n⏹️  Pro zastavení stiskni Ctrl+C")
        print("=" * 50)
        
        # Spuštění serveru
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 API server zastaven")
        return True
    except Exception as e:
        print(f"❌ Chyba při spuštění API: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    start_mysql_api()

if __name__ == "__main__":
    main()