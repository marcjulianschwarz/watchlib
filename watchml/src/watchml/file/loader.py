import xml.etree.ElementTree as ET
from pathlib import Path


class WatchLoader:
    def __init__(self, data_path: str | Path, cache_path: str | Path | None = None):
        self.data_path = Path(data_path)
        self.cache_path = Path(cache_path) if cache_path else Path(data_path) / "cache"

    def load_export_root(self) -> ET.Element:
        tree = ET.parse(self.data_path / "Export.xml")
        root = tree.getroot()
        return root
