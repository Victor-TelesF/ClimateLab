from climatelab.utils.data_paths import DataPaths
from pandas import DataFrame, read_csv, errors
from pathlib import Path
from typing import Iterator
from climatelab.exceptions.inmet_exception import EmptyInmetFileError, InvalidInmetFilenameError

class ExtractInmet:

    def __init__(self, year: int):
        self._paths = DataPaths()
        self._year = year
        self._registry_errors = {}

    @property
    def registry_erros(self) -> dict:
        return self._registry_errors

    def inmet_paths(self) -> Iterator[tuple[str, Path]]:

        files = self._paths.csv_paths(self._year)

        for file in files:
            
            partes = file.stem.split("_")
            code_station = partes[3]
            file_year = partes[-1][-4:]
            identifier = f"{code_station}_{file_year}"
            
            yield identifier, file

    def inmet_dataframes(self) -> Iterator[tuple[str, Path, DataFrame]]:
        directory = self.inmet_paths()
        for identifier, file in directory:
            try:
                data = self.inmet_dataframe(file)
            except Exception as e:
                self._registry_errors[file] = e
                continue
            yield identifier, file, data

        

    def inmet_metadata(self, file: Path) -> DataFrame:
        try:

            data = read_csv(
                file,
                sep=";",
                nrows=8,
                header=None,
                encoding="latin1",
                dtype=str,
            )
        except (errors.EmptyDataError, errors.ParserError) as e:
            self._registry_errors[file] = e

        return data
    
    def inmet_dataframe(self, file: Path) -> DataFrame:
        try:
            data = read_csv(
                file,
                sep=";",
                skiprows=8,
                encoding="latin1",
            decimal=",",
            )
        except (errors.EmptyDataError, errors.ParserError) as e:
            self._registry_errors[file] = e

        return data