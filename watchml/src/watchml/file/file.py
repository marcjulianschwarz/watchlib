import os
from pathlib import Path
from typing import List

import pandas as pd


class FileSystemManager:
    """Class to manage file system operations."""

    @staticmethod
    def scaffold_paths(paths: List[Path | str]):
        """
        Creates a folder structure.

        Parameters
        ----------
        paths : List[Path | str]
            List of paths to create.
        """

        for path in paths:
            if not os.path.exists(path):
                os.mkdir(path)

    @staticmethod
    def to_processed(path: Path | str, df: pd.DataFrame, name: str):
        """
        Writes a DataFrame to a csv file.

        Parameters
        ----------
        path : Path | str
            Path to the folder.
        df : pd.DataFrame
            DataFrame to write.
        name : str
            Name of the file.
        """
        df.to_csv(path / f"{name}.csv", index=False)

    @staticmethod
    def delete_files_in(path: Path | str):
        """
        Deletes all files in a folder.

        Parameters
        ----------
        path : Path | str
            Path to the folder.
        """
        path = Path(path)
        if not path.exists():
            return
        for file in os.listdir(path):
            print(f"Deleting {file}")
            os.remove(path / file)
