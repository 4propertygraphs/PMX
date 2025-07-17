import numpy as np
from config.settings import Settings


def calc_z_scores(df):
    standard_deviation = df[Settings.DataColumns.COL_PRICE].std()
    mean = df[Settings.DataColumns.COL_PRICE].mean()
    z_scores = np.array([])
    for x in df[Settings.DataColumns.COL_PRICE]:
        z_scores = np.append(z_scores, ((x - mean) / standard_deviation))
    df[Settings.DataColumns.COL_Z_SCORES] = z_scores
    return df
