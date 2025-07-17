import hashlib

from app.api.core.config.settings import TestingConfig
from db.database_connection import DatabaseConnection
from db.models.tokens import Token
from db.models.users import Users
from fastapi import HTTPException
from sqlalchemy import select
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


def auth_api_key(key, domain):
    hashed_key = get_db_info(domain)
    hash_object = hashlib.sha256()
    hash_object.update(key.encode())
    new_hashed_key = hash_object.hexdigest()

    if hashed_key == new_hashed_key:
        return
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="API key is invalid")


def get_db_info(domain):
    db = DatabaseConnection(database=TestingConfig.PMX_DATABASE_URI)

    users = db._create_session(select(Users).where(Users.domain.in_([domain])))
    users = users.fetchall()
    try:
        token = db._create_session(
            select(Token).where(Token.user_id.in_([users[0][0]]))
        )
        token = token.fetchall()
    except IndexError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Could not find {domain} in database",
        )

    hashed_key = token[0][1]  # hashed key in the database

    return hashed_key
