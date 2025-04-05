import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4

import pandas as pd

from .file import FileSystemManager

WorkoutElement = ET.Element


class WatchWriter:
    def __init__(self, data_path: str | Path, cache_path: str | Path | None = None):
        self.data_path = Path(data_path)
        self.cache_path = Path(cache_path) if cache_path else Path(data_path) / "cache"

    def scaffold_folder_structure(self):
        paths = [
            self.cache_path,
            self.cache_path / "workout_statistics",
            self.cache_path / "routes",
            self.cache_path / "workout_metadata_entries",
            self.cache_path / "records",
        ]

        # Only create the cache folder structure if it doesn't exist yet
        if not self.cache_path.exists():
            FileSystemManager.scaffold_paths(paths)

    def write_record_files(self, record_df: pd.DataFrame):
        unique_record_types = record_df["type"].unique()
        for record_type in unique_record_types:
            record_sub_df = record_df.loc[record_df["type"] == record_type]
            FileSystemManager.to_processed(
                path=self.cache_path / "records", df=record_sub_df, name=record_type
            )

    def write_full_record_file(self, record_df: pd.DataFrame):
        record_df.to_csv(self.cache_path / "records.csv", index=False)

    def _write_workout_event_file_for(self, workout, workout_id: str):
        events = workout.findall("WorkoutEvent")
        event_attributes = []
        for event in events:
            event.attrib["workout_uuid"] = workout_id
        event_attribs = [event.attrib for event in events]
        event_attributes.extend(event_attribs)

        events_df = pd.DataFrame(event_attributes)
        FileSystemManager.to_processed(
            path=self.cache_path, df=events_df, name="workout_events"
        )

    def _write_statistics_file_for(self, workout, workout_id: str):
        statistics = workout.findall("WorkoutStatistics")
        statistic_attribs = [statistic.attrib for statistic in statistics]
        statistic_df = pd.DataFrame(statistic_attribs)
        FileSystemManager.to_processed(
            path=self.cache_path / "workout_statistics",
            df=statistic_df,
            name=workout_id,
        )

    def _write_meta_data_entry_file_for(self, workout, workout_id: str):
        metadata_entries = workout.findall("WorkoutMetadataEntry")
        metadata_entry_attribs = [
            {metadata_entry.attrib["key"]: metadata_entry.attrib["value"]}
            for metadata_entry in metadata_entries
        ]
        metadata_entry_df = pd.DataFrame(metadata_entry_attribs)
        FileSystemManager.to_processed(
            path=self.cache_path / "workout_metadata_entries",
            df=metadata_entry_df,
            name=workout_id,
        )

    def _write_route_files_for(self, route_root, workout_id: str):
        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
        routes = route_root.findall("gpx:trk", ns)

        route_data = {
            "lon": [],
            "lat": [],
            "time": [],
            "elevation": [],
            "speed": [],
            "course": [],
            "hAcc": [],
            "vAcc": [],
        }

        for route in routes:
            route_segments = route.findall("gpx:trkseg", ns)
            for route_segment in route_segments:
                route_points = route_segment.findall("gpx:trkpt", ns)
                for route_point in route_points:
                    elevation = route_point.find("gpx:ele", ns).text
                    time = route_point.find("gpx:time", ns).text

                    # contains information about speed, course and acceleration
                    extension = route_point.find("gpx:extensions", ns)

                    lon = route_point.get("lon")
                    lat = route_point.get("lat")
                    speed = extension.find("gpx:speed", ns).text
                    course = extension.find("gpx:course", ns).text
                    hAcc = extension.find("gpx:hAcc", ns).text
                    vAcc = extension.find("gpx:vAcc", ns).text

                    route_data["lon"].append(float(lon))
                    route_data["lat"].append(float(lat))
                    route_data["elevation"].append(float(elevation))
                    route_data["time"].append(time)
                    route_data["speed"].append(float(speed))
                    route_data["course"].append(float(course))
                    route_data["hAcc"].append(float(hAcc))
                    route_data["vAcc"].append(float(vAcc))

        route_df = pd.DataFrame(route_data)
        FileSystemManager.to_processed(
            path=self.cache_path / "routes", df=route_df, name=workout_id
        )

    def write_workout_files(self, root: ET.Element):
        workout_attributes = []
        route_attributes = []
        workouts = root.findall("Workout")

        for workout in workouts:
            # Generate unique id for each workout to be able to join workouts with events, routes, etc.
            workout_id = uuid4()
            workout.attrib["uuid"] = workout_id
            workout_attributes.append(workout.attrib)

            self._write_workout_event_file_for(workout, workout_id)

            routes = workout.findall("WorkoutRoute")

            for route in routes:
                route.attrib["workout_uuid"] = workout_id
                file_ref = route.find("FileReference")
                if file_ref is not None:
                    route_path = file_ref.attrib["path"]
                    route.attrib["path"] = route_path
                    route_path = self.data_path / route_path[1:]
                    route_tree = ET.parse(route_path)
                    route_root = route_tree.getroot()

                    self._write_route_files_for(route_root, workout_id)

            route_attribs = [route.attrib for route in routes]
            route_attributes.extend(route_attribs)

            self._write_statistics_file_for(workout, workout_id)
            self._write_meta_data_entry_file_for(workout, workout_id)

        workouts_df = pd.DataFrame(workout_attributes)
        routes_meta_df = pd.DataFrame(route_attributes)

        FileSystemManager.to_processed(
            path=self.cache_path, df=workouts_df, name="workouts"
        )
        FileSystemManager.to_processed(
            path=self.cache_path, df=routes_meta_df, name="routes_meta"
        )

    def _load_full_record_df(self, root: ET.Element) -> pd.DataFrame:
        records = root.findall("Record")
        record_attribs = [record.attrib for record in records]
        record_df = pd.DataFrame(record_attribs)
        return record_df

    def write_metadata(self, root: ET.Element):
        locale = root.attrib["locale"]
        metadata_node = root.find("Me").attrib
        export_date = root.find("ExportDate").attrib["value"]

        metadata_df = pd.DataFrame(metadata_node, index=[0])
        metadata_df["locale"] = locale
        metadata_df["export_date"] = export_date
        FileSystemManager.to_processed(
            path=self.cache_path, df=metadata_df, name="metadata"
        )

    def write_activity_summary(self, root: ET.Element):
        activity_summary_nodes = root.findall("ActivitySummary")
        activity_summary_attributes = [
            activity_summary_node.attrib
            for activity_summary_node in activity_summary_nodes
        ]
        activity_summary_df = pd.DataFrame(activity_summary_attributes)
        FileSystemManager.to_processed(
            path=self.cache_path, df=activity_summary_df, name="activity_summary"
        )

    def write_all(self, root: ET.Element):
        self.write_metadata(root)
        self.write_activity_summary(root)
        full_record_df = self._load_full_record_df(root)
        self.write_record_files(full_record_df)
        self.write_full_record_file(full_record_df)
        self.write_workout_files(root)
