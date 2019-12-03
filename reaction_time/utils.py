import datetime
import pandas as pd


def calculate_time_delta_ms(start_dt, end_dt):
    """ Calculate the time delta in milliseconds between datetime objects

    Parameters
    ----------
    start_dt : datetime.datetime
        Starting datetime
    end_dt: datetime.datetime
        Ending datetime

    Returns
    -------
    float
        Time delta in milliseconds

    """
    diff = end_dt - start_dt
    millis = diff.days * 24 * 60 * 60 * 1000
    millis += diff.seconds * 1000
    millis += diff.microseconds / 1000
    return millis


def avg_time_scores_by(df, by, metrics=None, sort_by="time_ms"):
    """ Helper function for averaging time and score metrics by a field

    Parameters
    ----------
    df: pd.DataFrame
    by: string or list
        group by statement for pandas
    metrics: list, optional
        Metrics to calculate
    sort_by: string, optional
        Field to sort by (sorts in descending order)

    Returns
    -------
    pd.DataFrame:
        Summarized dataframe

    """

    if metrics is None:
        metrics = ["time_ms", "correct"]

    return (
        df.groupby(by)[metrics]
        .mean()
        .sort_values(sort_by, ascending=False)
        .reset_index()
    )

