from typing import Tuple
import pandas as pd
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime as dt


class ECG:

    def __init__(self, data: str, name: str):
        self.data, self.meta_data = self.read_ecg(data)
        self.name = name
        self.x = [xx for xx in range(0, len(self.data))]
        self.y = self.data

    def read_ecg(self, ecg: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        data = ecg.split("\n")
        m_data = data[:12]
        meta_data = {}
        for m in m_data:
            if m != "" and "," in m: # makes sure that the row isnt empty and that it is a key,value pair
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

        #print(meta_data)

        return values, meta_data


    def __getitem__(self, key):
        return self.meta_data[key]


class ECGWave(ABC):

    normal_duration_range: Tuple[float, float]
    normal_amplitude_range: Tuple[float, float]
    wave_data: pd.DataFrame

    def __init__(self):
        pass

    @abstractmethod
    def duration(self):
        raise NotImplementedError

    @abstractmethod
    def amplitude(self):
        raise NotImplementedError

    @abstractmethod
    def rate(self):
        raise NotImplementedError


class PWave(ECGWave):
    def __init__(self):
        pass


class QWave(ECGWave):
    def __init__(self):
        pass


class RWave(ECGWave):
    def __init__(self):
        pass


class SWave(ECGWave):
    def __init__(self):
        super().__init__()


class TWave(ECGWave):
    def __init__(self):
        super().__init__()


class QRSComplex:

    qwave: QWave
    rwave: RWave
    swave: SWave

    def __init__(self, qwave: QWave, rwave: RWave, swave: SWave) -> None:
        self.qwave = qwave
        self.rwave = rwave
        self.swave = swave

    def rate(self):
        raise NotImplementedError


class WorkoutRoute:

    route: pd.DataFrame
    name: str

    start: dt
    end: dt
    duration_sec: float

    def __init__(self, data, name: str):
        if isinstance(data, pd.DataFrame):
            self.route = data
        elif isinstance(data, ET.Element):
            self.route = self.__read_route(data)
        else:
            raise ValueError("This workout type does not exist")

        self.name = name
        start, end, time = self.__times()
        self.start = start
        self.end = end
        self.duration_sec = time

    def __getitem__(self, key):
        return self.route[key]

    @property
    def lon(self):
        return self.route["lon"]

    @property
    def lat(self):
        return self.route["lat"]

    @property
    def time(self):
        return self.route["time"]

    @property
    def elevation(self):
        return self.route["elevation"]

    @property
    def speed(self):
        return self.route["speed"]

    @property
    def course(self):
        return self.route["course"]

    @property
    def hAcc(self):
        return self.route["hAcc"]

    @property
    def vAcc(self):
        return self.route["vAcc"]

    def __times(self):
        if not self["time"].empty:
            start = self["time"].iloc[0]
            end = self["time"].iloc[-1]
            start = dt.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
            end = dt.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
            time = (end - start).total_seconds()

            return start, end, time
        else:
            return None, None, 0

    def __read_route(self, data: ET.Element) -> pd.DataFrame:

        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
        tracks = data.findall('gpx:trk', ns)

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

                    elevation = track_point.find('gpx:ele', ns).text
                    time = track_point.find('gpx:time', ns).text
                    extension = track_point.find('gpx:extensions', ns)

                    lon = track_point.get("lon")
                    lat = track_point.get("lat")
                    speed = extension.find('gpx:speed', ns).text
                    course = extension.find('gpx:course', ns).text
                    hAcc = extension.find('gpx:hAcc', ns).text
                    vAcc = extension.find('gpx:vAcc', ns).text

                    data["lon"].append(float(lon))
                    data["lat"].append(float(lat))
                    data["elevation"].append(float(elevation))
                    data["time"].append(time)
                    data["speed"].append(float(speed))
                    data["course"].append(float(course))
                    data["hAcc"].append(float(hAcc))
                    data["vAcc"].append(float(vAcc))

        return pd.DataFrame(data)
