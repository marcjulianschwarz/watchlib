import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from watchlib.utils import WorkoutRoute, ECG
from watchlib.analysis import split_between_heartbeats, heart_rate_variability_pairwise

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