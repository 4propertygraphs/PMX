import time

from config.settings import Settings
from data_manager.data_manager import DataManager
from data_manager.find_missing_counties import remove_weird_regions
from data_manager.outlier_detection import calc_z_scores
from db.mysql_database_connection import ConnectDatabase

start = time.time()
d = DataManager()

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
                                Settings.DataColumns.COL_MARKET_TYPE: "Residential Sale"
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
raw_data = d.df
address_data = d.df[
    [
        Settings.DataColumns.COL_COUNTY,
        Settings.DataColumns.COL_REGION,
        Settings.DataColumns.COL_AREA,
        Settings.DataColumns.COL_PRICE,
        Settings.DataColumns.COL_BEDS,
        Settings.DataColumns.COL_RAW_ADDRESS,
        Settings.DataColumns.COL_SQR_METRES,
        Settings.DataColumns.COL_PRICE_PER_SQR_METRES,
        Settings.DataColumns.COL_STREET,
        Settings.DataColumns.COL_STREET_NUMBER,
        Settings.DataColumns.COL_EIR_CODE,
        Settings.DataColumns.COL_HOUSE_NO_STREET,
        Settings.DataColumns.COL_NEIGHBORHOOD,
        Settings.DataColumns.COL_SALE_DATE,
        Settings.DataColumns.COL_LOCATION,
    ]
]

# Calculating z scores to see what data has a lot of outliers

outliers_current_year = calc_z_scores(
    d.df[
        [
            Settings.DataColumns.COL_PRICE,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_MONTH_YEAR,
        ]
    ]
)
outliers_last_year = calc_z_scores(
    d.df[
        [
            Settings.DataColumns.COL_PRICE,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_MONTH_YEAR,
        ]
    ]
)

# Calculate the average and yoy of counties
condition = (d.df[Settings.DataColumns.COL_PRICE] > d.df.price.quantile(0.05)) & (
    d.df[Settings.DataColumns.COL_PRICE] < d.df.price.quantile(0.95)
)
current_year_df, details = d.calculate_running_average(
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

last_year_df, details1 = d.calculate_running_average(
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

pmx_yoy = d.calculate_percentage(current_year_df, last_year_df)
avg_yoy = d.calculate_percentage(
    current_year_df,
    last_year_df,
    Settings.DataColumns.COL_AVG,
    Settings.DataColumns.COL_AVG_YOY,
)
# Calculate the yoy and average of region
region_current_year = details
region_last_year = details1
region_current_year = region_current_year.dropna()
region_last_year = region_last_year.dropna()

# find regions that are not correct and change them to something correct
region_current_year[Settings.DataColumns.COL_REGION] = region_current_year.apply(
    remove_weird_regions, axis=1
)
region_last_year[Settings.DataColumns.COL_REGION] = region_last_year.apply(
    remove_weird_regions, axis=1
)

# applying standard deviation
condition_current = (
    region_current_year[Settings.DataColumns.COL_PRICE]
    > region_current_year.price.quantile(0.05)
) & (
    region_current_year[Settings.DataColumns.COL_PRICE]
    < region_current_year.price.quantile(0.95)
)
condition_last = (
    region_last_year[Settings.DataColumns.COL_PRICE]
    > region_last_year.price.quantile(0.05)
) & (
    region_last_year[Settings.DataColumns.COL_PRICE]
    < region_last_year.price.quantile(0.95)
)
region_current_year = region_current_year.loc[condition_current]
region_last_year = region_last_year.loc[condition_last]

region_current_year, region_details_current = d.calculate_running_average(
    region_current_year, Settings.DataColumns.COL_REGION, rolling_window=72
)
region_last_year, region_details_last = d.calculate_running_average(
    region_last_year, Settings.DataColumns.COL_REGION, rolling_window=72
)
region_yoy = d.calculate_percentage(region_current_year, region_last_year)


# Calculate the yoy and average of area
area_current_year = details
area_last_year = details1

area_current_year, area_details_current = d.calculate_running_average(
    area_current_year, Settings.DataColumns.COL_AREA, rolling_window=72
)
area_last_year, area_details_last = d.calculate_running_average(
    area_last_year, Settings.DataColumns.COL_AREA, rolling_window=72
)


area_yoy = d.calculate_percentage(area_current_year, area_last_year)

area_yoy = area_yoy[
    area_yoy[Settings.DataColumns.COL_COUNTY].isin(Settings.General.COUNTY_LIST)
]

area_yoy = area_yoy.loc[area_yoy[Settings.DataColumns.COL_AREA].notnull()]
area_current_year = area_current_year.loc[
    area_current_year[Settings.DataColumns.COL_AREA].notnull()
]


db = ConnectDatabase(Settings.DatabaseSettings.DATABASE_URI)
db.create_table_from_df(
    raw_data=raw_data,
    county_yoy_rolling=pmx_yoy[
        [
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_YOY,
        ]
    ],
    county_yoy_avg=avg_yoy[
        [
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_AVG_YOY,
        ]
    ],
    county_avg=current_year_df[
        [
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_AVG,
        ]
    ],
    county_rolling_avg=current_year_df[
        [
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_ROL_AVG,
        ]
    ],
    outliers_scores_current_year=outliers_current_year,
    outliers_last_year=outliers_last_year,
    region_rolling_avg=region_current_year[
        [
            Settings.DataColumns.COL_ROL_AVG,
            Settings.DataColumns.COL_REGION,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
        ]
    ],
    region_avg=region_current_year[
        [
            Settings.DataColumns.COL_AVG,
            Settings.DataColumns.COL_REGION,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
        ]
    ],
    region_yoy=region_yoy[
        [
            Settings.DataColumns.COL_YOY,
            Settings.DataColumns.COL_REGION,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
        ]
    ],
    area_avg=area_current_year[
        [
            Settings.DataColumns.COL_AVG,
            Settings.DataColumns.COL_AREA,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_REGION,
        ]
    ],
    area_rolling_avg=area_current_year[
        [
            Settings.DataColumns.COL_ROL_AVG,
            Settings.DataColumns.COL_AREA,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_REGION,
        ]
    ],
    area_yoy=area_yoy[
        [
            Settings.DataColumns.COL_YOY,
            Settings.DataColumns.COL_AREA,
            Settings.DataColumns.COL_BEDS,
            Settings.DataColumns.COL_COUNTY,
            Settings.DataColumns.COL_REGION,
        ]
    ],
)

db.create_table_from_df(address_data=address_data)
end = time.time()
print(end - start)
