import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Tuple, Dict
import numpy as np
from watchlib.utils import ECG, WorkoutRoute
from abc import ABC


class DataLoader:

    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = path + "/Export.xml"
        self.ecg_path = path + "/electrocardiograms"
        self.workout_path = path + "/workout-routes"
        self.cached_routes_path = self.workout_path + "/cached_routes"
        self.cached_export_data_path = self.path + "/cached_export_data"

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
            data[key].append((time, value))

        for key in data.keys():
            data[key] = pd.DataFrame(data[key], columns=["time", "value"])

        return data


    # ECG
    def load_ecg(self, ecg_name: str) -> ECG:
        return ECG(pd.read_csv(self.ecg_path + "/" + ecg_name), ecg_name)

    def load_ecgs(self) -> List[ECG]:
        files = os.listdir(self.ecg_path)
        print(f"Loading {len(files)} electrocardiograms.")
        return [self.load_ecg(filename) for filename in files]


    # Workout Routes
    def load_route(self, route_name: str) -> WorkoutRoute:
        with open(self.workout_path + "/" + route_name, "rb") as f:
                route = ET.parse(f, parser=ET.XMLParser(encoding="utf-8")).getroot()
                return WorkoutRoute(route, route_name)
    
    def load_routes(self) -> List[WorkoutRoute]:
        filenames = os.listdir(self.workout_path)
        filenames = [filename for filename in filenames if os.path.isfile(os.path.join(self.workout_path, filename))]
        print(f"Loading {len(filenames)} workout routes.")
        routes = []
        for filename in filenames:
            if filename == ".DS_Store":
                continue
            routes.append(self.load_route(filename))
        return routes


class CacheHandler:

    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = path + "/Export.xml"
        self.ecg_path = path + "/electrocardiograms"
        self.workout_path = path + "/workout-routes"
        self.cached_routes_path = self.workout_path + "/cached_routes"
        self.cached_export_data_path = self.path + "/cached_export_data"

    def __cache_route(self, route: WorkoutRoute):
        if not os.path.exists(self.cached_routes_path):
            os.mkdir(self.cached_routes_path)
        route.route.to_csv(self.cached_routes_path + "/" + route.name, index=False)

    def cache_routes(self, routes: List[WorkoutRoute]):
        for route in routes:
            self.__cache_route(route)
    
    def load_cached_route(self, filename) -> WorkoutRoute:
        return WorkoutRoute(pd.read_csv(self.cached_routes_path + "/" + filename), filename)

    def load_cached_routes(self) -> List[WorkoutRoute]:
        routes = []
        for filename in os.listdir(self.cached_routes_path):
            routes.append(self.load_cached_route(filename))
        return routes

    # Cached export data
    def cache_export_data(self, data: dict):
        for key in data:
            df = data[key]
            df.to_csv(self.cached_export_data_path + "/" + key + ".csv", index=False)

    def get_identifier_name(self, id):
        if "Identifier" in id:
            return id.split("Identifier")[1]
        else:
            return id.split("Type")[1]

    def load_cached_export_data_by_key(self, key: str) -> pd.DataFrame:
        return pd.read_csv(self.cached_export_data_path + "/" + key)

    def load_cached_export_data(self) -> Dict[str, pd.DataFrame]:
        data = {}
        for filename in os.listdir(self.cached_export_data_path):
            id = self.get_identifier_name(filename.split(".csv")[0])
            data[id] = self.load_cached_export_data_by_key(filename)
        return data


# Filtering

class Filter(ABC):

    def __init__():
        pass



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


class BBoxFilter(Filter):

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

    def check_country_bbox(self, country: str, bbox: BBox) -> bool:
        country_bbox = self.countries[country]
        min_lon, min_lat, max_lon, max_lat = country_bbox.get_values()
        min_lon_r, min_lat_r, max_lon_r, max_lat_r = bbox.get_values()
        return (min_lon_r > min_lon) and (min_lat_r > min_lat) and (max_lon_r < max_lon) and (max_lat_r < max_lat)

    def route_bboxes(self) -> List[BBox]:
        bboxes = []
        for route in self.routes:
            lat_min, lat_max = route["lat"].min(), route["lat"].max()
            lon_min, lon_max = route["lon"].min(), route["lon"].max()
            bboxes.append(BBox(lon_min, lat_min, lon_max, lat_max))
        return bboxes

    def route_countries(self) -> List[str]:
        countries = []
        bboxes = self.route_bboxes()
        for bbox in bboxes:
            for country in self.countries:
                if self.check_country_bbox(country, bbox):
                    countries.append(country)           
        return countries

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

class TimeFilter(Filter):

    def __init__(self, routes: List[WorkoutRoute]):
        self.routes = routes

    def routes_after(self, time:str):
        raise NotImplementedError

    def routes_before(self, time:str):
        raise NotImplementedError

    def routes_between(self, start, end):
        raise NotImplementedError

    def min_time(self):
        raise NotImplementedError

    def max_time(self):
        raise NotImplementedError


class FilterPipeline:

    def __init__(self, filter_names:List[str], filters: List[Filter]):
        self.filter_names = filter_names
        self.filters = filters

    def filter(self, data):
        filtered_data = data
        for filter in self.filters:
            data = filter.filter(data)
        return filtered_data
