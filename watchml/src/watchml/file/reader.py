import logging
import os
from pathlib import Path
from typing import List
from typing import Tuple

import pandas as pd
from watchml import ECG
from watchml import WorkoutRoute

logger = logging.getLogger(__name__)


class ECGReader:
    @staticmethod
    def read_ecg_from_file(path: str) -> ECG:
        with open(path, "r") as f:
            ecg = f.read()
            values, meta_data = ECGReader.read_ecg(ecg)
            name = str(path).split("/")[-1].replace(".csv", "")
        return ECG(values, meta_data, name)

    @staticmethod
    def read_ecg(ecg) -> Tuple[List[float], dict]:
        data = ecg.split("\n")
        m_data = data[:12]
        meta_data = {}
        for m in m_data:
            if (
                m != "" and "," in m
            ):  # makes sure that the row isnt empty and that it is a key,value pair
                x = m.split(",")
                if len(x) == 3:  # if commas were used instead of points for floats
                    meta_data[x[0]] = x[1] + "." + x[2]
                else:
                    meta_data[x[0]] = x[1]

        data = data[13:]

        values = []
        for d in data:
            if d != "":
                values.append(float(d.replace(",", ".")))

        return values, meta_data


class WatchReader:
    def __init__(self, data_path: str, cache_path: Path | str | None = None):
        self.data_path = Path(data_path)
        self.cache_path = (
            Path(cache_path) if cache_path is not None else data_path / "cache"
        )

    @property
    def metadata(self):
        return pd.read_csv(self.cache_path / "metadata.csv")

    @property
    def record_types(self):
        return [file.split(".")[0] for file in os.listdir(self.cache_path / "records")]

    def ecgs(self):
        logger.info("Reading ECGs")
        ecg_filenames = os.listdir(self.data_path / "electrocardiograms")
        ecgs = []
        for file in ecg_filenames:
            with open(self.data_path / "electrocardiograms" / file, "r") as f:
                ecg = f.read()
                logger.debug(f"Reading ECG {file}")
                name = file.split(".")[0]
                values, meta_data = ECGReader.ecg_data(ecg)
            ecgs.append(ECG(values, meta_data, name))
        return ecgs

    def activity_summary(self):
        logger.info("Reading activity summary dataframe")
        return pd.read_csv(self.cache_path / "activity_summary.csv")

    def workouts(self):
        logger.info("Reading workouts dataframe")
        return pd.read_csv(self.cache_path / "workouts.csv")

    def workout_events(self):
        logger.info("Reading workout events dataframe")
        return pd.read_csv(self.cache_path / "workout_events.csv")

    def routes_meta(self):
        logger.info("Reading routes meta dataframe")
        return pd.read_csv(self.cache_path / "routes_meta.csv")

    def route(self, workout_id: str):
        logger.debug(f"Reading route for workout {workout_id}")
        return pd.read_csv(self.cache_path / "routes" / f"{workout_id}.csv")

    def routes(self) -> List[WorkoutRoute]:
        logger.info("Reading routes")
        routes = []
        for row in self.routes_meta().itertuples():
            route_df = self.route(row.workout_uuid)
            route = WorkoutRoute(
                route_df=route_df, uuid=row.workout_uuid, gpx_path=row.path
            )
            routes.append(route)
        return routes

    def workout_metadata_entry(self, workout_id: str):
        logger.debug(f"Reading workout metadata entry for workout {workout_id}")
        return pd.read_csv(
            self.cache_path / "workout_metadata_entry" / f"{workout_id}.csv"
        )

    def workout_statistics(self, workout_id: str):
        logger.debug(f"Reading workout statistics for workout {workout_id}")
        return pd.read_csv(self.cache_path / "workout_statistics" / f"{workout_id}.csv")

    def records(self):
        logger.info("Reading records")
        records = []
        for file in os.listdir(self.cache_path / "records"):
            logger.debug(f"Reading record {file}")
            records.append(pd.read_csv(self.cache_path / "records" / file))
        return records

    def record(self, record_type: str):
        logger.debug(f"Reading record {record_type}")
        return pd.read_csv(self.cache_path / "records" / f"{record_type}.csv")
