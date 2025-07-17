#!/usr/bin/env python3
"""
Jednoduchý FastAPI backend optimalizovaný pro WebContainer
"""

# Základní importy bez subprocess
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import json
    from datetime import datetime
    import os
except ImportError as e:
    print(f"Chyba importu: {e}")
    print("Instaluji závislosti...")
    # Fallback bez subprocess
    os.system("python -m pip install fastapi uvicorn requests --quiet")
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import json
    from datetime import datetime

# Vytvoření FastAPI aplikace
app = FastAPI(
    title="Property Market API",
    description="API pro analýzu nemovitostního trhu",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Globální proměnné pro cache
cache = {}
cache_timeout = 300  # 5 minut

def get_from_api(url, params=None):
    """Bezpečné volání API s error handlingem"""
    try:
        import requests
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Property Market API je spuštěno",
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "all_data": "/api/pmx/all",
            "averages": "/api/pmx/average",
            "yoy_changes": "/api/pmx/yoy", 
            "rent_data": "/api/pmx/rent",
            "properties": "/api/eval/property"
        }
    }

@app.get("/api/pmx/all")
async def get_all_data(entity: str = "county", version: str = "avg"):
    """Získat všechna data"""
    try:
        # Cache klíč
        cache_key = f"all_{entity}_{version}"
        
        # Kontrola cache
        if cache_key in cache:
            cached_time, data = cache[cache_key]
            if (datetime.now() - cached_time).seconds < cache_timeout:
                return data
        
        # Volání API
        base_url = "https://ippi.io/api/pmx/all"
        params = {"entity": entity, "version": version}
        
        data = get_from_api(base_url, params)
        
        if data:
            # Uložení do cache
            cache[cache_key] = (datetime.now(), data)
            return data
        else:
            return {"error": "Nepodařilo se načíst data z API", "data": {}}
            
    except Exception as e:
        return {"error": f"Chyba při načítání dat: {str(e)}", "data": {}}

@app.get("/api/pmx/average")
async def get_average_prices(county: str, beds: str = None):
    """Získat průměrné ceny pro konkrétní kraj"""
    try:
        cache_key = f"avg_{county}_{beds}"
        
        if cache_key in cache:
            cached_time, data = cache[cache_key]
            if (datetime.now() - cached_time).seconds < cache_timeout:
                return data
        
        base_url = "https://ippi.io/api/pmx/average"
        params = {"county": county}
        if beds:
            params["beds"] = beds
            
        data = get_from_api(base_url, params)
        
        if data:
            cache[cache_key] = (datetime.now(), data)
            return data
        else:
            return []
            
    except Exception as e:
        return {"error": f"Chyba při načítání průměrných cen: {str(e)}"}

@app.get("/api/pmx/yoy")
async def get_yoy_changes(county: str, beds: str = None):
    """Získat year-over-year změny"""
    try:
        cache_key = f"yoy_{county}_{beds}"
        
        if cache_key in cache:
            cached_time, data = cache[cache_key]
            if (datetime.now() - cached_time).seconds < cache_timeout:
                return data
        
        base_url = "https://ippi.io/api/pmx/yoy"
        params = {"county": county}
        if beds:
            params["beds"] = beds
            
        data = get_from_api(base_url, params)
        
        if data:
            cache[cache_key] = (datetime.now(), data)
            return data
        else:
            return []
            
    except Exception as e:
        return {"error": f"Chyba při načítání YoY dat: {str(e)}"}

@app.get("/api/pmx/rent")
async def get_rent_data(version: str = "avg"):
    """Získat data o nájemním trhu"""
    try:
        cache_key = f"rent_{version}"
        
        if cache_key in cache:
            cached_time, data = cache[cache_key]
            if (datetime.now() - cached_time).seconds < cache_timeout:
                return data
        
        base_url = "https://ippi.io/api/pmx/rent"
        params = {"version": version}
        
        data = get_from_api(base_url, params)
        
        if data:
            cache[cache_key] = (datetime.now(), data)
            return data
        else:
            return []
            
    except Exception as e:
        return {"error": f"Chyba při načítání rent dat: {str(e)}"}

@app.get("/api/eval/property")
async def get_property_details(area: str = "All"):
    """Získat detaily jednotlivých nemovitostí"""
    try:
        cache_key = f"property_{area}"
        
        if cache_key in cache:
            cached_time, data = cache[cache_key]
            if (datetime.now() - cached_time).seconds < cache_timeout:
                return data
        
        base_url = "https://ippi.io/api/eval/property"
        params = {"area": area}
        
        data = get_from_api(base_url, params)
        
        if data:
            cache[cache_key] = (datetime.now(), data)
            return data
        else:
            return []
            
    except Exception as e:
        return {"error": f"Chyba při načítání property dat: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(cache)
    }

if __name__ == "__main__":
    print("🚀 Spouštím Property Market API...")
    print("📡 API bude dostupné na: http://localhost:8000")
    print("📊 Frontend běží na: http://localhost:5173")
    
    try:
        import uvicorn
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            access_log=False
        )
    except ImportError:
        print("❌ Uvicorn není nainstalován")
        os.system("python -m pip install uvicorn")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)