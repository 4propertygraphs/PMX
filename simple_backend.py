#!/usr/bin/env python3
"""
FastAPI backend s přímým napojením na ippi.io API - POUZE SKUTEČNÁ DATA
"""

import sys
import os

# Přidej cestu k PMX-api modulu
sys.path.append("Elasticsearch-to-MySQL-master/Elasticsearch-to-MySQL-master/PMX-api")

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import json
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    import requests
    import pandas as pd
    
    # Import existujícího autentifikačního systému
    from app.api.utils.auth.check_api_key import auth_api_key
    
except ImportError as e:
    print(f"Chyba importu: {e}")
    print("CHYBA: Některé moduly nejsou dostupné. Zkontroluj cestu k PMX-api.")
    exit(1)

# Vytvoření FastAPI aplikace
app = FastAPI(
    title="Property Market API",
    description="API pro analýzu nemovitostního trhu s přímým napojením na ippi.io",
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

# ippi.io API konfigurace
ELASTICSEARCH_URL = "https://elasticsearch.prod.ippi.io:9200/_search"
API_TOKEN = "eyJraWQiOiItMTU5OTYzOTIzOSIsIng1dCI6InNoZllfa0J4ajJLOWtuTThaa1BKeDFTM2o5NCIsImprdSI6Imh0dHA6Ly9zZWN1cml0eS5wcm9kLmdrZS5pcHBpLmlvLzRwbS9vYXV0aC92Mi9vYXV0aC1hbm9ueW1vdXMvandrcyIsImFsZyI6IlJTMjU2In0.eyJqdGkiOiIwNWNhZTc5NS1lYzZiLTRjNTYtYjkyYy0xMzFlZWJmN2YwMmYiLCJkZWxlZ2F0aW9uSWQiOiJjMmQzOTVkNS1iMTVlLTRiMDEtYjM0YS04Y2QwOTY2Zjc5ZTQiLCJleHAiOjE2OTY1OTA0NTcsIm5iZiI6MTY2NTA1NDQ1Nywic2NvcGUiOiJlbGFzdGljX3NlYXJjaCIsImlzcyI6InNlY3VyaXR5LnByb2QuZ2tlLmlwcGkuaW8iLCJzdWIiOiJpcHBpIiwiYXVkIjoiaHR0cHM6Ly9pcHBpYXBpLjRwcm9wZXJ0eS5jb20vIiwiaWF0IjoxNjY1MDU0NDU3LCJwdXJwb3NlIjoiYWNjZXNzX3Rva2VuIn0.nBVo2mF2I-fbJXDQhhZ0jofSuHoxF9z8p4NhoaRGeUcRHuu1zixtIatO4TbPSoTcq5op6Jp352TViFBDDoRJNRm9lsyFHeKaWafiJ5C2ngrbE5DdQJiOP2wCT33_d-qFfbMPz-HVSMg6mDrWJ0RV-yYtdrGCLXxAWl122K-mfXGQIipt_P6gDbOhK0TIbc02HDxwouq3Hj_hJvFSFiWFBYwnDRi4wmYRXsnvavRoRB3ld5p_1orcdZGyWYDsf8ZmTDY8mVEU09LGnSkffldiRBMxr82y3SNr2F8MtyyicLaIkPNpR_TyfXIE7WwR0K-HT0SzHj3bECG5gvJaVkJPQ"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

COUNTY_LIST = [
    "Antrim", "Carlow", "Cavan", "Clare", "Cork", "Donegal", "Down", "Dublin",
    "Fermanagh", "Galway", "Kerry", "Kildare", "Kilkenny", "Laoighis", "Laois",
    "Leitrim", "Limerick", "Longford", "Louth", "Mayo", "Meath", "Monaghan",
    "Offaly", "Roscommon", "Sligo", "Tipperary", "Tyrone", "Waterford",
    "Westmeath", "Wexford", "Wicklow"
]

def get_date_range():
    """Získej rozsah dat pro dotazy"""
    date_on = datetime.today()
    years_ago = date_on - relativedelta(years=3)
    last_year = date_on - relativedelta(years=1)
    
    import_date_from = years_ago.replace(day=1)
    next_month = date_on.replace(day=28) + timedelta(days=4)
    import_date_to = next_month - timedelta(days=next_month.day)
    next_month = last_year.replace(day=28) + timedelta(days=4)
    last_year_end_date = next_month - timedelta(days=next_month.day)
    
    return import_date_from, import_date_to, last_year_end_date

async def query_elasticsearch(query_body, max_size=10000):
    """Dotaz na ippi.io Elasticsearch"""
    try:
        # Nejdříve získej celkový počet záznamů
        response = requests.get(
            ELASTICSEARCH_URL,
            data=json.dumps(query_body),
            headers=HEADERS,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Elasticsearch error: {response.status_code}")
            return []
        
        total_records = response.json()["hits"]["total"]
        print(f"📊 Celkem nalezeno záznamů: {total_records}")
        
        # Získej všechna data
        size = min(total_records, max_size)
        response = requests.get(
            f"https://elasticsearch.prod.ippi.io:9200/_search?size={size}",
            data=json.dumps(query_body),
            headers=HEADERS,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()["hits"]["hits"]
        else:
            print(f"❌ Error getting data: {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return []

def process_elasticsearch_data(raw_data):
    """Zpracuj data z Elasticsearch"""
    processed = []
    
    for item in raw_data:
        try:
            source = item.get("_source", {})
            
            # Validace dat
            beds = source.get("beds")
            if not beds or beds <= 0:
                continue
                
            beds = int(beds)
            if beds > 5:
                beds = 6
                
            price = source.get("price")
            if not price or price <= 0:
                continue
                
            price = float(price)
            county = source.get("county", "")
            
            if county not in COUNTY_LIST:
                continue
                
            processed.append({
                "county": county,
                "beds": beds,
                "price": price,
                "area": source.get("area", ""),
                "region": source.get("region", ""),
                "saleDate": source.get("saleDate", ""),
                "rawAddress": source.get("rawAddress", ""),
                "sqrMetres": source.get("sqrMetres", 0),
                "location": source.get("location", ""),
                "id": source.get("id", "")
            })
            
        except Exception as e:
            continue
    
    return processed

def calculate_averages_and_yoy(data):
    """Vypočítej průměry a YoY změny ze skutečných dat"""
    if not data:
        return {}, {}
    
    df = pd.DataFrame(data)
    
    # Převeď datum
    df['saleDate'] = pd.to_datetime(df['saleDate'])
    df['month_year'] = df['saleDate'].dt.to_period('M')
    
    # Odstraň outliers (5% - 95% percentil)
    condition = (df['price'] > df['price'].quantile(0.05)) & (df['price'] < df['price'].quantile(0.95))
    df_clean = df.loc[condition]
    
    # Seskup podle krajů a ložnic
    grouped = df_clean.groupby(['county', 'beds'])['price'].agg(['mean', 'count']).reset_index()
    
    # Vytvoř výsledky pro průměry
    avg_results = {}
    for _, row in grouped.iterrows():
        county = row['county']
        if county not in avg_results:
            avg_results[county] = []
        
        avg_results[county].append({
            'county': county,
            'beds': int(row['beds']),
            'avg': float(row['mean'])
        })
    
    # Pro YoY - porovnej s loňskými daty
    current_year = datetime.now().year
    last_year = current_year - 1
    
    current_year_data = df_clean[df_clean['saleDate'].dt.year == current_year]
    last_year_data = df_clean[df_clean['saleDate'].dt.year == last_year]
    
    yoy_results = {}
    if not current_year_data.empty and not last_year_data.empty:
        current_grouped = current_year_data.groupby(['county', 'beds'])['price'].mean().reset_index()
        last_grouped = last_year_data.groupby(['county', 'beds'])['price'].mean().reset_index()
        
        for _, current_row in current_grouped.iterrows():
            county = current_row['county']
            beds = current_row['beds']
            current_price = current_row['price']
            
            # Najdi odpovídající loňský záznam
            last_row = last_grouped[
                (last_grouped['county'] == county) & 
                (last_grouped['beds'] == beds)
            ]
            
            if not last_row.empty:
                last_price = last_row.iloc[0]['price']
                yoy_change = ((current_price - last_price) / last_price) * 100
                
                if county not in yoy_results:
                    yoy_results[county] = []
                
                yoy_results[county].append({
                    'county': county,
                    'beds': int(beds),
                    'yoy': round(yoy_change, 1)
                })
    
    return avg_results, yoy_results

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Property Market API s přímým napojením na ippi.io",
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "data_source": "ippi.io Elasticsearch - POUZE SKUTEČNÁ DATA"
    }

@app.get("/api/pmx/all")
async def get_all_data(
    key: str = Query(..., description="API klíč"),
    domain: str = Query(..., description="Doména"),
    entity: str = Query("county", description="Entita (county/region/area)"),
    version: str = Query("avg", description="Verze (avg/yoy)")
):
    """Získat všechna data podle entity a verze - POUZE SKUTEČNÁ DATA"""
    try:
        # Autentifikace
        auth_api_key(key=key, domain=domain)
        
        # Získej rozsah dat
        import_date_from, import_date_to, _ = get_date_range()
        
        # Elasticsearch dotaz
        query = {
            "_source": {
                "include": [
                    "saleDate", "county", "area", "region", "rawAddress", "price",
                    "beds", "id", "sqrMetres", "location"
                ]
            },
            "query": {
                "bool": {
                    "must": [{"match": {"marketType": "Residential Sale"}}],
                    "filter": [{
                        "range": {
                            "saleDate": {
                                "gte": import_date_from.strftime("%Y-%m-%d"),
                                "lte": import_date_to.strftime("%Y-%m-%d")
                            }
                        }
                    }]
                }
            }
        }
        
        print(f"🔍 Dotazuji ippi.io od {import_date_from} do {import_date_to}")
        raw_data = await query_elasticsearch(query)
        
        if not raw_data:
            return {"error": "Žádná data z ippi.io", "data": {}}
        
        processed_data = process_elasticsearch_data(raw_data)
        print(f"✅ Zpracováno {len(processed_data)} skutečných záznamů")
        
        avg_results, yoy_results = calculate_averages_and_yoy(processed_data)
        
        if version == "yoy":
            return yoy_results
        else:
            return avg_results
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"Chyba při načítání dat: {str(e)}", "data": {}}

@app.get("/api/pmx/average")
async def get_average_prices(
    key: str = Query(...),
    domain: str = Query(...),
    county: str = Query(...),
    beds: str = Query(None),
    region: str = Query(None),
    area: str = Query(None)
):
    """Získat průměrné ceny - POUZE SKUTEČNÁ DATA"""
    try:
        auth_api_key(key=key, domain=domain)
        
        # Získej všechna data a filtruj
        all_data = await get_all_data(key, domain, "county", "avg")
        
        if county not in all_data:
            return []
        
        result = all_data[county]
        
        # Filtruj podle ložnic
        if beds:
            bed_list = [int(b) for b in beds.split(",")]
            result = [item for item in result if item['beds'] in bed_list]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"Chyba při načítání průměrných cen: {str(e)}"}

@app.get("/api/pmx/yoy")
async def get_yoy_changes(
    key: str = Query(...),
    domain: str = Query(...),
    county: str = Query(...),
    beds: str = Query(None),
    region: str = Query(None),
    area: str = Query(None)
):
    """Získat year-over-year změny - POUZE SKUTEČNÁ DATA"""
    try:
        auth_api_key(key=key, domain=domain)
        
        # Získej YoY data
        all_data = await get_all_data(key, domain, "county", "yoy")
        
        if county not in all_data:
            return []
        
        result = all_data[county]
        
        # Filtruj podle ložnic
        if beds:
            bed_list = [int(b) for b in beds.split(",")]
            result = [item for item in result if item['beds'] in bed_list]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"Chyba při načítání YoY dat: {str(e)}"}

@app.get("/api/pmx/rent")
async def get_rent_data(
    key: str = Query(...),
    domain: str = Query(...),
    version: str = Query("avg")
):
    """Získat data o nájemním trhu - POUZE SKUTEČNÁ DATA"""
    try:
        auth_api_key(key=key, domain=domain)
        
        # Získej rozsah dat
        import_date_from, import_date_to, _ = get_date_range()
        
        # Elasticsearch dotaz pro nájmy
        query = {
            "_source": {"include": ["county", "price", "beds", "saleDate"]},
            "query": {
                "bool": {
                    "must": [{"match": {"marketType": "Residential Rent"}}],
                    "filter": [{
                        "range": {
                            "saleDate": {
                                "gte": import_date_from.strftime("%Y-%m-%d"),
                                "lte": import_date_to.strftime("%Y-%m-%d")
                            }
                        }
                    }]
                }
            }
        }
        
        print("🏠 Dotazuji nájemní data z ippi.io")
        raw_data = await query_elasticsearch(query, max_size=5000)
        
        if not raw_data:
            return []
        
        processed_data = process_elasticsearch_data(raw_data)
        
        if not processed_data:
            return []
        
        # Seskup podle krajů a ložnic
        df = pd.DataFrame(processed_data)
        
        if version == "yoy":
            # Vypočítej YoY pro nájmy
            df['saleDate'] = pd.to_datetime(df['saleDate'])
            current_year = datetime.now().year
            last_year = current_year - 1
            
            current_data = df[df['saleDate'].dt.year == current_year]
            last_data = df[df['saleDate'].dt.year == last_year]
            
            if current_data.empty or last_data.empty:
                return []
            
            current_grouped = current_data.groupby(['county', 'beds'])['price'].mean().reset_index()
            last_grouped = last_data.groupby(['county', 'beds'])['price'].mean().reset_index()
            
            result = []
            for _, current_row in current_grouped.iterrows():
                county = current_row['county']
                beds = current_row['beds']
                current_price = current_row['price']
                
                last_row = last_grouped[
                    (last_grouped['county'] == county) & 
                    (last_grouped['beds'] == beds)
                ]
                
                if not last_row.empty:
                    last_price = last_row.iloc[0]['price']
                    yoy_change = ((current_price - last_price) / last_price) * 100
                    
                    result.append({
                        'county': county,
                        'beds': int(beds),
                        'avg_yoy': round(yoy_change, 1)
                    })
        else:
            # Průměrné nájmy
            grouped = df.groupby(['county', 'beds'])['price'].mean().reset_index()
            result = []
            for _, row in grouped.iterrows():
                result.append({
                    'county': row['county'],
                    'beds': int(row['beds']),
                    'avg': float(row['price'])
                })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"Chyba při načítání rent dat: {str(e)}"}

@app.get("/api/eval/property")
async def get_property_details(
    key: str = Query(...),
    domain: str = Query(...),
    area: str = Query("All")
):
    """Získat detaily jednotlivých nemovitostí - POUZE SKUTEČNÁ DATA"""
    try:
        auth_api_key(key=key, domain=domain)
        
        # Získej rozsah dat
        import_date_from, import_date_to, _ = get_date_range()
        
        # Elasticsearch dotaz
        query = {
            "_source": {
                "include": [
                    "county", "region", "area", "beds", "price", 
                    "rawAddress", "location", "saleDate", "sqrMetres"
                ]
            },
            "query": {
                "bool": {
                    "must": [{"match": {"marketType": "Residential Sale"}}],
                    "filter": [{
                        "range": {
                            "saleDate": {
                                "gte": import_date_from.strftime("%Y-%m-%d"),
                                "lte": import_date_to.strftime("%Y-%m-%d")
                            }
                        }
                    }]
                }
            }
        }
        
        print("🔍 Dotazuji detaily nemovitostí z ippi.io")
        raw_data = await query_elasticsearch(query, max_size=1000)
        
        if not raw_data:
            return []
        
        processed_data = process_elasticsearch_data(raw_data)
        
        # Filtruj podle oblasti
        if area != "All":
            filtered_data = []
            for prop in processed_data:
                if (prop['county'] == area or 
                    prop['region'] == area or 
                    prop['area'] == area):
                    filtered_data.append(prop)
            processed_data = filtered_data
        
        return processed_data[:100]  # Omez na 100 výsledků
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"Chyba při načítání property dat: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test připojení k ippi.io
        test_query = {
            "query": {"match_all": {}},
            "size": 1
        }
        
        response = requests.get(
            ELASTICSEARCH_URL,
            data=json.dumps(test_query),
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "ippi_connection": "connected",
                "data_source": "ippi.io Elasticsearch - POUZE SKUTEČNÁ DATA"
            }
        else:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "ippi_connection": f"error: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "ippi_connection": f"error: {str(e)}"
        }

if __name__ == "__main__":
    print("🚀 Spouštím Property Market API s přímým napojením na ippi.io...")
    print("📡 API bude dostupné na: http://localhost:8000")
    print("📊 Používá přímo ippi.io Elasticsearch - POUZE SKUTEČNÁ DATA")
    print("🔑 Použij API klíč: test_api_key_123, domain: localhost")
    
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
        print("❌ Uvicorn není nainstalován.")
        exit(1)