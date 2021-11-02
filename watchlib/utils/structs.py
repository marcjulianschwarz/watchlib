from typing import Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

class ECG:

    def __init__(self, data: pd.DataFrame, name: str):
        self.data, self.meta_data = self.read_ecg(data)
        self.name = name

    def read_ecg(self, ecg: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        name = ecg.columns[1]
        ecg = ecg.rename(columns={
                ecg.columns[0]: "name",
                ecg.columns[1]: "value"})

        meta_data = ecg.iloc[:9]
        meta_data = dict(zip(meta_data.name, meta_data.value))
        meta_data["name"] = name

        data = ecg[9:].dropna().astype("int32")

        return data, meta_data
    

    def bpm(self, a: float = 50, d: float = 180, r:float = 3, plot: bool = False) -> int:
        """
            Calculates heart rate (bpm) from ecg data.

            a: heart beat slope amplitude threshold
            d: heart beat distance threshold
            r: slope calculation resolution
            plot: plot ecg, slope and heart beat points
        """
        
        x = [xx for xx in range(0, len(self.data["name"]))]
        y = self.data["name"]

        def slope(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            slope = (y2 - y1)/(x2 - x1)
            return slope

        slopes = []
        for xx in x:
            if xx + r < len(y):
                point1 = (xx, y.iloc[xx])
                point2 = (xx+r, y.iloc[xx+r])
                slopes.append(slope(point1, point2))

        bpm_points = [-d]
        for idx, slope in enumerate(slopes):
            if np.abs(slope) > a and np.abs(bpm_points[-1] - x[idx]) > d:
                bpm_points.append(x[idx])
        bpm_points = bpm_points[1:]

        bp = len(bpm_points)*2
        #bp_val = valid[name]
        #error = np.abs(bp - bp_val)
    
        if plot:
            fig, ax = plt.subplots(figsize=(20, 5))
            ax.plot(x, y, label="ECG", zorder=0)
            ax.plot(slopes, label="slope", zorder=1)
            ax.scatter(x=bpm_points, y=[200 for y in range(len(bpm_points))], c="r", s=60, label="heartbeat", zorder=2)
            ax.legend()
            plt.show()
            return bp, fig

        return bp


class WorkoutRoute:

    route: pd.DataFrame
    name: str

    def __init__(self, data, name: str):
        if isinstance(data, pd.DataFrame):
            self.route = data
        else:
            self.route = self.__read_route()
        
        self.name = name

    def __getitem__(self, key):
        return self.route[key]

    def __read_route(self) -> pd.DataFrame:

        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
        tracks = self.data.findall('gpx:trk', ns)

        data = {
            "lon": [],
            "lat": [],
            "time": [],
            "elevation": [],
            "speed": [],
            "course": [],
            "hAcc": [],
            "vAcc": []
        }

        for track in tracks:
            track_segments = track.findall('gpx:trkseg', ns)
            for track_segment in track_segments:
                track_points = track_segment.findall('gpx:trkpt', ns)
                for track_point in track_points:

                    elevation = track_point.findall('gpx:ele', ns)[0].text
                    time = track_point.findall('gpx:time', ns)[0].text
                    extension = track_point.findall('gpx:extensions', ns)[0]

                    lon = track_point.get("lon")
                    lat = track_point.get("lat")
                    speed = extension.findall('gpx:speed', ns)[0].text
                    course = extension.findall('gpx:course', ns)[0].text
                    hAcc = extension.findall('gpx:hAcc', ns)[0].text
                    vAcc = extension.findall('gpx:vAcc', ns)[0].text

                    data["lon"].append(float(lon))
                    data["lat"].append(float(lat))
                    data["elevation"].append(float(elevation))
                    data["time"].append(time)
                    data["speed"].append(float(speed))
                    data["course"].append(float(course))
                    data["hAcc"].append(float(hAcc))
                    data["vAcc"].append(float(vAcc))

        return pd.DataFrame(data)

