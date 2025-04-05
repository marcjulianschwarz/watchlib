from typing import List
from typing import Protocol

import pandas as pd
from watchml.data import WorkoutRoute

from .dist import Distances
from .dist import SeriesDistance


class NNIndex(Protocol):
    def nns(self, t: int, n: int = 3) -> List[int]:
        ...


class NN(Protocol):
    def build_index(self) -> NNIndex:
        ...


class AnnoyNNIndex(NNIndex):
    from annoy import AnnoyIndex

    def __init__(self, index: AnnoyIndex):
        self.index = index

    def nns(self, t, n=3) -> List[int]:
        return self.index.get_nns_by_item(t, n)


class AnnoyNN(NN):
    def __init__(self, tracks: List[WorkoutRoute]):
        self.tracks = tracks

    def build_index(self) -> NNIndex:
        from annoy import AnnoyIndex

        index = AnnoyIndex(2, metric="euclidean")
        for i, track in enumerate(self.tracks):
            index.add_item(i, [track.lon.mean(), track.lat.mean()])
        index.build(100)
        return AnnoyNNIndex(index)


class BaselineNNIndex(NNIndex):
    def __init__(self, dists):
        self.dists = dists

    def nns(self, t, n=3) -> List[int]:
        vals = []
        for k, v in self.dists.items():
            i, _ = k
            if i == t:
                vals.append(v)
        return pd.DataFrame(vals).sort_values(by=0).index.values[:n]


class BaselineNN(NN):
    def __init__(self, tracks: List[WorkoutRoute]):
        self.tracks = tracks

    def track_dist(
        self, track1: WorkoutRoute, track2: WorkoutRoute, dist: SeriesDistance
    ) -> float:
        df1 = track1.track_df
        df2 = track2.track_df
        return (
            dist(df1["lon"], df2["lon"]).fillna(0.01).sum()
            + dist(df1["lat"], df2["lat"]).fillna(0.01).sum()
        )

    def build_index(self, dist=Distances.euclidean_series) -> BaselineNNIndex:
        dists = {}
        for i, track1 in enumerate(self.tracks):
            for j, track2 in enumerate(self.tracks):
                d = self.track_dist(track1, track2, dist)
                dists[(i, j)] = d
        return BaselineNNIndex(dists)
