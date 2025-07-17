import numpy as np
import pandas as pd
from config.settings import Settings


class CalculationHandler:
    # Calculate the moving average
    @staticmethod
    def calculate_running_average(
        data, entity=Settings.DataColumns.COL_COUNTY, rolling_window=None, rolling=True
    ):
        if rolling_window is None:
            rolling_window = Settings.General.ROLLING_AVERAGE_WINDOW
        dframe = data.sort_values(
            [
                f"{entity}",
                Settings.DataColumns.COL_BEDS,
                Settings.DataColumns.COL_MONTH_YEAR,
            ]
        )
        new_df = pd.DataFrame()
        current_year_df = pd.DataFrame()
        for county in dframe[f"{entity}"].unique():
            for beds in dframe[Settings.DataColumns.COL_BEDS].unique():
                dff = dframe.loc[
                    (dframe[f"{entity}"] == county)
                    & (dframe[Settings.DataColumns.COL_BEDS] == beds)
                ].sort_values([Settings.DataColumns.COL_MONTH_YEAR])
                if not dff.empty:
                    #  This calculates the rolling average for every county per bed.
                    dff[Settings.DataColumns.COL_ROL_AVG] = (
                        dff[Settings.DataColumns.COL_PRICE]
                        .rolling(rolling_window, min_periods=1)
                        .mean()
                    )

                    dff[Settings.DataColumns.COL_AVG] = dff[
                        Settings.DataColumns.COL_PRICE
                    ].mean()
                    new_df = pd.concat([new_df, dff], ignore_index=True)

                    current_year_df = pd.concat(
                        [
                            current_year_df,
                            dff.iloc[[-1]],
                        ],
                        ignore_index=True,
                    )

                else:
                    # Create a new row with zero average value

                    new_row = pd.DataFrame(
                        [[None, county, beds, None, 0, None, None, None]],
                        columns=[
                            Settings.DataColumns.COL_MONTH_YEAR,
                            Settings.DataColumns.COL_COUNTY,
                            Settings.DataColumns.COL_BEDS,
                            Settings.DataColumns.COL_PRICE,
                            Settings.DataColumns.COL_AVG,
                            Settings.DataColumns.COL_ID,
                            Settings.DataColumns.COL_AREA,
                            Settings.DataColumns.COL_REGION,
                        ],
                    )
                    new_df = pd.concat([new_df, new_row], ignore_index=True)
                    current_year_df = pd.concat(
                        [current_year_df, new_row], ignore_index=True
                    )
        return current_year_df, new_df

    @staticmethod
    def calculate_percentage(
        data_now,
        data_last_year,
        entity=Settings.DataColumns.COL_ROL_AVG,
        output_name=Settings.DataColumns.COL_YOY,
    ):
        data_now[output_name] = (
            (data_now[entity] - data_last_year[entity]) / data_last_year[entity]
        ) * 100
        data_now[output_name] = pd.to_numeric(
            data_now[output_name], errors="coerce"
        ).replace([np.nan, np.inf], 0)
        return data_now
