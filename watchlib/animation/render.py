import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['animation.embed_limit'] = 2**128
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib import animation
from datetime import datetime as dt
from typing import Tuple
from abc import ABC, abstractmethod

class HealthAnimation(ABC):

    resolution: float = 0.08
    color_on: str = "elevation"

    interval: int = 10
    fig_size = (5, 5)
    data: pd.DataFrame = None
    meta_data: pd.DataFrame = None

    def __init__(self, data, meta_data=None):
        self.data = data
        self.meta_data = meta_data

    def set_options(self, options):
        for option in options:
            raise NotImplementedError

    def set_interval(self, interval: int):
        self.interval = interval

    def set_fig_size(self, shape: Tuple[int, int]):
        self.fig_size = shape

    def set_color_on(self, color_on: str):
        self.color_on = color_on
    
    def set_resolution(self, resolution: int):
        self.resolution = resolution
    
    @abstractmethod
    def animate(self):
        pass


class WorkoutAnimation(HealthAnimation):

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

        x, y, elevation, s = (x[::strip], y[::strip], elevation[::strip], s[::strip])

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

        fig, ax, lc, segments = self.plot_route()

        def init():
            ax.view_init(10, 0)
            return [fig]

        def update(i):
            lc.set_segments(segments[:i])
            if rotation:
                ax.view_init(10, i/5)
            return [fig]
        
        anim = animation.FuncAnimation(fig, update, init_func=init, frames=len(segments), interval=self.interval, blit=True)
        return anim


class ECGAnimation(HealthAnimation):

    def plot_ecg(self):

        y = self.data["name"]
        x = np.linspace(0, 1, len(y))

        fig, ax = plt.subplots(figsize=(40,5))
        
        ax.plot(x, y)

        if self.meta_data:
            plt.title("Date: " + self.meta_data["Aufzeichnungsdatum"] + "     Classification: " + self.meta_data["Klassifizierung"])

        return fig, ax

    def animate(self):

        fig, ax = self.plot_ecg()

        def init():
            return [fig]

        def update(i):
            return [fig]
    
