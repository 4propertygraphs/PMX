#!/usr/bin/env python3
"""
FastAPI backend s použitím existujícího autentifikačního a databázového systému
"""

import sys
import os

# Přidej cestu k PMX-api modulu
sys.path.append("Elasticsearch-to-MySQL-master/Elasticsearch-to-MySQL-master/PMX-api")

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import json
    from datetime import datetime
    
    # Import existujících modulů z projektu
    from app.api.utils.auth.check_api_key import auth_api_key
    from db.database_connection import DatabaseConnection
    from db.queries.queries import querying
    from db.models.current_year_county import CurrentYearCounty
    from db.models.current_year_region import CurrentYearRegion
    from db.models.current_year_area import CurrentYearArea
    from db.models.pmx_yoy import CountyYoY
    from db.models.pmx_yoy_region import PMXYoYRegion
    from db.models.pmx_yoy_area import PMXYoYArea
    from db.models.rent_avg import rent_avg
    from db.models.rent_yoy import RentYoy
    from db.models.property import addressData
    from sqlalchemy import select, and_
    
except ImportError as e:
    print(f"Chyba importu: {e}")
    print("CHYBA: Některé moduly nejsou dostupné. Zkontroluj cestu k PMX-api.")
    exit(1)

# Vytvoření FastAPI aplikace
app = FastAPI(
    title="Property Market API",
    description="API pro analýzu nemovitostního trhu s databází",
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Property Market API s databází je spuštěno",
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "database": "MySQL PMX Report"
    }

@app.get("/api/pmx/all")
async def get_all_data(
    key: str = Query(..., description="API klíč"),
    domain: str = Query(..., description="Doména"),
    entity: str = Query("county", description="Entita (county/region/area)"),
    version: str = Query("avg", description="Verze (avg/yoy)")
):
    """Získat všechna data podle entity a verze"""
    try:
        # Autentifikace
        auth_api_key(key=key, domain=domain)
        
        # Mapování tabulek
        VERSION_TABLE_MAP = {
            "county": {
                "yoy": CountyYoY,
                "avg": CurrentYearCounty,
                "columns": ["index", "county", "beds"],
            },
            "region": {
                "yoy": PMXYoYRegion,
                "avg": CurrentYearRegion,
                "columns": ["index", "region", "beds", "county"],
            },
            "area": {
                "yoy": PMXYoYArea,
                "avg": CurrentYearArea,
                "columns": ["index", "area", "beds", "county", "region"],
            },
        }
        
        if entity not in VERSION_TABLE_MAP:
            raise HTTPException(status_code=400, detail="Entity musí být 'county', 'region' nebo 'area'")
        
        entity_map = VERSION_TABLE_MAP[entity]
        
        if version not in entity_map:
            raise HTTPException(status_code=400, detail="Version musí být 'yoy' nebo 'avg'")
        
        # Přidej správný sloupec pro data
        columns = entity_map["columns"].copy()
        columns.append(version if version == "yoy" else "avg")
        
        entity_dict = {
            "query": select(entity_map[version]),
            "columns": columns,
        }
        
        # Dotaz do databáze
        query_handler = querying()
        result = query_handler.general_query(entity_dict)
        
        # Parsuj JSON výsledek
        import pandas as pd
        df = pd.read_json(result, orient="index")
        
        # Seskup podle entity
        output = {}
        entity_column = entity if entity != "avg" else "county"
        
        for entity_name in df[entity_column].unique():
            temp_df = df.loc[df[entity_column] == entity_name]
            entities_dict = temp_df.to_dict(orient="records")
            output[entity_name] = entities_dict
        
        return output
        
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
    """Získat průměrné ceny"""
    try:
        auth_api_key(key=key, domain=domain)
        
        beds_list = [1, 2, 3, 4, 5, 6] if beds is None else [int(b) for b in beds.split(",")]
        
        # Určit kterou tabulku použít
        if region and area:
            query = select(CurrentYearArea).where(
                and_(
                    CurrentYearArea.beds.in_(beds_list),
                    CurrentYearArea.region == region,
                    CurrentYearArea.area == area,
                    CurrentYearArea.county == county
                )
            )
            columns = ["region", "area", "beds", "avg", "county"]
        elif region:
            query = select(CurrentYearRegion).where(
                and_(
                    CurrentYearRegion.beds.in_(beds_list),
                    CurrentYearRegion.region == region,
                    CurrentYearRegion.county == county
                )
            )
            columns = ["region", "beds", "avg", "county"]
        elif area:
            query = select(CurrentYearArea).where(
                and_(
                    CurrentYearArea.beds.in_(beds_list),
                    CurrentYearArea.area == area,
                    CurrentYearArea.county == county
                )
            )
            columns = ["area", "beds", "avg", "county"]
        else:
            query = select(CurrentYearCounty).where(
                and_(
                    CurrentYearCounty.beds.in_(beds_list),
                    CurrentYearCounty.county == county
                )
            )
            columns = ["county", "beds", "avg"]
        
        entity_dict = {"query": query, "columns": columns}
        
        query_handler = querying()
        result = query_handler.general_query(entity_dict)
        
        try:
            response = json.loads(result)
            return response
        except (TypeError, json.JSONDecodeError):
            return {}
            
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
    """Získat year-over-year změny"""
    try:
        auth_api_key(key=key, domain=domain)
        
        beds_list = [1, 2, 3, 4, 5, 6] if beds is None else [int(b) for b in beds.split(",")]
        
        # Určit kterou tabulku použít
        if region and area:
            query = select(PMXYoYArea).where(
                and_(
                    PMXYoYArea.beds.in_(beds_list),
                    PMXYoYArea.region == region,
                    PMXYoYArea.area == area,
                    PMXYoYArea.county == county
                )
            )
            columns = ["region", "area", "beds", "yoy", "county"]
        elif region:
            query = select(PMXYoYRegion).where(
                and_(
                    PMXYoYRegion.beds.in_(beds_list),
                    PMXYoYRegion.region == region,
                    PMXYoYRegion.county == county
                )
            )
            columns = ["region", "beds", "yoy", "county"]
        elif area:
            query = select(PMXYoYArea).where(
                and_(
                    PMXYoYArea.beds.in_(beds_list),
                    PMXYoYArea.area == area,
                    PMXYoYArea.county == county
                )
            )
            columns = ["area", "beds", "yoy", "county"]
        else:
            query = select(CountyYoY).where(
                and_(
                    CountyYoY.beds.in_(beds_list),
                    CountyYoY.county == county
                )
            )
            columns = ["county", "beds", "yoy"]
        
        entity_dict = {"query": query, "columns": columns}
        
        query_handler = querying()
        result = query_handler.general_query(entity_dict)
        
        try:
            response = json.loads(result)
            return response
        except (TypeError, json.JSONDecodeError):
            return {}
            
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
    """Získat data o nájemním trhu"""
    try:
        auth_api_key(key=key, domain=domain)
        
        if version == "yoy":
            query = select(RentYoy)
            columns = ["index", "county", "beds", "avg_yoy"]
        elif version == "avg":
            query = select(rent_avg)
            columns = ["index", "county", "beds", "avg"]
        else:
            raise HTTPException(status_code=400, detail="Version musí být 'avg' nebo 'yoy'")
        
        entity_dict = {"query": query, "columns": columns}
        
        query_handler = querying()
        result = query_handler.general_query(entity_dict)
        
        try:
            response = json.loads(result)
            return response
        except (TypeError, json.JSONDecodeError):
            return {}
            
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
    """Získat detaily jednotlivých nemovitostí"""
    try:
        auth_api_key(key=key, domain=domain)
        
        entity_dict = {
            "query": select(addressData),
            "columns": [
                "county", "region", "area", "beds", "price", 
                "rawAddress", "location", "saleDate", "sqrMetres"
            ],
        }
        
        query_handler = querying()
        df = query_handler.general_query(entity_dict, return_type=pd.DataFrame)
        
        if area != "All":
            response_df = df[
                (df["county"] == area) | (df["region"] == area) | (df["area"] == area)
            ]
        else:
            response_df = df
        
        # Resetuj index
        new_index = [i for i in range(len(response_df.index))]
        response_df.index = new_index
        
        response_raw = response_df[entity_dict["columns"]].to_json(orient="index")
        response = json.loads(response_raw)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"Chyba při načítání property dat: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test databázového připojení
        query_handler = querying()
        test_query = {"query": select(CurrentYearCounty).limit(1), "columns": ["county"]}
        query_handler.general_query(test_query)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": f"error: {str(e)}"
        }

if __name__ == "__main__":
    print("🚀 Spouštím Property Market API s databází...")
    print("📡 API bude dostupné na: http://localhost:8000")
    print("📊 Používá MySQL databázi PMX Report")
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