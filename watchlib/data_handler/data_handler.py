from fileinput import filename
import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Tuple, Dict
import numpy as np
from watchlib.utils import ECG, WorkoutRoute
from abc import ABC


class DataManager(ABC):

    def get_filenames_for(self, path: str) -> List[str]:
        filenames = os.listdir(path)
        filenames = [f for f in filenames if os.path.isfile(
            os.path.join(path, f)) and not f.startswith(".")]
        return filenames


class DataLoader(DataManager):

    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = path + "/Export.xml"
        self.ecg_path = path + "/electrocardiograms"
        self.workout_path = path + "/workout-routes"

    def supports(self, data: str):
        if data == "ecg":
            return os.path.exists(self.ecg_path)
        if data == "routes":
            return os.path.exists(self.workout_path)
        if data == "health":
            return os.path.exists(self.export_path)

    def load_export_data(self) -> dict:

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

        print(f"[Data Loader]\tLoading {len(data)} health dataframes...")

        for key in data.keys():
            data[key] = pd.DataFrame(data[key], columns=["time", "value"])

        return data

    # ----------
    # ECG
    # ----------

    def load_ecg(self, ecg_name: str) -> ECG:
        with open(os.path.join(self.ecg_path, ecg_name), "r", encoding="utf-8") as f:
            return ECG(f.read(), ecg_name)

    def load_ecgs(self) -> List[ECG]:
        filenames = self.get_filenames_for(self.ecg_path)
        print(f"[Data Loader]\tLoading {len(filenames)} electrocardiograms...")
        return [self.load_ecg(filename) for filename in filenames]

    # ----------
    # Workout Routes
    # ----------

    def load_route(self, route_name: str) -> WorkoutRoute:
        with open(os.path.join(self.workout_path, route_name), "rb") as f:
            route = ET.parse(f, parser=ET.XMLParser(
                encoding="utf-8")).getroot()
            return WorkoutRoute(route, route_name)

    def load_routes(self) -> List[WorkoutRoute]:
        filenames = self.get_filenames_for(self.workout_path)
        print(f"[Data Loader]\tLoading {len(filenames)} workout routes...")
        routes = []
        for filename in filenames:
            routes.append(self.load_route(filename))
        return routes

    def count_routes(self):
        return len(self.get_filenames_for(self.workout_path))


class CacheHandler(DataManager):

    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = os.path.join(path, "Export.xml")
        self.ecg_path = os.path.join(path, "electrocardiograms")
        self.workout_path = os.path.join(path, "workout-routes")
        self.cached_routes_path = os.path.join(
            self.workout_path, "cached_routes")
        self.cached_export_data_path = os.path.join(path, "cached_export_data")
        self.cached_route_animations_path = os.path.join(self.workout_path, "cached_animations")

        if "apple_health_export" in self.workout_path: # Only create folders if path is a apple export path
            if not os.path.exists(self.cached_routes_path):
                os.makedirs(self.cached_routes_path, exist_ok=True)
            if not os.path.exists(self.cached_export_data_path):
                os.makedirs(self.cached_export_data_path, exist_ok=True)
            if not os.path.exists(self.cached_route_animations_path):
                os.makedirs(self.cached_route_animations_path, exist_ok=True)

    def __cache_route(self, route: WorkoutRoute):
        if not os.path.exists(self.cached_routes_path):
            os.mkdir(self.cached_routes_path)
        route.route.to_csv(os.path.join(
            self.cached_routes_path, route.name), index=False)

    def isCached(self, data: str):
        if data == "routes":
            return len(self.get_filenames_for(self.cached_routes_path)) > 1
        elif data == "export":
            return len(self.get_filenames_for(self.cached_export_data_path)) > 1

    def cache_routes(self, routes: List[WorkoutRoute]):
        print(f"[Cache Handler]\tCaching {len(routes)} routes...")
        for route in routes:
            self.__cache_route(route)

    def load_cached_route(self, filename) -> WorkoutRoute:
        return WorkoutRoute(pd.read_csv(os.path.join(self.cached_routes_path, filename)), filename)

    def load_cached_routes(self) -> List[WorkoutRoute]:
        routes = []
        filenames = self.get_filenames_for(self.cached_routes_path)
        print(f"[Cache Handler]\tLoadig {len(filenames)} cached routes...")
        for filename in filenames:
            routes.append(self.load_cached_route(filename))
        return routes

    # ----------
    # Cached export data
    # ----------

    def cache_export_data(self, data: dict):
        print(f"[Cache Handler]\tCaching {len(data)} health dataframes...")
        for key in data:
            df = data[key]
            df.to_csv(os.path.join(self.cached_export_data_path,
                      f"{key}.csv"), index=False)

    def get_identifier_name(self, id):
        if "Identifier" in id:
            return id.split("Identifier")[1]
        else:
            return id.split("Type")[1]

    def load_cached_export_data_by_key(self, key: str) -> pd.DataFrame:
        return pd.read_csv(os.path.join(self.cached_export_data_path, key))

    def load_cached_export_data(self) -> Dict[str, pd.DataFrame]:
        data = {}
        filenames = self.get_filenames_for(self.cached_export_data_path)
        print(f"[Cache Handler]\tLoading {len(filenames)} cached health dataframes...")
        for filename in filenames:
            id = self.get_identifier_name(filename.split(".csv")[0])
            data[id] = self.load_cached_export_data_by_key(filename)
        return data
