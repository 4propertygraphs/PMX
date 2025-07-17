#!/usr/bin/env python3
"""
Import dat z Elasticsearch do MySQL
"""
import sys
import os
import subprocess
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def run_elasticsearch_import():
    """Spuštění importu z Elasticsearch"""
    print("📊 Importuji data z Elasticsearch...")
    
    elasticsearch_dir = "Elasticsearch-to-MySQL-master/Elasticsearch-to-MySQL-master/ElasticsearchToMysql"
    
    if not os.path.exists(elasticsearch_dir):
        print(f"❌ Adresář {elasticsearch_dir} nenalezen!")
        return False
    
    original_dir = os.getcwd()
    
    try:
        os.chdir(elasticsearch_dir)
        
        # Instalace závislostí
        print("📦 Instaluji závislosti...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Import prodejních dat
        print("🏠 Importuji data o prodeji nemovitostí...")
        result = subprocess.run([sys.executable, "elasticsearch_to_mysql/sales.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Data o prodeji úspěšně importována!")
        else:
            print(f"⚠️ Varování při importu prodejů: {result.stderr}")
        
        # Import nájemních dat
        print("🏘️ Importuji data o nájmech...")
        result = subprocess.run([sys.executable, "elasticsearch_to_mysql/rent.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Data o nájmech úspěšně importována!")
        else:
            print(f"⚠️ Varování při importu nájmů: {result.stderr}")
            
        return True
        
    except subprocess.TimeoutExpired:
        print("⏰ Import trval příliš dlouho - pokračuji s dostupnými daty")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Chyba při importu: {e}")
        return False
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    print("📥 Spouštím import dat...")
    print("⚠️  POZOR: Import může trvat několik minut")
    print("=" * 50)
    
    if run_elasticsearch_import():
        print("\n✅ IMPORT DOKONČEN!")
        print("\n📋 DALŠÍ KROK:")
        print("Spusť API server: python start_api.py")
    else:
        print("\n❌ Import selhal!")
        print("Zkus spustit API s demo daty: python start_simple_api.py")

if __name__ == "__main__":
    main()