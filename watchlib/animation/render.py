import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib import animation
from datetime import datetime as dt
from typing import Tuple

class WorkoutAnimation:
    
    resolution: float = 0.08
    color_on: str = "elevation"

    path: str = "animations/"
    interval: int = 20
    format: str = "mp4"
    fps: int = 120
    dpi: int = 80
    
    def __init__(self, workout_route):
        self.workout_route = workout_route

    def set_options(self, options):
        for option in options:
            raise NotImplementedError

    def set_path(self, path: str):
        self.path = path

    def set_interval(self, interval: int):
        self.interval = interval

    def set_fps(self, fps: int):
        self.fps = fps

    def set_dpi(self, dpi: int):
        self.dpi = dpi

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
        title = pd.to_datetime(self.workout_route["time"].iloc[0]).date()
        strip = int(1 / self.resolution)
        x, y = self.project_to_xy(self.workout_route["lon"], self.workout_route["lat"])
        elevation = self.workout_route["elevation"]
        s = self.workout_route[self.color_on]

        x, y, elevation, s = (x[::strip], y[::strip], elevation[::strip], s[::strip])

        return x, y, elevation, s, title
        

    def plot_route(self):
        x, y, elevation, s, title = self.data_for_plotting()

        fig = plt.figure(figsize=(8,8))
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
        plt.show()

        return fig, ax, lc, segments


    def walk_route_animation(self, rotation: bool = True):

        fig, ax, lc, segments = self.plot_route()

        def init():
            ax.view_init(10, 0)
            return [fig]

        def update_route(i):
            lc.set_segments(segments[:i])
            if rotation:
                ax.view_init(10, i/5)
            return [fig]
        
        anim = animation.FuncAnimation(fig, update_route, init_func=init, frames=len(segments), interval=self.interval, blit=True)
        return anim

    def render(self, animation_type: str):
        if animation_type == "walk_route":
            return self.walk_route_animation(False)
        elif animation_type == "walk_route_animation":
            return self.walk_route_animation(True)

    def save(self, anim, path):
        anim.save(self.path + "animation_test" + "." + self.format, fps=self.fps, dpi=self.dpi)