from climatelab.utils.data_paths import DataPaths
from pandas import DataFrame, read_csv

class ExtractInmet2024:

    def __init__(self):
        self._paths = DataPaths()

    def all_inmet_2024_files(self):
        pass

    def inmet_2024_dataframe(self, station: str) -> DataFrame:
        return read_csv(
        self._paths.csv_path(station),
        sep=";",
        skiprows=8,
        encoding="latin1",
        decimal=",",
        )