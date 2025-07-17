import json

from app.api.utils.auth.check_api_key import auth_api_key
from db.models.current_year_area import CurrentYearArea
from db.models.current_year_county import CurrentYearCounty
from db.models.current_year_region import CurrentYearRegion
from db.queries.queries import querying
from fastapi import APIRouter
from sqlalchemy import and_, select

router = APIRouter()


@router.get("/average")
async def get_avg(
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
            "query": select(CurrentYearArea).where(
                and_(
                    and_(
                        CurrentYearArea.beds.in_(beds),
                        and_(
                            CurrentYearArea.region.in_([region]),
                            CurrentYearArea.area.in_([area]),
                        ),
                    ),
                    CurrentYearArea.county.in_([county]),
                )
            ),
            "columns": ["region", "area", "beds", "avg", "county"],
        },
        "TrueFalse": {
            "query": select(CurrentYearRegion).where(
                and_(
                    CurrentYearRegion.beds.in_(beds),
                    and_(
                        CurrentYearRegion.region.in_([region]),
                        CurrentYearRegion.county.in_([county]),
                    ),
                )
            ),
            "columns": ["region", "beds", "avg", "county"],
        },
        "FalseTrue": {
            "query": select(CurrentYearArea).where(
                and_(
                    CurrentYearArea.beds.in_(beds),
                    and_(
                        CurrentYearArea.area.in_([area]),
                        CurrentYearArea.county.in_([county]),
                    ),
                )
            ),
            "columns": ["area", "beds", "avg", "county"],
        },
        "FalseFalse": {
            "query": select(CurrentYearCounty).where(
                and_(
                    CurrentYearCounty.beds.in_(beds),
                    CurrentYearCounty.county.in_([county]),
                )
            ),
            "columns": ["county", "beds", "avg"],
        },
    }

    insert = querying()
    r = insert.general_query(ENTITY_TABLE_MAP[options])
    try:
        response = json.loads(r)
    except TypeError:
        response = {}
    return response
