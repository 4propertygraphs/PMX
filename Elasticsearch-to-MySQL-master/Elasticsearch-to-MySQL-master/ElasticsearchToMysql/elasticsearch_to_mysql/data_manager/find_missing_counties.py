from config.settings import Settings
from geopy import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut


def locate_county(location, geolocator, attempt=1, max_attempts=50):
    try:
        return geolocator.reverse(location)
    except GeocoderTimedOut | GeocoderServiceError:
        if attempt <= max_attempts:
            return locate_county(location, attempt=attempt + 1)
        return None


def get_counties(data):
    geolocator = Nominatim(user_agent="stefn_mysql")
    df = data[~data[Settings.DataColumns.COL_COUNTY].isin(Settings.General.COUNTY_LIST)]
    for index, row in df.iterrows():
        new_location = locate_county(row[Settings.DataColumns.COL_LOCATION], geolocator)
        for c in Settings.General.COUNTY_LIST:
            if c in new_location.address:
                df.at[index, Settings.DataColumns.COL_COUNTY] = c

    data.update(df)
    return data


def remove_weird_regions(row):
    if (
        any(char.isdigit() for char in row[Settings.DataColumns.COL_REGION])
        or row[Settings.DataColumns.COL_REGION] == Settings.DataColumns.COL_COUNTY
        or row[Settings.DataColumns.COL_REGION] == "County"
    ):
        if "Dublin" not in row[Settings.DataColumns.COL_REGION]:
            return f"{row[Settings.DataColumns.COL_COUNTY]} County"
        return row[Settings.DataColumns.COL_REGION]
    return row[Settings.DataColumns.COL_REGION]
