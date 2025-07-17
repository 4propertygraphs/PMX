#!/usr/bin/env python3
"""
Kompletní setup script pro Property Market Dashboard
"""
import subprocess
import sys
import os
import mysql.connector
from mysql.connector import Error
import hashlib

def install_python_dependencies():
    """Instalace Python závislostí"""
    print("📦 Instaluji Python závislosti...")
    
    dependencies = [
        'fastapi==0.104.1',
        'uvicorn==0.24.0.post1',
        'requests==2.31.0',
        'pandas==2.1.3',
        'python-dateutil==2.8.2',
        'mysql-connector-python',
        'pymysql',
        'sqlalchemy==2.0.23',
        'elasticsearch==6.8.2',
        'geopy==2.4.0',
        'numpy==1.26.1',
        'openpyxl',
        'autopep8'
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ Nainstalováno: {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Chyba při instalaci {dep}: {e}")
            return False
    return True

def setup_mysql_database():
    """Nastavení MySQL databáze"""
    print("🗄️ Nastavuji MySQL databázi...")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Změň pokud máš heslo
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Vytvoření databází
            databases = ['pmx_report', 'pmx_api_auth']
            
            for db_name in databases:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                print(f"✅ Databáze '{db_name}' vytvořena")
            
            # Nastavení autentifikace
            cursor.execute("USE pmx_api_auth")
            
            # Tabulka uživatelů
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                domain TEXT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table)
            
            # Tabulka tokenů
            create_tokens_table = """
            CREATE TABLE IF NOT EXISTS tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                token VARCHAR(64),
                user_id INT,
                salt VARCHAR(16),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
            cursor.execute(create_tokens_table)
            
            # Test uživatel a token
            test_api_key = "test_api_key_123"
            hash_object = hashlib.sha256()
            hash_object.update(test_api_key.encode())
            hashed_key = hash_object.hexdigest()
            
            cursor.execute("INSERT IGNORE INTO users (id, domain) VALUES (1, 'localhost')")
            cursor.execute("""
                INSERT INTO tokens (token, user_id, salt) 
                VALUES (%s, 1, 'test_salt')
                ON DUPLICATE KEY UPDATE token = VALUES(token)
            """, (hashed_key,))
            
            connection.commit()
            print("✅ MySQL databáze nastavena")
            print(f"🔑 Test API klíč: {test_api_key}")
            
    except Error as e:
        print(f"❌ Chyba MySQL: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def install_node_dependencies():
    """Instalace Node.js závislostí"""
    print("📦 Instaluji Node.js závislosti...")
    
    try:
        subprocess.check_call(['npm', 'install'])
        print("✅ Node.js závislosti nainstalovány")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Chyba při instalaci npm: {e}")
        return False

def main():
    print("🚀 Spouštím kompletní setup Property Market Dashboard...")
    print("=" * 60)
    
    # 1. Python závislosti
    if not install_python_dependencies():
        print("❌ Selhala instalace Python závislostí")
        return False
    
    # 2. MySQL setup
    if not setup_mysql_database():
        print("❌ Selhalo nastavení MySQL")
        return False
    
    # 3. Node.js závislosti
    if not install_node_dependencies():
        print("❌ Selhala instalace Node.js závislostí")
        return False
    
    print("\n" + "=" * 60)
    print("✅ SETUP DOKONČEN!")
    print("\n📋 DALŠÍ KROKY:")
    print("1. Import dat: python import_data.py")
    print("2. Spuštění API: python start_api.py")
    print("3. Spuštění frontendu: npm run dev")
    print("\n🔗 PŘÍSTUPY:")
    print("- Frontend: http://localhost:5173")
    print("- API: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    print("\n🔑 PŘIHLAŠOVACÍ ÚDAJE:")
    print("- API Key: test_api_key_123")
    print("- Domain: localhost")

if __name__ == "__main__":
    main()