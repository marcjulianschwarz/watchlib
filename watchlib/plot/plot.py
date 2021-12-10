import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from watchlib.analysis.analysis_utils import slopes_for, slopes_of_slopes_for
from watchlib.analysis.analysis_ecg_utils import bpm_points, split_between_heartbeats
from watchlib.utils import WorkoutRoute, ECG
from watchlib.analysis import heart_rate_variability_pairwise

def plot_elevation(route: WorkoutRoute):
    elevation = route["elevation"]
    time = route["time"]

    fig, ax = plt.subplots(figsize=(15, 5))

    ax.plot(time, elevation)

    plt.xticks([1,2,3,4])
        
    ax.grid(True)

    plt.title("Elevation for: " + route.name)
    plt.show()

def plot_side(route: WorkoutRoute):
    raise NotImplementedError

def plot_hrv(ecg: ECG):
    splits = split_between_heartbeats(ecg)
    for s in splits:    
        x = [xx for xx in range(0, len(s["name"]))]
        y = s["name"]
        plt.plot(x, y)
    plt.title(f"ECG: {ecg.name} --- HRV: {round(heart_rate_variability_pairwise(ecg),2)}")
    plt.show()

def plot_ecg(ecg: ECG):

    x, y = ecg.x, ecg.y
    s = slopes_for(list(zip(x, y)))
    slopes_of_s = slopes_of_slopes_for(list(zip(x, y)))
    points = bpm_points(ecg, slopes=s)

    fig, ax = plt.subplots(figsize=(20, 5))
    ax.plot(x, y, label="ECG", zorder=0)
    ax.plot(s, label="slope", zorder=1)
    ax.plot(slopes_of_s, label="slope of slopes", zorder=1)
    
    ax.scatter(x=points, y=[200 for y in range(len(points))], c="r", s=60, label="heartbeat", zorder=2)
    ax.legend()
    plt.show()