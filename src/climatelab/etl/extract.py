from climatelab.utils.data_paths import DataPaths
from pandas import DataFrame, read_csv
from pathlib import Path
from typing import Iterator

class ExtractInmet:

    def __init__(self, year: int):
        self._paths = DataPaths()
        self._year = year

    def inmet_dataframes(self) -> Iterator[tuple[str, Path, DataFrame]]:
        directory = self.inmet_paths()
        for identifier, file in directory:
            data = self.inmet_dataframe(file)
            yield identifier, file, data
        

    def inmet_paths(self) -> Iterator[tuple[str, Path]]:
        files = self._paths.csv_paths(self._year)
        for file in files:
            partes = file.stem.split("_")
            code_station = partes[3]
            file_year = partes[-1][-4:]

            identifier = f"{code_station}_{file_year}"

            yield identifier, file


    def inmet_metadata(self, file: Path) -> DataFrame:
        return read_csv(
            file,
            sep=";",
            nrows=8,
            header=None,
            encoding="latin1",
            dtype=str,
        )
    
    def inmet_dataframe(self, file: Path) -> DataFrame:
        return read_csv(
            file,
            sep=";",
            skiprows=8,
            encoding="latin1",
        decimal=",",
        )