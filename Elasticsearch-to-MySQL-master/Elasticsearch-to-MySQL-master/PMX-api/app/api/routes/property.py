import datetime
import json

import pandas as pd
from app.api.utils.auth.check_api_key import auth_api_key
from db.models.property import addressData
from db.queries.queries import querying
from fastapi import APIRouter
from sqlalchemy import select

router = APIRouter()


def convert_timestamp(self, timestamp):
    timestamp_seconds = timestamp.timestamp()
    dt_object = datetime.utcfromtimestamp(timestamp_seconds)
    return dt_object.strftime("%Y/%m/%d")


@router.get("/property")
async def get_properties(
    key: str,
    domain: str,
    area: str | None = None,
):
    if area is not None:
        area = area.capitalize()

    auth_api_key(key=key, domain=domain)

    ENTITY_TABLE_MAP = {
        "query": select(addressData),
        "columns": [
            "county",
            "region",
            "area",
            "beds",
            "price",
            "rawAddress",
            "location",
            "saleDate",
            "sqrMetres",
        ],
    }

    insert = querying()
    df = insert.general_query(ENTITY_TABLE_MAP, return_type=pd.DataFrame)
    if not area == "All":
        response_df = df[
            (df["county"] == area) | (df["region"] == area) | (df["area"] == area)
        ]
    else:
        response_df = df
    new_index = [i for i in range(len(response_df.index))]
    response_df.index = new_index
    response_raw = response_df[ENTITY_TABLE_MAP["columns"]].to_json(orient="index")
    response = json.loads(response_raw)
    return response
