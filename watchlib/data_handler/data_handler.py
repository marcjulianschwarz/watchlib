import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Tuple, Dict
import numpy as np
from watchlib.utils import ECG, WorkoutRoute


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

    def read_ecgs(self, ecgs: Dict[str, pd.DataFrame]) -> Dict[str, Tuple[pd.DataFrame, pd.DataFrame]]:
        return dict(zip(ecgs.keys(), [self.read_ecg(ecg) for ecg in ecgs.values()]))


    # Workout Routes
    def load_routes(self) -> List[WorkoutRoute]:
        filenames = os.listdir(self.workout_path)
        filenames = [filename for filename in filenames if os.path.isfile(os.path.join(self.workout_path, filename))]
        print(f"Loading {len(filenames)} workout routes.")
        routes = []
        for filename in filenames:
            if filename == ".DS_Store":
                continue
            with open(self.workout_path + "/" + filename, "rb") as f:
                route = ET.parse(f, parser=ET.XMLParser(encoding="utf-8")).getroot()
                routes.append(WorkoutRoute(route, filename))
        return routes


    def read_routes(self, routes: Dict[str, ET.Element]) -> Dict[str, WorkoutRoute]:
        data = {}
        for r in routes:
            route = routes[r]
            data[r] = WorkoutRoute(route)
        return data

    # CSV saving and loading
    def cache_route(self, data: pd.DataFrame, filename: str):
        if not os.path.exists(self.cached_routes_path):
            os.mkdir(self.cached_routes_path)
        data.to_csv(self.cached_routes_path + "/" + filename)

    def cache_routes(self, data: Dict[str, pd.DataFrame]):
        for key in data:
            self.cache_route(data[key], key)
    
    def load_cached_route(self, filename) -> WorkoutRoute:
        return WorkoutRoute(pd.read_csv(self.cached_routes_path + "/" + filename), filename)

    def load_cached_routes(self) -> List[WorkoutRoute]:
        routes = []
        for filename in os.listdir(self.cached_routes_path):
            routes.append(self.load_cached_route(filename))
        return routes


# Filtering

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

    countries: Dict[str, BBox] = {
        "All": BBox(0, 0, 100, 100),
        "Italy": BBox(6.75, 36.62, 18.48, 47.12),
        "Germany": BBox(5.98865807458, 47.3024876979, 15.0169958839, 54.983104153),
        "Austria": BBox(9.48, 46.43, 16.98, 49.04)
    }

    def __init__(self, routes: List[WorkoutRoute]):
        self.routes = routes

    def set_routes(self, routes: List[WorkoutRoute]):
        self.routes = routes

    def filter(self, bbox: BBox) -> List[WorkoutRoute]:
        
        """
            routes: routes that should be filtered
        """

        min_lon, min_lat, max_lon, max_lat = bbox.get_values()

        filtered_routes = []
        for route in self.routes:
            if (route["lon"].min() >= min_lon) and (route["lon"].max() <= max_lon):
                if (route["lat"].min() >= min_lat) and (route["lat"].max() <= max_lat):
                    filtered_routes.append(route)
        return filtered_routes

    def haversine(self, lat1: float, lat2: float, lon1: float, lon2: float) -> float:
        """
            Calculates distance between two points on earth in km
        """
        lat1, lat2, lon1, lon2 = np.deg2rad((lat1, lat2, lon1, lon2))

        latd = lat2 - lat1
        lond = lon2 - lon1
        R = 6372.8 # Earth radius in km
        d = 2*R*np.arcsin(np.sqrt(np.sin(latd/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(lond/2)**2))
        return d

    def haversine_for_route(self, route: WorkoutRoute) -> float:
        lat1, lat2 = route["lat"].min(), route["lat"].max()
        lon1, lon2 = route["lon"].min(), route["lon"].max()
        return self.haversine(lat1, lat2, lon1, lon2)

    def simple_dist(self, lat1: float, lat2: float, lon1: float, lon2: float) -> Tuple[float, float]:
        """
            Calculates distances between two lon and lat values
        """

        degree_to_meter = 111139
        lond = np.abs(lon1 - lon2)*degree_to_meter
        latd = np.abs(lat1 - lat2)*degree_to_meter
        return lond, latd

    def filter_small_routes(self, tolerance: float = 1.0) -> List[WorkoutRoute]:
        """
            This function uses the diagonal distance between the
            boundary box corners to filter out smaller routes based
            on a tolerance in km.
        """

        filtered_routes = []
        for route in self.routes:
            h = self.haversine_for_route(route)
            if h >= tolerance:
                filtered_routes.append(route)
        return filtered_routes

    def max_bbox(self) -> float:
        distances = [self.haversine_for_route(route) for route in self.routes]
        return max(distances)

    def min_bbox(self) -> float:
        distances = [self.haversine_for_route(route) for route in self.routes]
        return min(distances)
