from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataPaths:
    inmet: Path = Path("data/raw/inmet")
    processed: Path = Path("data/processed")

    def csv_path(self, station_code: str, year: int = 2024) -> Path:
        folder = self.inmet / str(year)

        matches = sorted(
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".csv"
            and f"_{station_code}_" in path.stem
        )

        if len(matches) != 1:
            raise ValueError(
                f"Esperado 1 CSV para {station_code} em {year}; "
                f"encontrados {len(matches)}."
            )

        return matches[0]