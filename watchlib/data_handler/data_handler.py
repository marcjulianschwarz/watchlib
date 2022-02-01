import multiprocessing
import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Dict
from watchlib.utils import ECG, WorkoutRoute
from abc import ABC
from multiprocessing import Pool


class DataManager(ABC):

    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = os.path.join(path, "Export.xml")
        self.ecg_path = os.path.join(path, "electrocardiograms")
        self.workout_path = os.path.join(path, "workout-routes")  

        self.export_path_exists = os.path.exists(self.export_path)
        self.ecg_path_exists = os.path.exists(self.ecg_path)
        self.workout_path_exists = os.path.exists(self.workout_path)

    def get_filenames_for(self, path: str) -> List[str]:
        filenames = os.listdir(path)
        filenames = [f for f in filenames if os.path.isfile(
            os.path.join(path, f)) and not f.startswith(".")]
        return filenames


class DataLoader(DataManager):

    def __init__(self, path: str) -> None:
        super().__init__(path)

    def supports(self, data: str):
        if data == "ecg":
            return os.path.exists(self.ecg_path)
        if data == "routes":
            return os.path.exists(self.workout_path)
        if data == "health":
            return os.path.exists(self.export_path)

    def load_export_data(self) -> dict:

        if self.supports("health"):
            tree = ET.parse(self.export_path)
            root = tree.getroot()
            records = root.findall('Record')

            data = {}

            # Init all arrays
            for record in records:
                data[record.get("type")] = []

            print(f"[Data Loader]\t\tLoading {len(data)} health dataframes...")

            for record in records:
                key = record.get("type")
                value = record.get("value")
                time = record.get("creationDate")
                data[key].append((time, value))

            for key in data.keys():
                data[key] = pd.DataFrame(data[key], columns=["time", "value"])

            return data
        else:
            print("[ERROR] the health data path (Export.xml) doesnt exist.")
            return {}
            

    # ----------
    # ECG
    # ----------

    def load_ecg(self, ecg_name: str) -> ECG:
        with open(os.path.join(self.ecg_path, ecg_name), "r", encoding="utf-8") as f:
            return ECG(f.read(), ecg_name)

    def load_ecgs(self) -> List[ECG]:
        if self.supports("ecg"):
            filenames = self.get_filenames_for(self.ecg_path)
            print(f"[Data Loader]\t\tLoading {len(filenames)} electrocardiograms...")
            return [self.load_ecg(filename) for filename in filenames]
        else:
            print("[ERROR] the ecg path doesnt exist.")
            return []

    # ----------
    # Workout Routes
    # ----------

    def load_route(self, route_name: str) -> WorkoutRoute:
        with open(os.path.join(self.workout_path, route_name), "rb") as f:
            route = ET.parse(f, parser=ET.XMLParser(
                encoding="utf-8")).getroot()
            return WorkoutRoute(route, route_name)

    def load_routes(self, parallel=True) -> List[WorkoutRoute]:
        if not self.supports("routes"):
            print("[ERROR] the workout-routes path doesnt exist.")
        else:
            if parallel:
                return self.load_routes_par()    
            else:
                return self.load_routes_seq()
        
    def load_routes_seq(self) -> List[WorkoutRoute]:
        filenames = self.get_filenames_for(self.workout_path)
        print(f"[Data Loader]\t\tLoading {len(filenames)} workout routes...")
        return [self.load_route(filename) for filename in filenames]

    def load_routes_par(self) -> List[WorkoutRoute]:
        filenames = self.get_filenames_for(self.workout_path)
        pool = Pool(multiprocessing.cpu_count())
        print(f"[Data Loader]\t\tLoading {len(filenames)} workout routes in parallel...")
        return pool.map(self.load_route, filenames)
        
    def count_routes(self):
        return len(self.get_filenames_for(self.workout_path))


class CacheHandler(DataManager):

    def __init__(self, path: str) -> None:

        super().__init__(path)
        
        self.cached_routes_path = os.path.join(self.workout_path, "cached_routes")
        self.cached_export_data_path = os.path.join(path, "cached_export_data")
        self.cached_route_animations_path = os.path.join(self.workout_path, "cached_animations")
        self.__check_folders()

    def __check_folders(self):
        if "apple_health_export" in self.workout_path: # Only create folders if path is an apple export path
            if not os.path.exists(self.cached_routes_path):
                os.makedirs(self.cached_routes_path, exist_ok=True)
            if not os.path.exists(self.cached_export_data_path):
                os.makedirs(self.cached_export_data_path, exist_ok=True)
            if not os.path.exists(self.cached_route_animations_path):
                os.makedirs(self.cached_route_animations_path, exist_ok=True)

    def delete_all_caches(self):
        self.delete_all_export_caches()
        self.delete_all_route_caches()

    def delete_all_export_caches(self):
        for file in self.get_filenames_for(self.cached_export_data_path):
            self.delete_export_cache(file)

    def delete_all_route_caches(self):
        for file in self.get_filenames_for(self.cached_routes_path):
            self.delete_route_cache(file)

    def delete_all_animation_caches(self):
        for file in self.get_filenames_for(self.cached_route_animations_path):
            self.delete_animation_cache(file)

    # Delete individual caches
    def delete_export_cache(self, name: str):
        print(f"[Cache Handler]\t\tDELETE {name}")
        os.remove(os.path.join(self.cached_export_data_path, name))

    def delete_route_cache(self, name: str):
        print(f"[Cache Handler]\t\tDELETE {name}")
        os.remove(os.path.join(self.cached_routes_path, name))

    def delete_animation_cache(self, name: str):
        print(f"[Cache Handler]\t\tDELETE {name}")
        os.remove(os.path.join(self.cached_route_animations_path, name))

    def isCached(self, data: str):
        if data == "routes":
            return len(self.get_filenames_for(self.cached_routes_path)) > 1
        elif data == "export":
            return len(self.get_filenames_for(self.cached_export_data_path)) > 1
        elif data == "animation":
            return 

    # ----------
    # Cache routes
    # ----------

    def __cache_route(self, route: WorkoutRoute):
        route.route.to_csv(os.path.join(
            self.cached_routes_path, route.name), index=False)

    def cache_routes(self, routes: List[WorkoutRoute]):
        self.__check_folders()
        print(f"[Cache Handler]\t\tCaching {len(routes)} routes...")
        for route in routes:
            self.__cache_route(route)

    def load_cached_route(self, filename) -> WorkoutRoute:
        return WorkoutRoute(pd.read_csv(os.path.join(self.cached_routes_path, filename)), filename)

    def load_cached_routes(self) -> List[WorkoutRoute]:
        if self.is_routes_cached():    
            routes = []
            filenames = self.get_filenames_for(self.cached_routes_path)
            print(f"[Cache Handler]\t\tLoadig {len(filenames)} cached routes...")
            for filename in filenames:
                routes.append(self.load_cached_route(filename))
            return routes
        else:
            print("[ERROR]\t\tThe routes havent been cached yet.")
            return []

    def is_routes_cached(self):
        self.__check_folders()
        return self.isCached("routes")

    # ---------
    # Cache route animations
    # ---------

    def cache_route_animation(self, html: str, name: str):
        self.__check_folders()
        print(f"[Cache Handler]\t\tCaching animation: {name}")
        with open(os.path.join(self.cached_route_animations_path, name), "w") as f:
            f.write(html)

    def load_cached_route_animation(self, name: str):
        if self.is_animation_cached(name):
            print(f"[Cache Handler]\t\tLoading cached animation: {name}")
            with open(os.path.join(self.cached_route_animations_path, name), "r") as f:
                return f.read()
        else:
            print(f"[ERROR]\t\tThe animation {name} hasnt been cached yet.")

    def is_animation_cached(self, name: str):
        return os.path.exists(os.path.join(self.cached_route_animations_path, name))

    # ----------
    # Cached export data
    # ----------

    def cache_export_data(self, data: dict):
        self.__check_folders()
        print(f"[Cache Handler]\t\tCaching {len(data)} health dataframes...")
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
        if self.is_export_data_cached():
            data = {}
            filenames = self.get_filenames_for(self.cached_export_data_path)
            print(f"[Cache Handler]\t\tLoading {len(filenames)} cached health dataframes...")
            for filename in filenames:
                id = self.get_identifier_name(filename.split(".csv")[0])
                data[id] = self.load_cached_export_data_by_key(filename)
            return data
        else:
            print("[ERROR]\t\tExport data hasnt been cached yet.")
            return {}

    def is_export_data_cached(self):
        return os.path.exists(self.cached_export_data_path)
