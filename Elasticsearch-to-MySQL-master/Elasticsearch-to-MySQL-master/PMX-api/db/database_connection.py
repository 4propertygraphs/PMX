from app.api.core.config.settings import TestingConfig
from sqlalchemy import MetaData, create_engine


class DatabaseConnection:
    def __init__(self, database = TestingConfig.PMX_DATABASE_URI):
        self.database = database
        self.__engine = create_engine(self.database, echo=False)
        self._MetaData = MetaData

    def _create_session(self, query):
        with self.__engine.connect() as conn:
            response = conn.execute(query)
            return response
