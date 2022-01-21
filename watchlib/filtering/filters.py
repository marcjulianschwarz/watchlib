from typing import List, Tuple, Dict
from watchlib.utils import WorkoutRoute
from abc import ABC
import numpy as np
import json
from datetime import datetime as dt


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


class Filter(ABC):

    def __init__(self):
        pass

    def filter() -> List:
        pass


# Abstract filter class to filter with bounding boxes
class BBoxFilter(Filter):

    def set_routes(self, routes: List[WorkoutRoute]):
        self.routes = routes

    def route_bboxes(self, routes: List[WorkoutRoute]) -> List[BBox]:
        bboxes = []
        for route in self.routes:
            lat_min, lat_max = route["lat"].min(), route["lat"].max()
            lon_min, lon_max = route["lon"].min(), route["lon"].max()
            bboxes.append(BBox(lon_min, lat_min, lon_max, lat_max))
        return bboxes


class DiagonalBBoxFilter(BBoxFilter):

    def __init__(self, diagonal_distance: float):
        self.diagonal_distance = diagonal_distance

    def __haversine(lat1: float, lat2: float, lon1: float, lon2: float) -> float:
        """
            Calculates distance between two points on earth in km
        """
        lat1, lat2, lon1, lon2 = np.deg2rad((lat1, lat2, lon1, lon2))

        latd = lat2 - lat1
        lond = lon2 - lon1
        R = 6372.8  # Earth radius in km
        d = 2*R*np.arcsin(np.sqrt(np.sin(latd/2)**2 +
                          np.cos(lat1)*np.cos(lat2)*np.sin(lond/2)**2))
        return d

    def __haversine_for_route(route: WorkoutRoute) -> float:
        lat1, lat2 = route["lat"].min(), route["lat"].max()
        lon1, lon2 = route["lon"].min(), route["lon"].max()
        return DiagonalBBoxFilter.__haversine(lat1, lat2, lon1, lon2)

    @staticmethod
    def max_bbox(routes: List[WorkoutRoute]) -> float:
        distances = [DiagonalBBoxFilter.__haversine_for_route(
            route) for route in routes]
        return max(distances)

    @staticmethod
    def min_bbox(routes: List[WorkoutRoute]) -> float:
        distances = [DiagonalBBoxFilter.__haversine_for_route(
            route) for route in routes]
        return min(distances)

    def simple_dist(self, lat1: float, lat2: float, lon1: float, lon2: float) -> Tuple[float, float]:
        """
            Calculates distances between two lon and lat values
        """

        degree_to_meter = 111139
        lond = np.abs(lon1 - lon2)*degree_to_meter
        latd = np.abs(lat1 - lat2)*degree_to_meter
        return lond, latd

    def filter(self, routes: List[WorkoutRoute]) -> List[WorkoutRoute]:
        """
            This function uses the diagonal distance between the
            boundary box corners to filter out smaller routes based
            on a tolerance in km.
        """

        print(
            f"[Filter]\t\tFiltering out routes with a shorter diagonal than {self.diagonal_distance}km.")
        filtered_routes = []
        for route in routes:
            h = DiagonalBBoxFilter.__haversine_for_route(route)
            if h >= self.diagonal_distance:
                filtered_routes.append(route)
        return filtered_routes


class CountryFilter(BBoxFilter):

    countries: Dict[str, BBox] = {
        "All": BBox(0, 0, 100, 100),
        "Italy": BBox(6.75, 36.62, 18.48, 47.12),
        "Germany": BBox(5.98865807458, 47.3024876979, 15.0169958839, 54.983104153),
        "Austria": BBox(9.48, 46.43, 16.98, 49.04)
    }

    def __init__(self, country_bbox: BBox):
        self.country_bbox = country_bbox
        # self.load_country_bboxes()

    def load_country_bboxes(self, path: str):
        with open(path, "r") as f:
            countries_json = json.load(f)
            for country in countries_json:
                min_lat = countries_json[country]["sw"]["lat"]
                min_lon = countries_json[country]["sw"]["lon"]

                max_lat = countries_json[country]["ne"]["lat"]
                max_lon = countries_json[country]["ne"]["lon"]

                self.countries[country] = BBox(
                    min_lon, min_lat, max_lon, max_lat)

    def check_country_bbox(self, country: str, bbox: BBox) -> bool:
        country_bbox = self.countries[country]
        min_lon, min_lat, max_lon, max_lat = country_bbox.get_values()
        min_lon_r, min_lat_r, max_lon_r, max_lat_r = bbox.get_values()
        return (min_lon_r > min_lon) and (min_lat_r > min_lat) and (max_lon_r < max_lon) and (max_lat_r < max_lat)

    def route_countries(self, routes: List[WorkoutRoute]) -> List[str]:
        countries = []
        bboxes = self.route_bboxes(routes)
        for bbox in bboxes:
            for country in self.countries:
                if self.check_country_bbox(country, bbox):
                    countries.append(country)
        return countries

    def filter(self, routes: List[WorkoutRoute]) -> List[WorkoutRoute]:
        """
            routes: routes that should be filtered
        """

        print(f"[Filter]\t\tFiltering only routes from {self.country_bbox}.")

        min_lon, min_lat, max_lon, max_lat = self.country_bbox.get_values()

        filtered_routes = []
        for route in routes:
            if (route["lon"].min() >= min_lon) and (route["lon"].max() <= max_lon):
                if (route["lat"].min() >= min_lat) and (route["lat"].max() <= max_lat):
                    filtered_routes.append(route)
        return filtered_routes


class TimeFilter(Filter):

    def __init__(self, _from: dt = None, _to: dt = None, min_duration_sec=0, max_duration_sec=0):
        if _from is None:
            self._from = dt.fromtimestamp(0)
        else:
            self._from = _from

        if _to is None:
            self._to = dt.now()
        else:
            self._to = _to

        self.min_duration_sec = min_duration_sec
        self.max_duration_sec = max_duration_sec

    def filter(self, routes: List[WorkoutRoute]) -> List[WorkoutRoute]:

        print(
            f"[Filter]\t\tFiltering out routes from {self._from.date()} to {self._to.date()} which are {self.min_duration_sec} to {self.max_duration_sec} seconds long.")
        filtered_routes = []
        for route in routes:
            if route.start and route.end and route.duration_sec:
                if route.start > self._from and route.end < self._to and route.duration_sec <= self.max_duration_sec and route.duration_sec >= self.min_duration_sec:
                    filtered_routes.append(route)
        return filtered_routes

    @staticmethod
    def min_time(routes: List[WorkoutRoute]) -> dt:
        return min([route.start.timestamp() for route in routes])

    @staticmethod
    def max_time(routes: List[WorkoutRoute]) -> dt:
        return max([route.end.timestamp() for route in routes])


class FilterPipeline:

    def __init__(self, filter_names: List[str], filters: List[Filter]):
        self.filter_names = filter_names
        self.filters = filters

    def filter(self, data):
        filtered_data = data

        for filter in self.filters:
            filtered_data = filter.filter(filtered_data)

        return filtered_data
