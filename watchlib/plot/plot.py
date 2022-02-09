import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from watchlib.analysis.analysis_utils import slopes_for, slopes_of_slopes_for
from watchlib.analysis.analysis_ecg_utils import bpm_points, split_between_heartbeats
from watchlib.utils import WorkoutRoute, ECG
from watchlib.analysis import heart_rate_variability_pairwise, heart_rate_variability


def plot_elevation(route: WorkoutRoute):
    elevation = route["elevation"]
    time = route["time"]

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(time, elevation)
    plt.xticks([1, 2, 3, 4])
    ax.grid(True)
    plt.title("Elevation for: " + route.name)
    plt.show()


def plot_side(route: WorkoutRoute):
    raise NotImplementedError


def plot_ecg(ecg: ECG, _from=None, _to=None, figsize=(20, 5), c="b", title=None, return_fig=False):
    if _from is None: _from = 0
    if _to is None: _to = len(ecg.x)
    if title is None: title = ecg.name

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(ecg.x[_from:_to], ecg.y[_from:_to], c=c)
    plt.title(title)
    plt.show()

    if return_fig:
        return fig


def plot_ecg_with_slopes(ecg: ECG, figsize=(20,5)):

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


def plot_ecg_hrvs_overlay(ecg: ECG, figsize=(10,5)):
    splits = split_between_heartbeats(ecg)
    fig, ax = plt.subplots(figsize=figsize)
    for split in splits:
        ax.plot([i for i in range(len(split))], split)    
    plt.title(
        f"ECG: {ecg.name} --- HRV: {round(heart_rate_variability_pairwise(ecg),2)}")
    plt.show()
