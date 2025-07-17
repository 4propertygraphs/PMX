import ast
import json
import warnings
from datetime import datetime, timedelta

import pandas as pd
import requests
from config.settings import Settings
from data_manager.calculation_handler import CalculationHandler
from data_manager.find_missing_counties import get_counties
from dateutil.relativedelta import relativedelta


warnings.filterwarnings("ignore")


class DataManager(CalculationHandler):
    def __init__(self):
        self.upto_last_year_data_df = None
        self.df = None
        self.date_on = datetime.today()
        self.import_date_from = self.set_dates()[0]
        self.import_date_to = self.set_dates()[1]
        self.last_year_end_date = self.set_dates()[2]
        print(self.import_date_from, self.import_date_to)

    def get_data(self, data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer "
            "eyJraWQiOiItMTU5OTYzOTIzOSIsIng1dCI6InNoZllfa0J4ajJLOWtuTThaa1BKeDFTM2o5NCIsImprdSI6Imh0dHA6Ly9zZWN1cml0eS5wcm9kLmdrZS5pcHBpLmlvLzRwbS9vYXV0aC92Mi9vYXV0aC1hbm9ueW1vdXMvandrcyIsImFsZyI6IlJTMjU2In0.eyJqdGkiOiIwNWNhZTc5NS1lYzZiLTRjNTYtYjkyYy0xMzFlZWJmN2YwMmYiLCJkZWxlZ2F0aW9uSWQiOiJjMmQzOTVkNS1iMTVlLTRiMDEtYjM0YS04Y2QwOTY2Zjc5ZTQiLCJleHAiOjE2OTY1OTA0NTcsIm5iZiI6MTY2NTA1NDQ1Nywic2NvcGUiOiJlbGFzdGljX3NlYXJjaCIsImlzcyI6InNlY3VyaXR5LnByb2QuZ2tlLmlwcGkuaW8iLCJzdWIiOiJpcHBpIiwiYXVkIjoiaHR0cHM6Ly9pcHBpYXBpLjRwcm9wZXJ0eS5jb20vIiwiaWF0IjoxNjY1MDU0NDU3LCJwdXJwb3NlIjoiYWNjZXNzX3Rva2VuIn0.nBVo2mF2I-fbJXDQhhZ0jofSuHoxF9z8p4NhoaRGeUcRHuu1zixtIatO4TbPSoTcq5op6Jp352TViFBDDoRJNRm9lsyFHeKaWafiJ5C2ngrbE5DdQJiOP2wCT33_d-qFfbMPz-HVSMg6mDrWJ0RV-yYtdrGCLXxAWl122K-mfXGQIipt_P6gDbOhK0TIbc02HDxwouq3Hj_hJvFSFiWFBYwnDRi4wmYRXsnvavRoRB3ld5p_1orcdZGyWYDsf8ZmTDY8mVEU09LGnSkffldiRBMxr82y3SNr2F8MtyyicLaIkPNpR_TyfXIE7WwR0K-HT0SzHj3bECG5gvJaVkJPQ",
        }

        # get the total amount of all records in the elasticsearch database and use that to get everything
        dt = json.dumps(data)
        response = requests.get(
            "https://elasticsearch.prod.ippi.io:9200/_search",
            data=dt,
            headers=headers,
            timeout=40,
        )
        print("first request send and received")
        toal_records = json.loads(response.text)["hits"]["total"]

        response1 = requests.get(
            f"https://elasticsearch.prod.ippi.io:9200/_search?size={toal_records}",
            data=dt,
            headers=headers,
            timeout=40,
        )
        print("second request send and received")
        result1 = json.loads(response1.text)["hits"]["hits"]
        raw_df = pd.json_normalize(result1)
        # rename columns of the data
        print("Changing column names")
        mystring = "{"
        for i in data["_source"]["include"]:
            mystring = mystring + "'" + f"_source.{i}" + "':'" + i + "',"

        raw_df.rename(columns=ast.literal_eval(mystring + "}"), inplace=True)
        self.__clean_data(raw_df, data)
        if Settings.Testing.REMOVE_ROGUE_DATA:
            self.df = get_counties(self.df)
        self.upto_last_year_data_df = self.df.loc[
            (self.df[Settings.DataColumns.COL_SALE_DATE] <= self.last_year_end_date)
        ]

    def set_dates(self):
        print("setting Dates")
        years_ago = self.date_on - relativedelta(years=3)
        last_year = self.date_on - relativedelta(years=1)
        import_date_from = years_ago.replace(day=1)
        next_month = self.date_on.replace(day=28) + timedelta(days=4)
        import_date_to = next_month - timedelta(
            days=next_month.day
        )  # date_on.replace(day=1) - timedelta(days=1)
        next_month = last_year.replace(day=28) + timedelta(days=4)
        last_year_end_date = next_month - timedelta(days=next_month.day)
        print("Done")
        return [import_date_from, import_date_to, last_year_end_date]

    def __clean_data(self, raw_df, data):
        print("cleaning data")
        raw_df[Settings.DataColumns.COL_SALE_DATE] = pd.to_datetime(
            raw_df[Settings.DataColumns.COL_SALE_DATE]
        )
        raw_df[Settings.DataColumns.COL_PRICE] = pd.to_numeric(
            raw_df[Settings.DataColumns.COL_PRICE]
        )
        raw_df[Settings.DataColumns.COL_BEDS] = pd.to_numeric(
            raw_df[Settings.DataColumns.COL_BEDS]
        )
        raw_df.loc[
            raw_df[Settings.DataColumns.COL_BEDS] > 5, Settings.DataColumns.COL_BEDS
        ] = 6

        filt = (raw_df[Settings.DataColumns.COL_BEDS].notnull()) & raw_df[
            Settings.DataColumns.COL_BEDS
        ] != 0
        df = raw_df[data["_source"]["include"]].loc[filt]

        df[Settings.DataColumns.COL_MONTH_YEAR] = df[
            Settings.DataColumns.COL_SALE_DATE
        ].dt.to_period("M")

        df = df.drop_duplicates(subset=[Settings.DataColumns.COL_ID])
        print("Data cleaned")
        self.df = df
