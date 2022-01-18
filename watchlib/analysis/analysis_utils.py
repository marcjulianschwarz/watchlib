from watchlib.utils import ECG
import numpy as np


def slope_between(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    slope = (y2 - y1)/(x2 - x1)
    return slope


def slopes_for(list, r=1):
    slopes = []
    for i in range(len(list) - r):
        p1 = list[i]
        p2 = list[i + r]
        slopes.append(slope_between(p1, p2))
    return slopes


# def slope_for_splits(split: ECG, r=3):
#     x = [xx for xx in range(0, len(split["name"]))]
#     y = split["name"]

#     slopes = []
#     for xx in x:
#         if xx + r < len(y):
#             point1 = (xx, y.iloc[xx])
#             point2 = (xx+r, y.iloc[xx+r])
#             slopes.append(slope_between(point1, point2))

#     # fig, ax = plt.subplots()
#     # ax.plot(slopes, label="slope", zorder=1)
#     # ax.plot(x, y, label="ECG", zorder=0)
#     # ax.legend()
#     return slopes

def slopes_of_slopes_for(l, r=1):

    y = slopes_for(l, r)
    x = [xx for xx in range(0, len(y))]
    slopes = slopes_for(list(zip(x, y)))

    # fig, ax = plt.subplots()
    # ax.plot(slopes, label="slope", zorder=1)
    # ax.plot(x, y[:-r])
    # ax.legend()

    return slopes
