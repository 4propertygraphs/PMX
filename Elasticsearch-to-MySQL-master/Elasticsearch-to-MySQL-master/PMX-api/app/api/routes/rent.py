import json

import pandas as pd
from app.api.utils.auth.check_api_key import auth_api_key
from db.models.rent_yoy import RentYoy
from db.models.rent_avg import rent_avg
from db.queries.queries import querying
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()

@router.get("/rent")
async def get_rent(key: str, domain: str, version: str):
    auth_api_key(key=key, domain=domain)

    if version == "yoy":
        query = select(RentYoy)
        entities = ["index", "county", "beds", "avg_yoy"]
    elif version == "avg":
        query = select(rent_avg)
        entities = ["index", "county", "beds", "avg"]
    else:
         raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Version is incorrect. Entity should be ('avg', 'yoy')",
        )
    
    entity_map = {
        "query": query,
        "columns": entities,
    }
    insert = querying()
    r = insert.general_query(entity_map)
    json_response = json.loads(r)
    return json_response