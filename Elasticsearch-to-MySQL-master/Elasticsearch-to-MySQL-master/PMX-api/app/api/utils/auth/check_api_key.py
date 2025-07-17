import hashlib

from app.api.core.config.settings import TestingConfig
from db.database_connection import DatabaseConnection
from db.models.tokens import Token
from db.models.users import Users
from fastapi import HTTPException
from sqlalchemy import select
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


def auth_api_key(key, domain):
    # Skip auth for now - just return
    return


def get_db_info(domain):
    # Skip auth for now
    return "dummy"
