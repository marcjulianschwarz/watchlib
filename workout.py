import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib import animation
from datetime import datetime as dt


# https://stackoverflow.com/questions/16266809/convert-from-latitude-longitude-to-x-y

def project_to_xy(lon, lat):

    middle_of_map_lat = np.mean(lat)
    lon = lon*np.abs(np.cos(middle_of_map_lat))
    return lon, lat


def workout_three_d(
        workout_route: pd.DataFrame,
        color_on: str = "elevation",
        resolution=0.5,
        save_animation: bool = False,
        path: str = "animations/",
        format: str = "gif"):

    if workout_route.empty:
        print("No data available for this route")
        return

    title = pd.to_datetime(workout_route["time"].iloc[0]).date()
    strip = int(1 / resolution)
    x, y = project_to_xy(workout_route["lon"], workout_route["lat"])
    elevation = workout_route["elevation"]
    s = workout_route[color_on]

    x, y, elevation, s = (x[::strip], y[::strip], elevation[::strip], s[::strip])

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')

    points = np.array([x, y, elevation]).T.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(s.min(), s.max())
    lc = Line3DCollection(segments, cmap="viridis", norm=norm)
    lc.set_array(s)
    # line = ax.add_collection3d(lc, zs=elevation, zdir="z")

    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(y.min(), y.max())
    ax.set_zlim(elevation.min() - 30, elevation.max() + 30)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_zlabel("Elevation")

    ax.text2D(0.05, 0.95, "Color:" + color_on, transform=ax.transAxes)

    plt.title(title)
    plt.show()

    if save_animation:
        def init():
            ax.view_init(10, 0)
            return [fig]

        def animate(i):
            ax.view_init(10, i)
            return [fig]

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=70, interval=20, blit=True)
        anim.save(path + "animation" + str(dt.now().timestamp()) + "." + format, fps=24, dpi=80)
