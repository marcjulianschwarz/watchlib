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
        return ECG(pd.read_csv(os.path.join(self.ecg_path, ecg_name)), ecg_name)

    def load_ecgs(self) -> List[ECG]:
        files = os.listdir(self.ecg_path)
        print(f"Loading {len(files)} electrocardiograms.")
        return [self.load_ecg(filename) for filename in files]


    # Workout Routes
    def load_route(self, route_name: str) -> WorkoutRoute:
        with open(os.path.join(self.workout_path, route_name), "rb") as f:
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
        self.export_path = os.path.join(path, "Export.xml")
        self.ecg_path = os.path.join(path, "electrocardiograms")
        self.workout_path = os.path.join(path, "workout-routes")
        self.cached_routes_path = os.path.join(self.workout_path, "cached_routes")
        self.cached_export_data_path = os.path.join(path, "cached_export_data")

    def __cache_route(self, route: WorkoutRoute):
        if not os.path.exists(self.cached_routes_path):
            os.mkdir(self.cached_routes_path)
        route.route.to_csv(os.path.join(self.cached_routes_path, route.name), index=False)

    def cache_routes(self, routes: List[WorkoutRoute]):
        for route in routes:
            self.__cache_route(route)
    
    def load_cached_route(self, filename) -> WorkoutRoute:
        return WorkoutRoute(pd.read_csv(os.path.join(self.cached_routes_path, filename)), filename)

    def load_cached_routes(self) -> List[WorkoutRoute]:
        routes = []
        for filename in os.listdir(self.cached_routes_path):
            routes.append(self.load_cached_route(filename))
        return routes

    # Cached export data
    def cache_export_data(self, data: dict):
        for key in data:
            df = data[key]
            df.to_csv(os.path.join(self.cached_export_data_path, f"{key}.csv"), index=False)

    def get_identifier_name(self, id):
        if "Identifier" in id:
            return id.split("Identifier")[1]
        else:
            return id.split("Type")[1]

    def load_cached_export_data_by_key(self, key: str) -> pd.DataFrame:
        return pd.read_csv(os.path.join(self.cached_export_data_path, key))

    def load_cached_export_data(self) -> Dict[str, pd.DataFrame]:
        data = {}
        for filename in os.listdir(self.cached_export_data_path):
            id = self.get_identifier_name(filename.split(".csv")[0])
            data[id] = self.load_cached_export_data_by_key(filename)
        return data

