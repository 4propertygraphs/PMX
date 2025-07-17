#!/usr/bin/env python3
"""
Setup script for PMX database
"""
import mysql.connector
from mysql.connector import Error
import sys

def create_databases():
    """Create the required databases if they don't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Add password if needed
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create databases
            databases = ['pmx_report', 'pmx_api_auth']
            
            for db_name in databases:
                try:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                    print(f"✅ Database '{db_name}' created or already exists")
                except Error as e:
                    print(f"❌ Error creating database {db_name}: {e}")
            
            # Create users table for API authentication
            cursor.execute("USE pmx_api_auth")
            
            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                domain TEXT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table)
            
            # Create tokens table
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
            
            # Insert test user and token
            import hashlib
            test_domain = "localhost"
            test_api_key = "test_api_key_123"
            
            # Hash the API key
            hash_object = hashlib.sha256()
            hash_object.update(test_api_key.encode())
            hashed_key = hash_object.hexdigest()
            
            # Insert user
            cursor.execute("INSERT IGNORE INTO users (id, domain) VALUES (1, %s)", (test_domain,))
            
            # Insert token
            cursor.execute("""
                INSERT INTO tokens (token, user_id, salt) 
                VALUES (%s, 1, 'test_salt')
                ON DUPLICATE KEY UPDATE token = VALUES(token)
            """, (hashed_key,))
            
            connection.commit()
            print("✅ Authentication tables created")
            print(f"✅ Test API key created: {test_api_key}")
            print(f"✅ Test domain: {test_domain}")
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        print("Make sure MySQL is running and accessible")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Setting up PMX databases...")
    if create_databases():
        print("\n✅ Database setup completed!")
        print("\n📝 Next steps:")
        print("1. Run the data import: python elasticsearch_to_mysql/sales.py")
        print("2. Run the rent data import: python elasticsearch_to_mysql/rent.py")
        print("3. Start the API: uvicorn main:app --reload")
        print("\n🔑 API Credentials for testing:")
        print("API Key: test_api_key_123")
        print("Domain: localhost")
    else:
        print("❌ Database setup failed!")
        sys.exit(1)