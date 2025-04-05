from abc import ABC
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import animation
from mpl_toolkits.mplot3d.art3d import Line3DCollection


class AnimationConfig(ABC):
    def __init__(
        self, interval: int, fig_size: Tuple[int, int], resolution: float
    ) -> None:
        """Config for the animation

        Parameters
        ----------
        interval : int
            _description_
        fig_size : Tuple[int, int]
            Figure size of the animation (width, height)
        resolution : float
            Resolution of the animation. 1.0 means every point is plotted, 0.5 means every second point is plotted, etc.
        """
        self.interval = interval
        self.fig_size = fig_size
        self.resolution = resolution

    def set_interval(self, interval: int):
        self.interval = interval

    def set_fig_size(self, shape: Tuple[int, int]):
        self.fig_size = shape

    def set_resolution(self, resolution: int):
        self.resolution = resolution


class WorkoutAnimationConfig(AnimationConfig):
    def __init__(
        self,
        interval: int = 25,
        fig_size: Tuple[int, int] = (10, 10),
        resolution: float = 0.08,
        color_on="elevation",
        rotate=True,
    ) -> None:
        super().__init__(interval, fig_size, resolution)
        self.color_on = color_on
        self.rotate = rotate

    def set_color_on(self, color_on: str):
        self.color_on = color_on

    def set_rotate(self, rotate: bool):
        self.rotate = rotate


class WorkoutAnimation:

    config: WorkoutAnimationConfig = WorkoutAnimationConfig()

    def __init__(self, data: pd.DataFrame, config: WorkoutAnimationConfig = None):
        """_summary_

        Parameters
        ----------
        data : pd.DataFrame
            _description_
        config : WorkoutAnimationConfig, optional
            _description_, by default None
        """
        self.data = data
        self.config = config if config else WorkoutAnimationConfig()

    def set_config(self, config: WorkoutAnimationConfig):
        self.config = config

    def __project_lonlat_to_xy(self, lon: float, lat: float) -> Tuple[float, float]:
        middle_of_map_lat = np.mean(lat)
        lon = lon * np.abs(np.cos(middle_of_map_lat))
        return lon, lat

    # Calculate line segments for coloring
    def __calculate_segments(
        self, x: pd.Series, y: pd.Series, elevation: pd.Series
    ) -> np.ndarray:
        points = np.array([x, y, elevation]).T.reshape(-1, 1, 3)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        return segments

    def __data_for_plotting(self) -> Tuple[pd.DataFrame]:
        title = pd.to_datetime(self.data["time"].iloc[0]).date()
        strip = int(1 / self.config.resolution)
        # x, y = self.__project_lonlat_to_xy(self.data["lon"], self.data["lat"])
        x, y = self.data["lon"], self.data["lat"]
        elevation = self.data["elevation"]
        s = self.data[self.config.color_on]

        x, y, elevation, s = (x[::strip], y[::strip], elevation[::strip], s[::strip])

        return x, y, elevation, s, title

    def plot_route(self):
        x, y, elevation, s, title = self.__data_for_plotting()

        fig = plt.figure(figsize=self.config.fig_size)
        ax = fig.add_subplot(111, projection="3d")

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
                ax.view_init(10, i / 5)
            return [fig]

        ani = animation.FuncAnimation(
            fig,
            update,
            init_func=init,
            frames=len(segments),
            interval=self.config.interval,
            blit=True,
        )
        return ani
