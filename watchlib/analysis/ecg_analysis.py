import typing
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib import split
from watchlib.utils import ECG, ECGWave
from typing import List

from watchlib.analysis.analysis_ecg_utils import bpm_points, hrvs, hrvs_pairwise


def bpm(ecg: ECG, a: float = 50, d: float = 180, r: float = 3, sample_rate: float = 512, plot: bool = False) -> int:
    """
        Calculates heart rate (bpm) from ecg data.

        a: heart beat slope amplitude threshold
        d: heart beat distance threshold
        r: slope calculation resolution
        sample_rate: in Hz
        plot: plot ecg, slope and heart beat points
    """

    print(f"[ECG Analysis]\tCalculating bpm for {ecg.name} ...")

    x, y = ecg.x, ecg.y
    points = bpm_points(ecg, a, d, r)
    bpm = len(points) * (60 / (len(y) / sample_rate))

    return bpm


# --------------------------
# HRV
# --------------------------

def heart_rate_variability(ecg: ECG) -> float:
    print(f"Calculating hrv for {ecg.name} ...")
    return np.mean(hrvs(ecg))


def heart_rate_variability_pairwise(ecg: ECG) -> float:
    print(f"Calculating pairwise hrv for {ecg.name} ...")
    return np.mean(hrvs_pairwise(ecg))

# --------------------------
# ECG WAVES
# --------------------------


def ecg_waves(split) -> List[ECGWave]:
    # TODO: Mark waves in split
    raise NotImplementedError


def interpret_ecg_wave(ecg_wave: ECGWave):
    raise NotImplementedError
