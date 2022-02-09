import numpy as np
from watchlib.utils import ECG, ECGWave
from typing import List

from watchlib.analysis.analysis_ecg_utils import bpm_points, hrvs, hrvs_pairwise

from sklearn.decomposition import PCA
from annoy import AnnoyIndex



def bpm(ecg: ECG, a: float = 50, d: float = 180, r: float = 3, sample_rate: float = 512, plot: bool = False) -> int:
    """
        Calculates heart rate (bpm) from ecg data.

        a: heart beat slope amplitude threshold
        d: heart beat distance threshold
        r: slope calculation resolution
        sample_rate: in Hz
        plot: plot ecg, slope and heart beat points
    """

    print(f"[ECG Analysis]\t\tCalculating bpm for {ecg.name} ...")

    x, y = ecg.x, ecg.y
    points = bpm_points(ecg, a, d, r)
    bpm = len(points) * (60 / (len(y) / sample_rate))

    return bpm


# --------------------------
# HRV
# --------------------------

def heart_rate_variability(ecg: ECG) -> float:
    print(f"[ECG Analysis]\t\tCalculating hrv for {ecg.name} ...")
    return np.mean(hrvs(ecg))


def heart_rate_variability_pairwise(ecg: ECG) -> float:
    print(f"[ECG Analysis]\t\tCalculating pairwise hrv for {ecg.name} ...")
    return np.mean(hrvs_pairwise(ecg))

# --------------------------
# ECG WAVES
# --------------------------


def ecg_waves(split) -> List[ECGWave]:
    # TODO: Mark waves in split
    raise NotImplementedError


def interpret_ecg_wave(ecg_wave: ECGWave):
    raise NotImplementedError


def annoy_with_pca(ecgs: List[ECG], trees=10000) -> AnnoyIndex:

    
    min_features = min([len(ecg.y) for ecg in ecgs])
    components = min(len(ecgs), min_features)

    ecg_data = [ecg.y[:min_features] for ecg in ecgs]

    pca = PCA(n_components=components)
    pca.fit(ecg_data) 

    ecgs_transformed = pca.transform(ecg_data)

    t = AnnoyIndex(components, metric="angular")
    for i, ecg in enumerate(ecgs_transformed):
        t.add_item(i, ecg)
    t.build(trees)

    return t


def annoy(ecgs: List[ECG], _from=None, _to=None, trees=10000) -> AnnoyIndex:

    min_features = min([len(ecg.y) for ecg in ecgs])
    
    if _from is None: _from = 0
    if _to is None: _to = min_features
    features = _to - _from

    ecg_data = [ecg.y[_from:_to] for ecg in ecgs]

    t = AnnoyIndex(features, metric="angular")
    for i, ecg in enumerate(ecg_data):
        t.add_item(i, ecg)
    t.build(trees)

    return t


