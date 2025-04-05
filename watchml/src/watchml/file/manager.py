import json
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from pathlib import Path

from .file import FileSystemManager
from .loader import WatchLoader
from .writer import WatchWriter


class WatchManager:
    def __init__(
        self, data_path: Path | str, cache_path: Path | str | None = None
    ) -> None:
        self.loader = WatchLoader(data_path=data_path, cache_path=cache_path)
        self.writer = WatchWriter(data_path=data_path, cache_path=cache_path)
        self.data_path = Path(data_path)
        self.cache_path = (
            Path(cache_path) if cache_path is not None else data_path / "cache"
        )

    def delete_old_data(self):
        FileSystemManager.delete_files_in(self.cache_path / "workout_statistics")
        FileSystemManager.delete_files_in(self.cache_path / "routes")
        FileSystemManager.delete_files_in(self.cache_path / "workout_metadata_entry")

    def update_cache_info(self):
        if not self.cache_path.exists():
            self.writer.scaffold_folder_structure()

        with open(self.cache_path / "cache.json", "w") as f:
            content = {
                "last_updated": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            f.write(json.dumps(content))

    def reload_data(self, root: ET.Element = None):
        self.writer.scaffold_folder_structure()

        if root is None:
            print("Reading Export.xml file...")
            root = self.loader.load_export_root()

        self.update_cache_info()
        # self.delete_old_data()

        self.writer.write_all(root=root)
