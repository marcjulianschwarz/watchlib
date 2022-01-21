from watchlib.utils import *
from watchlib.analysis.analysis_utils import slopes_for
from typing import List
import numpy as np


def bpm_points(ecg: ECG, a: float = 50, d: float = 180, r: float = 3, slopes=None):

    x, y = ecg.x, ecg.y
    points = list(zip(x, y))
    if slopes is None:
        slopes = slopes_for(points)

    # Start with -distance to count first beat
    bpm_points = [-d]
    for idx, slope in enumerate(slopes):
        if np.abs(slope) > a and np.abs(bpm_points[-1] - x[idx]) > d:
            bpm_points.append(x[idx])
    # Remove first beat (-distance)
    bpm_points = bpm_points[1:]
    return bpm_points


def heartbeat_distances_ms(ecg: ECG) -> List[float]:
    points = bpm_points(ecg)
    distances = []
    for i in range(0, len(points) - 1):
        distances.append((points[i + 1] - points[i]))
    return distances


# --------------------------
# HRV
# --------------------------
def hrvs(ecg: ECG) -> List[float]:
    dist = heartbeat_distances_ms(ecg)
    hrvs = []
    for i in range(0, len(dist) - 1):
        hrvs.append(np.abs((dist[i + 1] - dist[i])))
    return hrvs


def hrvs_pairwise(ecg: ECG) -> List[float]:
    dist = heartbeat_distances_ms(ecg)
    hrvs = []
    for i in range(0, len(dist) - 1):
        for j in range(i, len(dist) - 1):
            hrvs.append(np.abs(dist[i] - dist[j]))
    return hrvs


# --------------------------
# SPLITTING ECG INTO HEARTBEAT SECTIONS
# --------------------------
def split_between_heartbeats(ecg: ECG):
    points = bpm_points(ecg)
    splits = []
    for i in range(0, len(points) - 1):
        splits.append(ecg.data[points[i]:points[i+1]])
    return splits


def split_around_heartbeats(ecg: ECG):
    points = bpm_points(ecg)
    splits_hb = heartbeat_distances_ms(ecg)
    splits = []
    for i in range(1, len(splits_hb) - 2):
        split_half = int(splits_hb[i] / 2)
        start = points[i] - split_half
        end = points[i] + split_half
        splits.append(ecg.data[start:end])
    return splits
