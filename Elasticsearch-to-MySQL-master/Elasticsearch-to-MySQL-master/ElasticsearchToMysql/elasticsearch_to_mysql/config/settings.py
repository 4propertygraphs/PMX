from datetime import datetime


class Settings:
    class General:
        ROLLING_AVERAGE_WINDOW = (datetime.now().year - 2020) * 12
        COUNTY_LIST = [
            "Antrim",
            "Carlow",
            "Cavan",
            "Clare",
            "Cork",
            "Donegal",
            "Down",
            "Dublin",
            "Fermanagh",
            "Galway",
            "Kerry",
            "Kildare",
            "Kilkenny",
            "Laoighis",
            "Laois",
            "Leitrim",
            "Limerick",
            "Longford",
            "Louth",
            "Mayo",
            "Meath",
            "Monaghan",
            "Offaly",
            "Roscommon",
            "Sligo",
            "Tipperary",
            "Tyrone",
            "Waterford",
            "Westmeath",
            "Wexford",
            "Wicklow",
        ]

    class DatabaseSettings:
        DATABASE_URI = "mysql+pymysql://root@localhost:3306/pmx_report"

    class Testing:
        # when this is true it will remove the weird county but makes the program take a long time
        REMOVE_ROGUE_DATA = True

    class DataColumns:
        COL_MONTH_YEAR = "month_year"
        COL_COUNTY = "county"
        COL_BEDS = "beds"
        COL_PRICE = "price"
        COL_AVG = "avg"
        COL_ID = "id"
        COL_AREA = "area"
        COL_REGION = "region"
        COL_YOY = "yoy"
        COL_SALE_DATE = "saleDate"
        COL_Z_SCORES = "z_scores"
        COL_RAW_ADDRESS = "rawAddress"
        COL_DAYS_TO_SELL = "daysToSell"
        COL_MARKET_TYPE = "marketType"
        COL_PAGE_VIEWS = "pageviews"
        COL_BATHS = "baths"
        COL_LOCATION = "location"
        COL_SQR_METRES = "sqrMetres"
        COL_PRICE_PER_SQR_METRES = "pricePerSqrMetres"
        COL_STREET = "street"
        COL_STREET_NUMBER = "streetNumber"
        COL_EIR_CODE = "eircode"
        COL_HOUSE_NO_STREET = "houseNoStreet"
        COL_NEIGHBORHOOD = "neighborhood"
        COL_ROL_AVG = "rolling_avg"
        COL_AVG_YOY = "avg_yoy"
        
