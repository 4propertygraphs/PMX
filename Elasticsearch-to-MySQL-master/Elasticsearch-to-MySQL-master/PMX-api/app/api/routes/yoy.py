# app/api/routes/search.py

import json

from app.api.utils.auth.check_api_key import auth_api_key
from db.models.pmx_yoy import CountyYoY
from db.models.pmx_yoy_area import PMXYoYArea
from db.models.pmx_yoy_region import PMXYoYRegion
from db.queries.queries import querying
from fastapi import APIRouter
from sqlalchemy import and_, select

router = APIRouter()


@router.get("/yoy")
async def get_yoy(
    key: str,
    domain: str,
    county: str,
    beds: str | None = None,
    region: str | None = None,
    area: str | None = None,
):
    auth_api_key(key=key, domain=domain)
    beds = [1, 2, 3, 4, 5, 6] if beds is None else beds.split(",")

    options = f"{region is not None}{area is not None}"

    ENTITY_TABLE_MAP = {
        "TrueTrue": {
            "query": select(PMXYoYArea).where(
                and_(
                    and_(
                        PMXYoYArea.beds.in_(beds),
                        and_(
                            PMXYoYArea.region.in_([region]),
                            PMXYoYArea.area.in_([area]),
                        ),
                    ),
                    PMXYoYArea.county.in_([county]),
                )
            ),
            "columns": ["region", "area", "beds", "yoy", "county"],
        },
        "TrueFalse": {
            "query": select(PMXYoYRegion).where(
                and_(
                    PMXYoYRegion.beds.in_(beds),
                    and_(
                        PMXYoYRegion.region.in_([region]),
                        PMXYoYRegion.county.in_([county]),
                    ),
                )
            ),
            "columns": ["region", "beds", "yoy", "county"],
        },
        "FalseTrue": {
            "query": select(PMXYoYArea).where(
                and_(
                    PMXYoYArea.beds.in_(beds),
                    and_(
                        PMXYoYArea.area.in_([area]),
                        PMXYoYArea.county.in_([county]),
                    ),
                )
            ),
            "columns": ["area", "beds", "yoy", "county"],
        },
        "FalseFalse": {
            "query": select(CountyYoY).where(
                and_(
                    CountyYoY.beds.in_(beds),
                    CountyYoY.county.in_([county]),
                )
            ),
            "columns": ["county", "beds", "yoy"],
        },
    }
    insert = querying()
    r = insert.general_query(ENTITY_TABLE_MAP[options])
    try:
        response = json.loads(r)
    except TypeError:
        response = {}
    return response
