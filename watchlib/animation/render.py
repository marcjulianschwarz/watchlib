from abc import ABC, abstractmethod
from typing import Tuple
from matplotlib import animation
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from watchlib.utils.structs import ECG, WorkoutRoute
from watchlib.animation.config import WorkoutAnimationConfig, ECGAnimationConfig, AnimationConfig
matplotlib.rcParams['animation.embed_limit'] = 2**128


class HealthAnimation(ABC):

    config: AnimationConfig

    def __init__(self, data, config: AnimationConfig=None):
        self.data = data
        if config is not None:
            self.config = config
    
    @abstractmethod
    def animate(self):
        pass


class WorkoutAnimation(HealthAnimation):

    config: WorkoutAnimationConfig =  WorkoutAnimationConfig()

    def __init__(self, data: WorkoutRoute, config: WorkoutAnimationConfig=None):
        super().__init__(data, config)

    def set_config(self, config: WorkoutAnimationConfig):
        self.config = config

    def __project_lonlat_to_xy(self, lon: float, lat: float) -> Tuple[float, float]:
        middle_of_map_lat = np.mean(lat)
        lon = lon*np.abs(np.cos(middle_of_map_lat))
        return lon, lat

    # Calculate line segments for coloring
    def __calculate_segments(self, x: pd.Series, y: pd.Series, elevation: pd.Series) -> np.ndarray:
        points = np.array([x, y, elevation]).T.reshape(-1, 1, 3)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        return segments

    def __data_for_plotting(self) -> Tuple[pd.DataFrame]:
        title = pd.to_datetime(self.data["time"].iloc[0]).date()
        strip = int(1 / self.config.resolution)
        x, y = self.__project_lonlat_to_xy(self.data["lon"], self.data["lat"])
        elevation = self.data["elevation"]
        s = self.data[self.config.color_on]

        x, y, elevation, s = (x[::strip], y[::strip],
                              elevation[::strip], s[::strip])

        return x, y, elevation, s, title

    def plot_route(self):
        x, y, elevation, s, title = self.__data_for_plotting()

        fig = plt.figure(figsize=self.config.fig_size)
        ax = fig.add_subplot(111, projection='3d')

        segments = self.__calculate_segments(x, y, elevation)
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

        ax.text2D(0.05, 0.95, "Color:" + self.config.color_on, transform=ax.transAxes)
        plt.title(title)

        return fig, ax, lc, segments

    def animate(self) -> animation.FuncAnimation:

        print("[Workout Animation]\tAnimating workout route...")

        fig, ax, lc, segments = self.plot_route()

        def init():
            ax.view_init(10, 0)
            return [fig]

        def update(i):
            lc.set_segments(segments[:i])
            if self.config.rotate:
                ax.view_init(10, i/5)
            return [fig]

        ani = animation.FuncAnimation(fig, update, init_func=init, frames=len(
            segments), interval=self.config.interval, blit=True)
        return ani


class ECGAnimation(HealthAnimation):

    config: ECGAnimationConfig = ECGAnimationConfig()

    def __init__(self, data: ECG, config: ECGAnimationConfig=None):
        super().__init__(data, config)

    def set_config(self, config: ECGAnimationConfig):
        self.config = config

    def animate(self):

        l = 1/self.config.length
        ecg: ECG = self.data

        data = ecg.y[:int(len(ecg.y)/l)][::self.config.resolution]
        x_values = ecg.x[:int(len(ecg.y)/l)][::self.config.resolution]

        fig, ax = plt.subplots(figsize=(20, 5))
        ax.set_xlim(-10, len(ecg.y)+10)
        ax.set_ylim(min(data) - 20, max(data)+20)

        # INIT
        y = data[0]
        x = x_values[0]
        line, = ax.plot(x, y)


        def update(i):
            y = data[:i]
            x = x_values[:i]

            line.set_xdata(x)
            line.set_ydata(y)
            return line,

        ani = animation.FuncAnimation(
            fig, update, interval=self.config.interval, blit=True, frames=int(self.config.sample/self.config.resolution*30*self.config.length))

        return ani
