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
    
    def __getitem__(self, key):
        return self.data[key]

class ECGWave:
    def __init__(self):
        pass

class WorkoutRoute:

    route: pd.DataFrame
    name: str

    def __init__(self, data, name: str):
        if isinstance(data, pd.DataFrame):
            self.route = data
        elif isinstance(data, ET.Element):
            self.route = self.__read_route(data)
        else:
            raise ValueError("This workout type does not exist")
        
        self.name = name

    def __getitem__(self, key):
        return self.route[key]

    @property
    def lon(self):
        return self.route["lon"]
    
    @property
    def lat(self):
        return self.route["lat"]
    
    @property
    def time(self):
        return self.route["time"]
    
    @property
    def elevation(self):
        return self.route["elevation"]
    
    @property
    def speed(self):
        return self.route["speed"]
    
    @property
    def course(self):
        return self.route["course"]

    @property
    def hAcc(self):
        return self.route["hAcc"]
    
    @property
    def vAcc(self):
        return self.route["vAcc"]
    
    
    

    def __read_route(self, data: ET.Element) -> pd.DataFrame:

        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
        tracks = data.findall('gpx:trk', ns)

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

