import xml.etree.ElementTree as ET
import pandas as pd
import os

class DataLoader:
    
    def __init__(self, path: str) -> None:
        self.path = path
        self.export_path = path + "/Export.xml"
        self.ecg_path = path + "/electrocardiograms/"

    def get_export_data(self) -> dict:

        tree = ET.parse(self.export_path)
        root = tree.getroot()

        records = root.findall('Record')

        d = {}

        for x in records:
            d[x.get("type")] = []

        for record in records:
            d[record.get("type")].append(record.get("value"))

        return d


    def get_ecgs(self):

        ecgs = [pd.read_csv(self.ecg_path + filename) for filename in os.listdir(self.ecg_path)]
        return ecgs

    def read_ecg(self, ecg: pd.DataFrame):

        name = ecg.columns[1]
        ecg = ecg.rename(columns = {ecg.columns[0]: "name", ecg.columns[1]: "value"})

        meta_data = ecg.iloc[:9]
        meta_data = dict(zip(meta_data.name, meta_data.value))
        meta_data["name"] = name

        data = ecg[9:].dropna().astype("int32")

        return meta_data, data