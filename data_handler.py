import xml.etree.ElementTree as ET
import pandas as pd
import os

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

        d = {}

        for x in records:
            d[x.get("type")] = []

        for record in records:
            d[record.get("type")].append(record.get("value"))

        return d


    def get_ecgs(self):
        ecgs = [pd.read_csv(self.ecg_path + filename) for filename in os.listdir(self.ecg_path)]
        print(f"Loaded {len(ecgs)} electrocardiograms.")
        return ecgs

    def read_ecg(self, ecg: pd.DataFrame):

        name = ecg.columns[1]
        ecg = ecg.rename(columns = {ecg.columns[0]: "name", ecg.columns[1]: "value"})

        meta_data = ecg.iloc[:9]
        meta_data = dict(zip(meta_data.name, meta_data.value))
        meta_data["name"] = name

        data = ecg[9:].dropna().astype("int32")

        return meta_data, data

    def __get_workout_route_root(self, route: str) -> ET.Element:
        
        tree = ET.parse(open(self.workout_path + route))
        return tree.getroot()

    def read_workout_route(self, route) -> pd.DataFrame:
        
        route = self.__get_workout_route_root(route)
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

    def get_routes(self):

        return [ET.parse(open(self.workout_path + filename)) for filename in os.listdir(self.workout_path)]
