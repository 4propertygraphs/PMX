from sqlalchemy import MetaData, create_engine


class ConnectDatabase:
    def __init__(self, engine_string: str, echo=True):
        self.engine_string = engine_string
        self.echo = echo
        self.engine = create_engine(self.engine_string, echo=echo)
        self.metadata = MetaData()
        self.con = self.engine.connect()

    def create_table_from_df(self, **kwargs):
        for keys, value in kwargs.items():
            value.to_sql(keys, con=self.engine, if_exists="replace")
