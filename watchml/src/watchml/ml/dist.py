from typing import Callable

import pandas as pd


SeriesDistance = Callable[[pd.Series, pd.Series], pd.Series]


class Distances:
    @staticmethod
    def _manhatten(x, y):
        return abs(x - y)

    @staticmethod
    def _euclidean(x, y):
        return (x - y) ** 2

    @staticmethod
    def euclidean_series(s1: pd.Series, s2: pd.Series) -> pd.Series:
        return Distances._euclidean(s1, s2)

    @staticmethod
    def manhatten_series(s1: pd.Series, s2: pd.Series) -> pd.Series:
        return Distances._manhatten(s1, s2)
