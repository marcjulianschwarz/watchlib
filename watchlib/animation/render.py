from abc import ABC, abstractmethod
from typing import Tuple
from datetime import datetime as dt
from matplotlib import animation
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from watchlib.utils.structs import WorkoutRoute
matplotlib.rcParams['animation.embed_limit'] = 2**128


class HealthAnimation(ABC):

    resolution: float = 0.08

    interval: int = 10
    fig_size = (5, 5)

    def __init__(self, data):
        self.data = data

    def set_options(self, options):
        for option in options:
            raise NotImplementedError

    def set_interval(self, interval: int):
        self.interval = interval

    def set_fig_size(self, shape: Tuple[int, int]):
        self.fig_size = shape

    def set_resolution(self, resolution: int):
        self.resolution = resolution

    @abstractmethod
    def animate(self):
        pass


class WorkoutAnimation(HealthAnimation):

    color_on: str = "elevation"

    def set_color_on(self, color_on: str):
        self.color_on = color_on

    # Project latitude and longitude to x and y coordinate
    def project_to_xy(self, lon: float, lat: float) -> Tuple[float, float]:
        middle_of_map_lat = np.mean(lat)
        lon = lon*np.abs(np.cos(middle_of_map_lat))
        return lon, lat

    # Calculate line segments for coloring
    def calculate_segments(self, x: pd.Series, y: pd.Series, elevation: pd.Series) -> np.ndarray:
        points = np.array([x, y, elevation]).T.reshape(-1, 1, 3)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        return segments

    def data_for_plotting(self) -> Tuple[pd.DataFrame]:
        title = pd.to_datetime(self.data["time"].iloc[0]).date()
        strip = int(1 / self.resolution)
        x, y = self.project_to_xy(self.data["lon"], self.data["lat"])
        elevation = self.data["elevation"]
        s = self.data[self.color_on]

        x, y, elevation, s = (x[::strip], y[::strip],
                              elevation[::strip], s[::strip])

        return x, y, elevation, s, title

    def plot_route(self):
        x, y, elevation, s, title = self.data_for_plotting()

        fig = plt.figure(figsize=self.fig_size)
        ax = fig.add_subplot(111, projection='3d')

        segments = self.calculate_segments(x, y, elevation)
        norm = plt.Normalize(s.min(), s.max())
        lc = Line3DCollection(segments, cmap="viridis", norm=norm)
        lc.set_array(s)
        line = ax.add_collection3d(lc, zs=elevation, zdir="z")

        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        ax.set_zlim(elevation.min() - 30, elevation.max() + 30)

        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_zlabel("Elevation")

        ax.text2D(0.05, 0.95, "Color:" + self.color_on, transform=ax.transAxes)
        plt.title(title)

        return fig, ax, lc, segments

    def animate(self, rotation: bool = True):

        print("[Workout Animation]\tAnimating workout route...")

        fig, ax, lc, segments = self.plot_route()

        def init():
            ax.view_init(10, 0)
            return [fig]

        def update(i):
            lc.set_segments(segments[:i])
            if rotation:
                ax.view_init(10, i/5)
            return [fig]

        ani = animation.FuncAnimation(fig, update, init_func=init, frames=len(
            segments), interval=self.interval, blit=True)
        return ani


class ECGAnimation(HealthAnimation):

    def animate(self, length=1, res=6, speed=1, sample=512):

        l = 1/length
        ecg: pd.DataFrame = self.data

        data = ecg["name"].iloc[:int(len(ecg["name"])/l)].iloc[::res]
        x_values = [xx for xx in range(
            0, len(ecg["name"].iloc[:int(len(ecg["name"])/l)]))][::res]

        fig, ax = plt.subplots(figsize=(20, 5))
        ax.set_xlim(-10, len(ecg["name"])+10)
        ax.set_ylim(data.min() - 20, data.max()+20)

        # INIT
        y = data.iloc[0]
        x = x_values[0]
        line, = ax.plot(x, y)

        if self.data.meta_data:
            plt.title("Date: " + self.data.meta_data["Aufzeichnungsdatum"] +
                      "     Classification: " + self.data.meta_data["Klassifizierung"])

        def update(i):
            y = data.iloc[:i]
            x = x_values[:i]

            line.set_xdata(x)
            line.set_ydata(y)
            return line,

        ani = animation.FuncAnimation(
            fig, update, interval=1000/(sample/res)/speed, blit=True, frames=int(sample/res*30*length))

        return ani
