import multiprocessing
import xml.etree.ElementTree as ET
import pandas as pd
import os
from typing import List, Dict
from watchlib.utils import ECG, WorkoutRoute
from abc import ABC
from multiprocessing import Pool
import json
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, filename="watchlib.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

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

    def get_identifier_name(self, id):
        if "Identifier" in id:
            return id.split("Identifier")[1]
        else:
            return id.split("Type")[1]


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

    def load_health_data(self) -> Dict[str, pd.DataFrame]:

        if self.supports("health"):
            tree = ET.parse(self.export_path)
            root = tree.getroot()
            records = root.findall('Record')

            data = {}

            # Init all arrays
            for record in records:
                data[record.get("type")] = []

            logging.info(f"[Data Loader] Loading {len(data)} health dataframes")

            for record in records:
                key = record.get("type")
                key = self.get_identifier_name(key)
                value = record.get("value")
                time = record.get("creationDate")
                data[key].append((time, value))

            for key in data.keys():
                df = pd.DataFrame(data[key], columns=["time", "value"])
                df["time"] = pd.to_datetime(df["time"])
                data[key] = df

            return data
        else:
            logging.error("The health data path (Export.xml) doesnt exist")
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
            logging.info(f"[Data Loader]\t\tLoading {len(filenames)} ECGs")
            return [self.load_ecg(filename) for filename in filenames]
        else:
            logging.error("The ecg path doesnt exist")
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
            logging.error("The workout routes path doesnt exist")
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
        routes = pool.map(self.load_route, filenames)
        pool.close()
        pool.join()
        print(f"[Data Loader]\t\tLoading {len(filenames)} workout routes in parallel...")
        return routes
        
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
        self.delete_all_health_data_caches()
        self.delete_all_route_caches()

    def delete_all_health_data_caches(self):
        for file in self.get_filenames_for(self.cached_export_data_path):
            self.delete_health_data_cache(file)

    def delete_all_route_caches(self):
        for file in self.get_filenames_for(self.cached_routes_path):
            self.delete_route_cache(file)

    def delete_all_animation_caches(self):
        for file in self.get_filenames_for(self.cached_route_animations_path):
            self.delete_animation_cache(file)

    # Delete individual caches
    def delete_health_data_cache(self, name: str):
        logging.info("[Cache Handler] DELETE " + name)
        os.remove(os.path.join(self.cached_export_data_path, name))

    def delete_route_cache(self, name: str):
        logging.info("[Cache Handler] DELETE " + name)
        os.remove(os.path.join(self.cached_routes_path, name))

    def delete_animation_cache(self, name: str):
        logging.info("[Cache Handler] DELETE " + name)
        os.remove(os.path.join(self.cached_route_animations_path, name))

    def isCached(self, data: str) -> bool:
        if data == "routes":
            return len(self.get_filenames_for(self.cached_routes_path)) > 1
        elif data == "health":
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
        logging.info(f"[Cache Handler] Caching {len(routes)} routes" )
        for route in routes:
            self.__cache_route(route)

    def __load_route(self, filename) -> WorkoutRoute:
        return WorkoutRoute(pd.read_csv(os.path.join(self.cached_routes_path, filename)), filename)

    def load_routes(self) -> List[WorkoutRoute]:
        if self.is_routes_cached():    
            routes = []
            filenames = self.get_filenames_for(self.cached_routes_path)
            print(f"[Cache Handler]\t\tLoadig {len(filenames)} cached routes...")
            for filename in filenames:
                routes.append(self.__load_route(filename))
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

    def load_route_animation(self, name: str) -> str:
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

    def cache_health_data(self, data: dict):
        self.__check_folders()
        print(f"[Cache Handler]\t\tCaching {len(data)} health dataframes...")
        for key in data:
            df = data[key]
            df.to_csv(os.path.join(self.cached_export_data_path,
                      f"{key}.csv"), index=False)

    def load_health_data_by_key(self, key: str) -> pd.DataFrame:
        return pd.read_csv(os.path.join(self.cached_export_data_path, key))

    def load_health_data(self) -> Dict[str, pd.DataFrame]:
        if self.is_health_data_cached():
            data = {}
            filenames = self.get_filenames_for(self.cached_export_data_path)
            print(f"[Cache Handler]\t\tLoading {len(filenames)} cached health dataframes...")
            for filename in filenames:
                id = self.get_identifier_name(filename.split(".csv")[0])
                data[id] = self.load_health_data_by_key(filename)
            return data
        else:
            logging.error("Health data hasnt been cached yet")
            return {}

    def is_health_data_cached(self):
        return os.path.exists(self.cached_export_data_path)



class HealthDataHandler(DataManager):

    def __init__(self, health_data: dict):
        self.identifiers = self.load_identifiers()
        self.health_data = health_data

    def load_identifiers(self):
        with open(os.path.join(os.path.dirname(__file__), "hk_identifiers.json"), "r") as f:
            return json.load(f)

    def get_event_identfiers(self):
        events = []
        for id in self.identifiers:
            events.extend(self.identifiers[id]["event"])
        return events

    def get_quantity_identfiers(self, types: List[str] = ["sum", "mean"]):
        quantities = []
        for id in self.identifiers:
            quantity = self.identifiers[id]["quantity"]
            if "sum" in types:
                quantities.extend(quantity["sum"])
            if "mean" in types:
                quantities.extend(quantity["mean"])
        return quantities

    def get_data_for(self, identifiers: List[str]):
        data = {}
        for id in identifiers:
            if id in self.health_data:
                data[id] = self.health_data[id]
            #else:   
                #print("[WARNING]\t\tThe identifier {id} is not in health data.")
        return data

    def is_identifier(self, identifier: str, aggregate: str):
        for id in self.identifiers:
            if identifier in self.identifiers[id]["quantity"][aggregate]:
                return True
        return False

    def group(self, identifiers, by = lambda x: x.split(" ")[0]):

        data = self.get_data_for(identifiers)

        grouped_dfs = []
        for d in data:

            if self.is_identifier(d, "sum"):
                x = data[d].set_index("time").groupby(by).sum()
            if self.is_identifier(d, "mean"):
                x = data[d].set_index("time").groupby(by).mean()
            x.columns = [d]
            grouped_dfs.append(x)

        return pd.concat(grouped_dfs, axis=1)

    def drop_outliers(self, data, method, threshold):

        if isinstance(data, pd.DataFrame):
            cleaned = pd.DataFrame()
            for col in data.columns:
                if data[col].dtype == float:
                    cleaned[col] = self.drop_outliers(data[col], method, threshold)
                else:
                    cleaned[col] = data[col]
            return cleaned
        else:
            if method == "iqr":
                iqr = data.quantile(0.75) - data.quantile(0.25)
                return data[(data >= data.quantile(0.25) - threshold * iqr) & (data <= data.quantile(0.75) + threshold * iqr)]
            if method == "z-score":
                m = data.mean()
                s = data.std()
                return data[(data - m)/s < threshold]

    def impute(self, data: pd.DataFrame, columns: List[str], method, inplace=False):
        if not inplace:
            data = data.copy()
        
        for column in columns:
            data[column].fillna(method(data[column]), inplace=True)
        
        if not inplace:
            return data

    def impute_row_wise(self, data: pd.DataFrame, columns: List[str], method, inplace=False):
        if not inplace:
            data = data.copy()

        for column in columns:
            data[column] = data[column].apply(lambda x: method(data[column]))

        if not inplace:
            return data 