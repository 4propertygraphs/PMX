#!/usr/bin/env python3
"""
Run data import from Elasticsearch to MySQL
"""
import sys
import os
import subprocess
import time

def run_import():
    """Run the data import process"""
    print("🚀 Starting data import from Elasticsearch...")
    
    # Change to the correct directory
    elasticsearch_dir = "Elasticsearch-to-MySQL-master/Elasticsearch-to-MySQL-master/ElasticsearchToMysql"
    
    if not os.path.exists(elasticsearch_dir):
        print(f"❌ Directory {elasticsearch_dir} not found!")
        return False
    
    original_dir = os.getcwd()
    
    try:
        os.chdir(elasticsearch_dir)
        
        # Install dependencies
        print("📦 Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Run sales data import
        print("📊 Importing sales data...")
        result = subprocess.run([sys.executable, "elasticsearch_to_mysql/sales.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sales data imported successfully!")
        else:
            print(f"❌ Sales import failed: {result.stderr}")
            return False
        
        # Run rent data import
        print("🏠 Importing rent data...")
        result = subprocess.run([sys.executable, "elasticsearch_to_mysql/rent.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Rent data imported successfully!")
        else:
            print(f"❌ Rent import failed: {result.stderr}")
            return False
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during import: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    if run_import():
        print("\n✅ Data import completed successfully!")
        print("\n📝 Next step:")
        print("Start the API server: uvicorn main:app --reload")
    else:
        print("\n❌ Data import failed!")
        sys.exit(1)