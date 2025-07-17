import time

from config.settings import Settings
from data_manager.data_manager import DataManager
from data_manager.find_missing_counties import remove_weird_regions
from data_manager.outlier_detection import calc_z_scores
from db.mysql_database_connection import ConnectDatabase

start = time.time()
d = DataManager()
db = ConnectDatabase(Settings.DatabaseSettings.DATABASE_URI)

request = {
            "_source": {
                "include": [
                    Settings.DataColumns.COL_SALE_DATE,
                    Settings.DataColumns.COL_COUNTY,
                    Settings.DataColumns.COL_AREA,
                    Settings.DataColumns.COL_REGION,
                    Settings.DataColumns.COL_RAW_ADDRESS,
                    Settings.DataColumns.COL_PRICE,
                    Settings.DataColumns.COL_DAYS_TO_SELL,
                    Settings.DataColumns.COL_MARKET_TYPE,
                    Settings.DataColumns.COL_PAGE_VIEWS,
                    Settings.DataColumns.COL_BEDS,
                    Settings.DataColumns.COL_BATHS,
                    Settings.DataColumns.COL_ID,
                    Settings.DataColumns.COL_SQR_METRES,
                    Settings.DataColumns.COL_PRICE_PER_SQR_METRES,
                    Settings.DataColumns.COL_STREET,
                    Settings.DataColumns.COL_STREET_NUMBER,
                    Settings.DataColumns.COL_EIR_CODE,
                    Settings.DataColumns.COL_HOUSE_NO_STREET,
                    Settings.DataColumns.COL_NEIGHBORHOOD,
                    Settings.DataColumns.COL_LOCATION,
                ]
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                Settings.DataColumns.COL_MARKET_TYPE: "Residential Rent"
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                Settings.DataColumns.COL_SALE_DATE: {
                                    "gte": d.import_date_from.strftime("%Y-%m-%d"),
                                    "lte": d.import_date_to.strftime("%Y-%m-%d"),
                                }
                            }
                        }
                    ],
                }
            },
        }

d.get_data(request)
condition = (d.df[Settings.DataColumns.COL_PRICE] > d.df.price.quantile(0.05)) & (
    d.df[Settings.DataColumns.COL_PRICE] < d.df.price.quantile(0.95)
)
rent_county, details = d.calculate_running_average(
    d.df.loc[condition]
    .groupby(
        [
            Settings.DataColumns.COL_MONTH_YEAR,
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_ID,
            Settings.DataColumns.COL_AREA,
            Settings.DataColumns.COL_REGION,
        ]
    )[Settings.DataColumns.COL_PRICE]
    .mean()
    .reset_index()
)

last_rent_county, details1 = d.calculate_running_average(
    d.upto_last_year_data_df.loc[condition]
    .groupby(
        [
            Settings.DataColumns.COL_MONTH_YEAR,
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_ID,
            Settings.DataColumns.COL_AREA,
            Settings.DataColumns.COL_REGION,
        ]
    )[Settings.DataColumns.COL_PRICE]
    .mean()
    .reset_index()
)

avg_yoy = d.calculate_percentage(
    rent_county,
    last_rent_county,
    Settings.DataColumns.COL_AVG,
    Settings.DataColumns.COL_AVG_YOY,
)

db.create_table_from_df(rent_county_avg=rent_county[[Settings.DataColumns.COL_COUNTY, Settings.DataColumns.COL_BEDS, Settings.DataColumns.COL_AVG]],
                         rent_yoy=avg_yoy[[Settings.DataColumns.COL_COUNTY, Settings.DataColumns.COL_BEDS, Settings.DataColumns.COL_AVG_YOY]])