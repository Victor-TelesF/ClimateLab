from pandas import DataFrame, read_csv
from pandas.errors import ParserError, EmptyDataError
from pathlib import Path
from typing import Iterator
from datetime import datetime
import re

import logging
from climatelab.utils.data_paths import DataPaths
from climatelab.exceptions.inmet_exception import (
    EmptyInmetFileError, InvalidInmetFilenameError, 
    InmetYearMismatchError, InvalidInmetSchemaError,
    InvalidInmetCsvStructureError, DuplicateInmetStationYearError,
    InvalidInmetDateError, InvalidInmetDateRangeError, NoInmetFilesFoundError
    )


logger = logging.getLogger(__name__)

class ExtractInmet:

    def __init__(self, year: int):

        self._data_paths = DataPaths()
        self._year = year
        self._paths = self._data_paths.csv_paths(year)
        
    @property
    def data_paths(self) -> DataPaths:
        return self._data_paths

    @property
    def paths(self) -> list[Path]:
        return self._paths

    @property
    def year(self) -> int:
        return self._year 


    def _validate_filename(self, file: Path) -> str:

        formato = "%d-%m-%Y"
        
        partes = file.stem.split("_")

        if len(partes) < 8:
            raise InvalidInmetFilenameError("Nome menor que o padrão")
            
        code_station = partes[3]
        if not re.fullmatch(r"[A-Z][0-9]{3}", code_station):
            raise InvalidInmetFilenameError(
                f"Código de estação inválido: {code_station}"
            )

        try:

            data_inicial = datetime.strptime(partes[5], formato)
            data_final = datetime.strptime(partes[-1], formato)
        except ValueError as e:
            raise InvalidInmetDateError(
                "Data inválida no nome do arquivo"
                ) from e
    
        if data_inicial > data_final:
            raise InvalidInmetDateRangeError("Data inicial maior que a final")

        
        file_year = data_final.year

        if file_year != self.year:
            raise InmetYearMismatchError("Data do arquivo não bate com a data solicitada")

        
        return f"{code_station}_{file_year}"




    def inmet_paths(self) -> Iterator[tuple[str, Path]]:

        files = self.paths
        if not files:
            raise NoInmetFilesFoundError(
            f"Nenhum CSV disponível para {self.year}"
        )
        
        for file in files:
            try:
                identifier = self._validate_filename(file)
            except (
                InvalidInmetFilenameError,
                InvalidInmetDateRangeError,
                InvalidInmetDateError,
                InmetYearMismatchError
            ) as error:
                logger.warning(
                    "Arquivo ignorado | arquivo=%s | erro=%s | motivo=%s", 
                    file.name,
                    type(error).__name__,
                    error
                    )
                continue
            
            yield identifier, file


    def inmet_dataframes(self) -> Iterator[tuple[str, Path, DataFrame]]:
        directory = self.inmet_paths()
        for identifier, file in directory:
            
            file_dataframe = self.inmet_dataframe(file)
            file_metadata = self.inmet_metadata(file)

            yield identifier, file, file_dataframe

        

    def inmet_metadata(self, file: Path) -> DataFrame:
        
        data = read_csv(
            file,
            sep=";",
            nrows=8,
            header=None,
            encoding="latin1",
            dtype=str,
        )
    
        return data
    
    def inmet_dataframe(self, file: Path) -> DataFrame:
        
        data = read_csv(
            file,
            sep=";",
            skiprows=8,
            encoding="latin1",
        decimal=",",
        )

        return data