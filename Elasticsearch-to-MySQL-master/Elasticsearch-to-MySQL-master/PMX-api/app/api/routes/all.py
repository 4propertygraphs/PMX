import json

import pandas as pd
from app.api.utils.auth.check_api_key import auth_api_key
from db.models.current_year_area import CurrentYearArea
from db.models.current_year_county import CurrentYearCounty
from db.models.current_year_region import CurrentYearRegion
from db.models.pmx_yoy import CountyYoY
from db.models.pmx_yoy_area import PMXYoYArea
from db.models.pmx_yoy_region import PMXYoYRegion
from db.queries.queries import querying
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()

# this route is here so you can get all of the information about a specific region.
# It gets used for example by generating the PMX output.
@router.get("/all")
async def get_all(
    key: str,
    domain: str,
    version: str,
    entity: str,
):
    if version == "average":
        version = "avg"

    auth_api_key(key=key, domain=domain)
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
            "columns": ["index", "area", "beds", "county"],
        },
    }

    # this maps whatever the user send to VERSION_TABLE_MAP so 
    # we can request the correct table in the database
    if entity not in VERSION_TABLE_MAP:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Entity is incorrect. Entity should be ('region', 'area', 'county')",
        )
    entity_map = VERSION_TABLE_MAP[entity]

    if version not in entity_map:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Version is incorrect. Version should be ('yoy', 'average')",
        )
    entity_map["columns"].append(version)
    entity_dict = {
        "query": select(entity_map[version]),
        "columns": entity_map["columns"],
    }

    insert = querying()
    r = insert.general_query(entity_dict)
    df = pd.read_json(r, orient="index")

    # This makes the output more readable and makes the output correct
    output = {}
    for entities in df[entity].unique():
        temp_df = df.loc[df[entity] == entities]
        entities_dict = temp_df.to_dict(orient="records")
        output[entities] = entities_dict

    json_output = json.dumps(output)
    json_output = json.loads(json_output)
    return json_output
