#!/usr/bin/env python3
"""
Simple FastAPI backend that directly calls ippi.io Elasticsearch API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

app = FastAPI(title="Property Market API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ippi.io API configuration
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
    """Get date range for data queries"""
    date_on = datetime.today()
    years_ago = date_on - relativedelta(years=3)
    last_year = date_on - relativedelta(years=1)
    
    import_date_from = years_ago.replace(day=1)
    next_month = date_on.replace(day=28) + timedelta(days=4)
    import_date_to = next_month - timedelta(days=next_month.day)
    next_month = last_year.replace(day=28) + timedelta(days=4)
    last_year_end_date = next_month - timedelta(days=next_month.day)
    
    return import_date_from, import_date_to, last_year_end_date

async def query_elasticsearch(query_body):
    """Query ippi.io Elasticsearch API"""
    try:
        # First get total count
        response = requests.get(
            ELASTICSEARCH_URL,
            data=json.dumps(query_body),
            headers=HEADERS,
            timeout=40
        )
        response.raise_for_status()
        
        result = response.json()
        total_records = result["hits"]["total"]
        
        # Get all records
        response = requests.get(
            f"https://elasticsearch.prod.ippi.io:9200/_search?size={total_records}",
            data=json.dumps(query_body),
            headers=HEADERS,
            timeout=40
        )
        response.raise_for_status()
        
        return response.json()["hits"]["hits"]
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Elasticsearch API error: {str(e)}")

def process_property_data(raw_data, market_type="Residential Sale"):
    """Process raw Elasticsearch data into structured format"""
    processed = []
    
    for item in raw_data:
        source = item["_source"]
        
        # Basic validation
        if not source.get("beds") or not source.get("price") or not source.get("county"):
            continue
            
        beds = int(source["beds"]) if source["beds"] else 0
        if beds == 0:
            continue
            
        # Cap beds at 6+
        if beds > 5:
            beds = 6
            
        price = float(source["price"]) if source["price"] else 0
        if price <= 0:
            continue
            
        # Filter valid counties
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
    
    return processed

def calculate_averages_and_yoy(current_data, last_year_data):
    """Calculate averages and year-over-year changes"""
    # Group current year data
    current_df = pd.DataFrame(current_data)
    if current_df.empty:
        return {}, {}
        
    current_grouped = current_df.groupby(['county', 'beds'])['price'].agg(['mean', 'count']).reset_index()
    current_grouped.columns = ['county', 'beds', 'avg', 'count']
    
    # Group last year data
    last_year_df = pd.DataFrame(last_year_data)
    if not last_year_df.empty:
        last_year_grouped = last_year_df.groupby(['county', 'beds'])['price'].mean().reset_index()
        last_year_grouped.columns = ['county', 'beds', 'last_year_avg']
    else:
        last_year_grouped = pd.DataFrame(columns=['county', 'beds', 'last_year_avg'])
    
    # Merge and calculate YoY
    merged = current_grouped.merge(last_year_grouped, on=['county', 'beds'], how='left')
    merged['yoy'] = ((merged['avg'] - merged['last_year_avg']) / merged['last_year_avg'] * 100).fillna(0)
    
    # Convert to dictionaries grouped by county
    avg_result = {}
    yoy_result = {}
    
    for _, row in merged.iterrows():
        county = row['county']
        
        if county not in avg_result:
            avg_result[county] = []
            yoy_result[county] = []
            
        avg_result[county].append({
            'county': county,
            'beds': int(row['beds']),
            'avg': float(row['avg']),
            'count': int(row['count'])
        })
        
        yoy_result[county].append({
            'county': county,
            'beds': int(row['beds']),
            'yoy': float(row['yoy'])
        })
    
    return avg_result, yoy_result

@app.get("/")
async def root():
    return {"message": "Property Market API - Direct ippi.io connection"}

@app.get("/api/pmx/all")
async def get_all(entity: str = "county", version: str = "avg"):
    """Get all property data"""
    try:
        import_date_from, import_date_to, last_year_end_date = get_date_range()
        
        # Query for current period
        current_query = {
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
        
        # Query for last year period
        last_year_query = {
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
                                "lte": last_year_end_date.strftime("%Y-%m-%d")
                            }
                        }
                    }]
                }
            }
        }
        
        # Get data from Elasticsearch
        current_raw = await query_elasticsearch(current_query)
        last_year_raw = await query_elasticsearch(last_year_query)
        
        # Process data
        current_data = process_property_data(current_raw)
        last_year_data = process_property_data(last_year_raw)
        
        # Calculate averages and YoY
        avg_result, yoy_result = calculate_averages_and_yoy(current_data, last_year_data)
        
        if version == "yoy":
            return yoy_result
        else:
            return avg_result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.get("/api/pmx/average")
async def get_average(county: str, beds: str = None):
    """Get average prices for specific county"""
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
        raise HTTPException(status_code=500, detail=f"Error getting averages: {str(e)}")

@app.get("/api/pmx/yoy")
async def get_yoy(county: str, beds: str = None):
    """Get year-over-year changes for specific county"""
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
        raise HTTPException(status_code=500, detail=f"Error getting YoY data: {str(e)}")

@app.get("/api/pmx/rent")
async def get_rent(version: str = "avg"):
    """Get rental market data"""
    try:
        import_date_from, import_date_to, last_year_end_date = get_date_range()
        
        # Query for rental data
        rent_query = {
            "_source": {
                "include": ["saleDate", "county", "price", "beds"]
            },
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
        
        rent_raw = await query_elasticsearch(rent_query)
        rent_data = process_property_data(rent_raw, "Residential Rent")
        
        if not rent_data:
            return []
            
        # Calculate rent averages
        rent_df = pd.DataFrame(rent_data)
        rent_grouped = rent_df.groupby(['county', 'beds'])['price'].mean().reset_index()
        
        result = []
        for _, row in rent_grouped.iterrows():
            result.append({
                'county': row['county'],
                'beds': int(row['beds']),
                'avg' if version == 'avg' else 'avg_yoy': float(row['price'])
            })
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting rent data: {str(e)}")

@app.get("/api/eval/property")
async def get_properties(area: str = "All"):
    """Get individual property details"""
    try:
        import_date_from, import_date_to, _ = get_date_range()
        
        property_query = {
            "_source": {
                "include": [
                    "county", "region", "area", "beds", "price", "rawAddress",
                    "location", "saleDate", "sqrMetres"
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
        
        # Add area filter if specified
        if area != "All":
            property_query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": area,
                    "fields": ["county", "region", "area"]
                }
            })
        
        raw_data = await query_elasticsearch(property_query)
        processed_data = process_property_data(raw_data)
        
        # Limit to 1000 results for performance
        return processed_data[:1000]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting properties: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Property Market API...")
    print("📊 Direct connection to ippi.io Elasticsearch")
    print("🌐 Server running on http://localhost:8000")
    print("📖 API docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)