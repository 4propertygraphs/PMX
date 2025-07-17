import pandas as pd

from ..database_connection import DatabaseConnection


class querying(DatabaseConnection):
    def general_query(self, entity, return_type=dict) -> dict | pd.DataFrame:
        df = pd.DataFrame(self._create_session(entity["query"]))
        new_index = [i for i in range(len(df.index))]
        df.index = new_index
        if return_type == dict:
            response = df[entity["columns"]].to_json(orient="index")
        elif return_type == pd.DataFrame:
            response = df[entity["columns"]]
        return response
