import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# https://stackoverflow.com/questions/16266809/convert-from-latitude-longitude-to-x-y
# 
def project_to_xy(lon, lat):

    middle_of_map_lat = np.mean(lat)
    lon = lon*np.abs(np.cos(middle_of_map_lat))
    return lon, lat


def workout_three_d(workout_route, resolution=0.5):

    title = pd.to_datetime(workout_route["time"].iloc[0]).date()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x, y = project_to_xy(workout_route["lon"], workout_route["lat"])
    elevation =  workout_route["elevation"]

    strip = int(1 / resolution)

    ax.plot(x[::strip], y[::strip], elevation[::strip])
    ax.set_zlim(300, 500)
    plt.title(title)
    plt.show()
