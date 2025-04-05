import pandas as pd

skip_slow_tests = True


MONTH_TIME_OF_YEAR_MAPPING = {
    1: 1,
    2: 1,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0,
    11: 1,
    12: 1,
}


def add_date_components_to(
    df: pd.DataFrame, date_column_name: str = "dateComponents"
) -> pd.DataFrame:
    """Uses the date_column_name to create new columns for year, month, weekday, weekend and timeOfYear.
    Weekday is encoded as 0 for Monday, 1 for Tuesday, etc.
    Weekend is encoded as 0 for weekdays and 1 for weekends.
    TimeOfYear is encoded as 1 for winter and 0 for summer.

    Parameters
    ----------
    df : pd.DataFrame

    date_column_name : str, optional
        The column name to use to extract the date values, by default "dateComponents"

    Returns
    -------
    pd.DataFrame
        The original dataframe with the new columns added.
    """

    df = df.copy()
    date_column = df[date_column_name]
    date_column = pd.to_datetime(date_column)
    df["timeOfYear"] = date_column.dt.month.map(
        lambda month: MONTH_TIME_OF_YEAR_MAPPING[month]
    )
    df["year"] = date_column.dt.year
    df["month"] = date_column.dt.month
    df["weekday"] = date_column.dt.day_of_week
    df["weekend"] = df["weekday"].map(lambda weekday: 0 if weekday not in [5, 6] else 1)

    return df


def normalize(x, min_val, max_val):
    x = x - x.min()
    x = x / x.max()
    x = x * (max_val - min_val)
    x = x + min_val
    return x
