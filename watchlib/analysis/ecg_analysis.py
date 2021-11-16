import typing
import numpy as np
import matplotlib.pyplot as plt
from watchlib.utils import ECG, ECGWave
from typing import List


def analyse_ecg(ecg: ECG, a: float = 50, d: float = 180, r:float = 3, sample_rate:int = 512, plot: bool = False) -> int:
        """
            Calculates heart rate (bpm) from ecg data.

            a: heart beat slope amplitude threshold
            d: heart beat distance threshold
            r: slope calculation resolution
            sample_rate: in Hz
            plot: plot ecg, slope and heart beat points
        """
        
        x = [xx for xx in range(0, len(ecg["name"]))]
        y = ecg["name"]

        length_of_ecg = len(y) / sample_rate 

        def slope_between(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            slope = (y2 - y1)/(x2 - x1)
            return slope

        slopes = []
        for xx in x:
            if xx + r < len(y):
                point1 = (xx, y.iloc[xx])
                point2 = (xx+r, y.iloc[xx+r])
                slopes.append(slope_between(point1, point2))

        # Start with -distance to count first beat
        bpm_points = [-d]
        for idx, slope in enumerate(slopes):
            if np.abs(slope) > a and np.abs(bpm_points[-1] - x[idx]) > d:
                bpm_points.append(x[idx])
        # Remove first beat (-distance)
        bpm_points = bpm_points[1:]

        bpm = len(bpm_points) * 60 / length_of_ecg
    
        if plot:
            fig, ax = plt.subplots(figsize=(20, 5))
            ax.plot(x, y, label="ECG", zorder=0)
            ax.plot(slopes, label="slope", zorder=1)
            ax.scatter(x=bpm_points, y=[200 for y in range(len(bpm_points))], c="r", s=60, label="heartbeat", zorder=2)
            ax.legend()
            plt.show()
            return bpm, fig

        return bpm, bpm_points

def bpm_from_ecg(ecg: ECG, a: float = 50, d: float = 180, r:float = 3, sample_rate:int = 512, plot: bool = False) -> int:
    data = analyse_ecg(ecg, a, d, r, sample_rate, plot)
    return data[0]


def heartbeat_time_distance(ecg: ECG) -> List[float]:
    bpm, bpm_points = analyse_ecg(ecg)
    distances = []
    for i in range(0, len(bpm_points) - 1):
        distances.append((bpm_points[i + 1] - bpm_points [i]))
    return distances


def hrvs(ecg: ECG) -> List[float]:
    dist = heartbeat_time_distance(ecg)
    hrvs = []
    for i in range(0, len(dist) - 1):
        hrvs.append(np.abs((dist[i + 1] - dist[i])))
    return hrvs


def heart_rate_variability(ecg: ECG) -> float:
    return np.mean(hrvs(ecg))


def split_between_heartbeats(ecg: ECG):
    bpm, bpm_points = analyse_ecg(ecg)
    splits = []
    for i in range(0, len(bpm_points) - 1):
        splits.append(ecg.data.iloc[bpm_points[i]:bpm_points[i+1]])
    return splits


def ecg_waves(ecg: ECG) -> List[ECGWave]:
    raise NotImplementedError


def interpret_ecg_wave(ecg_wave: ECGWave):
    raise NotImplementedError


