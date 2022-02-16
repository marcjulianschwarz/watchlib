import numpy as np
from typing import List
import matplotlib.pyplot as plt

# Own imports
from watchlib.analysis.analysis_ecg_utils import bpm_points, hrvs, hrvs_pairwise, split_between_heartbeats
from watchlib.analysis.analysis_utils import slopes_for, slopes_of_slopes_for
from watchlib.utils import ECG, ECGWave


def ecg_distributions(ecgs: List[ECG]):

    bpms = [bpm(ecg) for ecg in ecgs]
    hrvs = [heart_rate_variability(ecg) for ecg in ecgs]
    hrvs_pair = [heart_rate_variability_pairwise(ecg) for ecg in ecgs]

    plt.hist(bpms, bins=35)
    plt.title("BPM distribution")
    plt.show()
    plt.hist(hrvs, bins=35)
    plt.title("HRV distribution")
    plt.xlim(0, 100)
    plt.show()
    plt.hist(hrvs_pair, bins=35)
    plt.title("HRV (pairwise) distribution")
    plt.xlim(0, 100)
    plt.show()


def bpm(ecg: ECG, a: float = 50, d: float = 180, r: float = 3, sample_rate: float = 512, verbose: bool = False) -> int:
    """
        Calculates heart rate (bpm) from ecg data.

        a: heart beat slope amplitude threshold
        d: heart beat distance threshold
        r: slope calculation resolution
        sample_rate: in Hz
        plot: plot ecg, slope and heart beat points
    """

    if verbose:
        print(f"[ECG Analysis]\t\tCalculating bpm for {ecg.name} ...")

    x, y = ecg.x, ecg.y
    points = bpm_points(ecg, a, d, r)
    bpm = len(points) * (60 / (len(y) / sample_rate))

    return bpm


def plot_ecg_with_slopes(ecg: ECG, figsize=(20, 5)):

    x, y = ecg.x, ecg.y
    s = slopes_for(list(zip(x, y)))
    slopes_of_s = slopes_of_slopes_for(list(zip(x, y)))
    points = bpm_points(ecg, slopes=s)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x, y, label="ECG", zorder=0)
    ax.plot(s, label="slope", zorder=1)
    ax.plot(slopes_of_s, label="slope of slopes", zorder=1)

    ax.scatter(x=points, y=[200 for y in range(len(points))],
               c="r", s=60, label="heartbeat", zorder=2)
    ax.legend()
    plt.show()
    return fig


# --------------------------
# HRV
# --------------------------

def heart_rate_variability(ecg: ECG, verbose: bool = False) -> float:
    if verbose:
        print(f"[ECG Analysis]\t\tCalculating hrv for {ecg.name} ...")
    return np.mean(hrvs(ecg))


def heart_rate_variability_pairwise(ecg: ECG, verbose: bool = False) -> float:
    if verbose:
        print(f"[ECG Analysis]\t\tCalculating pairwise hrv for {ecg.name} ...")
    return np.mean(hrvs_pairwise(ecg))


def plot_ecg_hrvs_overlay(ecg: ECG, figsize=(10, 5)):
    splits = split_between_heartbeats(ecg)
    fig, ax = plt.subplots(figsize=figsize)
    for split in splits:
        ax.plot([i for i in range(len(split))], split)
    plt.title(
        f"ECG: {ecg.name} --- HRV: {round(heart_rate_variability_pairwise(ecg),2)}")
    plt.show()

# --------------------------
# ECG WAVES
# --------------------------


def ecg_waves(split) -> List[ECGWave]:
    # TODO: Mark waves in split
    raise NotImplementedError


def interpret_ecg_wave(ecg_wave: ECGWave):
    raise NotImplementedError
