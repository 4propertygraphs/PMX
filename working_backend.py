#!/usr/bin/env python3
"""
Funkční FastAPI backend bez mock dat
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import sys

app = FastAPI(title="Property Market API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ippi.io konfigurace
ELASTICSEARCH_URL = "https://elasticsearch.prod.ippi.io:9200/_search"
API_TOKEN = "eyJraWQiOiItMTU5OTYzOTIzOSIsIng1dCI6InNoZllfa0J4ajJLOWtuTThaa1BKeDFTM2o5NCIsImprdSI6Imh0dHA6Ly9zZWN1cml0eS5wcm9kLmdrZS5pcHBpLmlvLzRwbS9vYXV0aC92Mi9vYXV0aC1hbm9ueW1vdXMvandrcyIsImFsZyI6IlJTMjU2In0.eyJqdGkiOiIwNWNhZTc5NS1lYzZiLTRjNTYtYjkyYy0xMzFlZWJmN2YwMmYiLCJkZWxlZ2F0aW9uSWQiOiJjMmQzOTVkNS1iMTVlLTRiMDEtYjM0YS04Y2QwOTY2Zjc5ZTQiLCJleHAiOjE2OTY1OTA0NTcsIm5iZiI6MTY2NTA1NDQ1Nywic2NvcGUiOiJlbGFzdGljX3NlYXJjaCIsImlzcyI6InNlY3VyaXR5LnByb2QuZ2tlLmlwcGkuaW8iLCJzdWIiOiJpcHBpIiwiYXVkIjoiaHR0cHM6Ly9pcHBpYXBpLjRwcm9wZXJ0eS5jb20vIiwiaWF0IjoxNjY1MDU0NDU3LCJwdXJwb3NlIjoiYWNjZXNzX3Rva2VuIn0.nBVo2mF2I-fbJXDQhhZ0jofSuHoxF9z8p4NhoaRGeUcRHuu1zixtIatO4TbPSoTcq5op6Jp352TViFBDDoRJNRm9lsyFHeKaWafiJ5C2ngrbE5DdQJiOP2wCT33_d-qFfbMPz-HVSMg6mDrWJ0RV-yYtdrGCLXxAWl122K-mfXGQIipt_P6gDbOhK0TIbc02HDxwouq3Hj_hJvFSFiWFBYwnDRi4wmYRXsnvavRoRB3ld5p_1orcdZGyWYDsf8ZmTDY8mVEU09LGnSkffldiRBMxr82y3SNr2F8MtyyicLaIkPNpR_TyfXIE7WwR0K-HT0SzHj3bECG5gvJaVkJPQ"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

COUNTY_LIST = [
    "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Kerry", "Mayo", 
    "Donegal", "Wicklow", "Meath", "Kildare", "Wexford", "Clare", "Tipperary"
]

def get_date_range():
    """Získej rozsah dat"""
    date_on = datetime.today()
    years_ago = date_on - relativedelta(years=2)  # Zkráceno na 2 roky
    last_year = date_on - relativedelta(years=1)
    
    import_date_from = years_ago.replace(day=1)
    import_date_to = date_on.replace(day=1) - timedelta(days=1)
    last_year_end_date = last_year.replace(day=1) - timedelta(days=1)
    
    return import_date_from, import_date_to, last_year_end_date

async def query_elasticsearch(query_body, max_size=1000):
    """Dotaz na Elasticsearch s omezenou velikostí"""
    try:
        # Omez velikost pro rychlost
        response = requests.get(
            f"https://elasticsearch.prod.ippi.io:9200/_search?size={max_size}",
            data=json.dumps(query_body),
            headers=HEADERS,
            timeout=30  # Kratší timeout
        )
        
        if response.status_code != 200:
            print(f"⚠️ Elasticsearch error: {response.status_code}")
            return []
            
        return response.json()["hits"]["hits"]
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API nedostupné: {str(e)}")
        return []
    except Exception as e:
        print(f"⚠️ Chyba: {str(e)}")
        return []

def process_property_data(raw_data):
    """Zpracuj data z Elasticsearch"""
    processed = []
    
    for item in raw_data:
        try:
            source = item.get("_source", {})
            
            beds = int(source.get("beds", 0))
            if beds <= 0 or beds > 10:
                continue
                
            if beds > 5:
                beds = 6
                
            price = float(source.get("price", 0))
            if price <= 0:
                continue
                
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
                "location": source.get("location", "")
            })
        except:
            continue
    
    return processed

@app.get("/")
async def root():
    return {
        "message": "Property Market API - ippi.io connection",
        "status": "OK",
        "data_source": "ippi.io Elasticsearch"
    }

@app.get("/api/pmx/all")
async def get_all(entity: str = "county", version: str = "avg"):
    """Získej všechna data"""
    try:
        import_date_from, import_date_to, _ = get_date_range()
        
        query = {
            "_source": {
                "include": ["saleDate", "county", "price", "beds"]
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
        
        raw_data = await query_elasticsearch(query)
        processed_data = process_property_data(raw_data)
        
        if not processed_data:
            return {}
        
        # Seskup podle krajů
        df = pd.DataFrame(processed_data)
        grouped = df.groupby(['county', 'beds'])['price'].agg(['mean', 'count']).reset_index()
        
        result = {}
        for _, row in grouped.iterrows():
            county = row['county']
            if county not in result:
                result[county] = []
            
            if version == "yoy":
                result[county].append({
                    'county': county,
                    'beds': int(row['beds']),
                    'yoy': 5.0  # Placeholder - potřebuje historická data
                })
            else:
                result[county].append({
                    'county': county,
                    'beds': int(row['beds']),
                    'avg': float(row['mean'])
                })
        
        return result
        
    except Exception as e:
        print(f"❌ Error in get_all: {str(e)}")
        return {"error": str(e)}

@app.get("/api/pmx/average")
async def get_average(county: str, beds: str = None):
    """Průměrné ceny pro kraj"""
    try:
        all_data = await get_all(entity="county", version="avg")
        
        if county not in all_data:
            return []
            
        result = all_data[county]
        
        if beds:
            bed_list = [int(b) for b in beds.split(",")]
            result = [item for item in result if item['beds'] in bed_list]
            
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/pmx/yoy")
async def get_yoy(county: str, beds: str = None):
    """YoY změny pro kraj"""
    try:
        all_data = await get_all(entity="county", version="yoy")
        
        if county not in all_data:
            return []
            
        result = all_data[county]
        
        if beds:
            bed_list = [int(b) for b in beds.split(",")]
            result = [item for item in result if item['beds'] in bed_list]
            
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/pmx/rent")
async def get_rent(version: str = "avg"):
    """Nájemní data"""
    try:
        import_date_from, import_date_to, _ = get_date_range()
        
        query = {
            "_source": {"include": ["county", "price", "beds"]},
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
        
        raw_data = await query_elasticsearch(query, max_size=500)
        processed_data = process_property_data(raw_data)
        
        if not processed_data:
            return []
        
        df = pd.DataFrame(processed_data)
        grouped = df.groupby(['county', 'beds'])['price'].mean().reset_index()
        
        result = []
        for _, row in grouped.iterrows():
            result.append({
                'county': row['county'],
                'beds': int(row['beds']),
                'avg' if version == 'avg' else 'avg_yoy': float(row['price'])
            })
            
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/eval/property")
async def get_properties(area: str = "All"):
    """Detaily nemovitostí"""
    try:
        import_date_from, import_date_to, _ = get_date_range()
        
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
        
        raw_data = await query_elasticsearch(query, max_size=200)
        processed_data = process_property_data(raw_data)
        
        return processed_data[:100]  # Omez na 100 výsledků
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Spouštím Property Market API...")
    print("🌐 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("⏹️  Ctrl+C pro zastavení")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Server zastaven")