import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Tuple


class DataLoader:

    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = path + "/Export.xml"
        self.ecg_path = path + "/electrocardiograms/"
        self.workout_path = path + "/workout-routes/"

    def get_export_data(self) -> dict:

        tree = ET.parse(self.export_path)
        root = tree.getroot()

        records = root.findall('Record')

        data = {}

        for x in records:
            data[x.get("type")] = []

        for record in records:
            key = record.get("type")
            value = record.get("value")
            time = record.get("creationDate")
            data[record.get("type")].append((time, value))

        for key in data.keys():
            data[key] = pd.DataFrame(data[key], columns=["time", "value"])

        return data

    # ECG

    def load_ecgs(self) -> List[pd.DataFrame]:
        files = os.listdir(self.ecg_path)
        print(f"Loading {len(files)} electrocardiograms.")
        return [pd.read_csv(self.ecg_path + filename) for filename in files]

    def load_ecg(self, ecg_name: str) -> pd.DataFrame:
        return pd.read_csv(self.ecg_path + ecg_name)

    def read_ecg(self, ecg: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:

        name = ecg.columns[1]
        ecg = ecg.rename(columns={
                ecg.columns[0]: "name",
                ecg.columns[1]: "value"})

        meta_data = ecg.iloc[:9]
        meta_data = dict(zip(meta_data.name, meta_data.value))
        meta_data["name"] = name

        data = ecg[9:].dropna().astype("int32")

        return meta_data, data

    # Workout Routes

    def load_workout_routes(self) -> List[ET.Element]:

        filenames = os.listdir(self.workout_path)
        print(f"Loading {len(filenames)} workout routes.")
        routes = []
        for filename in filenames:
            with open(self.workout_path + filename) as f:
                routes.append(ET.parse(f).getroot())
        return routes

    def load_workout_route(self, route: str) -> ET.Element:
        with open(self.workout_path + route) as file:
            return ET.parse(file).getroot()

    def read_workout_route(self, route: ET.Element) -> pd.DataFrame:

        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
        tracks = route.findall('gpx:trk', ns)

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
