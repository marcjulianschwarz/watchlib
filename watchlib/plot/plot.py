import matplotlib.pyplot as plt
from typing import List

# Own imports
from watchlib.utils import WorkoutRoute, ECG


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
    if _from is None:
        _from = 0
    if _to is None:
        _to = len(ecg.x)
    if title is None:
        title = ecg.name

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(ecg.x[_from:_to], ecg.y[_from:_to], c=c)
    plt.title(title)
    plt.show()

    if return_fig:
        return fig
