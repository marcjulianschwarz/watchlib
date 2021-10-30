import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Tuple, Dict
import numpy as np


class DataLoader:

    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = path + "/Export.xml"
        self.ecg_path = path + "/electrocardiograms"
        self.workout_path = path + "/workout-routes"
        self.cached_routes_path = self.workout_path + "/cached_routes"

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

    def load_ecg(self, ecg_name: str) -> pd.DataFrame:
        return pd.read_csv(self.ecg_path + "/" + ecg_name)

    def load_ecgs(self) -> Dict[str, pd.DataFrame]:
        files = os.listdir(self.ecg_path)
        print(f"Loading {len(files)} electrocardiograms.")
        return dict(zip(files, [self.load_ecg(filename) for filename in files]))

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

    def read_ecgs(self, ecgs: Dict[str, pd.DataFrame]) -> Dict[str, Tuple[pd.DataFrame, pd.DataFrame]]:
        return dict(zip(ecgs.keys(), [self.read_ecg(ecg) for ecg in ecgs.values()]))


    # Workout Routes
    def load_routes(self) -> List[ET.Element]:

        filenames = os.listdir(self.workout_path)
        filenames = [filename for filename in filenames if os.path.isfile(os.path.join(self.workout_path, filename))]
        print(f"Loading {len(filenames)} workout routes.")
        routes = []
        for filename in filenames:
            with open(self.workout_path + "/" + filename) as f:
                routes.append(ET.parse(f).getroot())
        
        return dict(zip(filenames, routes))

    def load_route(self, date: str) -> ET.Element:

        filenames = np.array(os.listdir(self.workout_path))
        routes = []
        route_roots = []
        for filename in filenames:
            if ("route_" + date) in filename:
                routes.append(filename)

        for route in routes:
            with open(self.workout_path + "/" + route) as file:
                route_roots.append(ET.parse(file).getroot())
        
        if len(route_roots) == 1:
            return route_roots[0]
        else:
            return route_roots

    def read_route(self, route: ET.Element) -> pd.DataFrame:

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

    def read_routes(self, routes: Dict[str, ET.Element]) -> Dict[str, pd.DataFrame]:
        data = [self.read_route(route) for route in routes.values()]
        return dict(zip(routes.keys(), data))

    # CSV saving and loading
    def cache_route(self, data: pd.DataFrame, filename: str):
        if not os.path.exists(self.cached_routes_path):
            os.mkdir(self.cached_routes_path)
        data.to_csv(self.cached_routes_path + "/" + filename)

    def cache_routes(self, data: Dict[str, pd.DataFrame]):
        for key in data:
            self.cache_route(data[key], key)
    
    def load_cached_route(self, path):
        return pd.read_csv(path)

    def load_cached_routes(self) -> Dict[str, pd.DataFrame]:
        data = {}
        for filename in os.listdir(self.cached_routes_path):
            data[filename] = self.load_cached_route(self.cached_routes_path + "/" + filename)
        return data


class BBox:

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def __init__(self, min_lon, min_lat, max_lon, max_lat):
        self.min_lon = min_lon
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.max_lat = max_lat

    def get_values(self):
        return self.min_lon, self.min_lat, self.max_lon, self.max_lat


class BBoxFilter:

    bbox: BBox
    countries: Dict[str, BBox] = {
        "Italy": BBox(6.75, 36.62, 18.48, 47.12),
        "Germany": BBox(5.98865807458, 47.3024876979, 15.0169958839, 54.983104153),
        "Austria": BBox(9.48, 46.43, 16.98, 49.04)
    }

    def __init__(self, bbox: BBox):
        self.bbox = bbox

    def filter(self, routes: Dict[str, pd.DataFrame]):
        
        """
            routes: routes that should be filtered
        """

        min_lon, min_lat, max_lon, max_lat = self.bbox.get_values()

        filtered_routes = {}
        for key in routes:
            route = routes[key]
            if (route["lon"].min() >= min_lon) and (route["lon"].max() <= max_lon):
                if (route["lat"].min() >= min_lat) and (route["lat"].max() <= max_lat):
                    filtered_routes[key] = route
        return filtered_routes

    def filter_small_routes(self, routes, tolerance):
        raise NotImplementedError