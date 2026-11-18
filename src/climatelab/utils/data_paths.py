from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataPaths:
    inmet: Path = Path("data/raw/inmet")
    processed: Path = Path("data/processed")

    def csv_paths(self, year: int) -> list[Path]:
        folder = self.inmet / str(year)

        return sorted(
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".csv"
        )