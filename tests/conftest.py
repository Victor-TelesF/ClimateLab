"""CSVs artificiais: nenhum teste precisa dos arquivos meteorológicos locais."""

import csv

import pytest

import climatelab.etl.extract as extract_module
from climatelab.utils.data_paths import DataPaths


@pytest.fixture
def inmet_root(tmp_path):
    root = tmp_path / "inmet"
    root.mkdir()
    return root


@pytest.fixture
def extractor_factory(monkeypatch, inmet_root):
    # Só redireciona a origem dos arquivos. O parser e a classe são os reais.
    monkeypatch.setattr(
        extract_module, "DataPaths", lambda: DataPaths(inmet=inmet_root)
    )
    return extract_module.ExtractInmet


@pytest.fixture
def extractor(extractor_factory, inmet_root):
    # As leituras diretas recebem o caminho do CSV explicitamente.
    (inmet_root / "2024").mkdir()
    return extractor_factory(2024)


@pytest.fixture
def metadata_rows():
    return [
        ["REGIAO:", "SE"],
        ["UF:", "SP"],
        ["ESTACAO:", "SÃO PAULO - MIRANTE"],
        ["CODIGO (WMO):", "A702"],
        ["LATITUDE:", "-23,496294"],
        ["LONGITUDE:", "-46,620088"],
        ["ALTITUDE:", "792,06"],
        ["DATA DE FUNDACAO:", "07/05/00"],
    ]


@pytest.fixture
def columns():
    # Cabeçalho independente de ColumnName e da implementação do extrator.
    return [
        "Data",
        "Hora UTC",
        "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
        "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)",
        "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)",
        "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)",
        "RADIACAO GLOBAL (Kj/m²)",
        "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
        "TEMPERATURA DO PONTO DE ORVALHO (°C)",
        "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)",
        "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)",
        "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)",
        "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)",
        "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)",
        "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)",
        "UMIDADE RELATIVA DO AR, HORARIA (%)",
        "VENTO, DIREÇÃO HORARIA (gr) (° (gr))",
        "VENTO, RAJADA MAXIMA (m/s)",
        "VENTO, VELOCIDADE HORARIA (m/s)",
        "",
    ]


@pytest.fixture
def observation_rows():
    return [
        [
            "2024/01/01", "0000 UTC", "0", "951,9", "952,1", "951,3",
            "0", "23,6", "21", "24,1", "23,5", "21,5", "20,8",
            "86", "83", "85", "103", "8,4", "3,5", "",
        ],
        [
            "2024/01/01", "0100 UTC", "1,2", "", "952,2", "951,4",
            "", "-2,5", "-3", "-2", "-4", "-2,8", "-3,2",
            "90", "87", "89", "120", "4,2", "1,7", "",
        ],
    ]


@pytest.fixture
def write_inmet(inmet_root, metadata_rows, columns, observation_rows):
    def write(
        *, year=2024, station="A702", name=None, metadata=None,
        header=None, rows=None, delimiter=";",
    ):
        folder = inmet_root / str(year)
        folder.mkdir(parents=True, exist_ok=True)
        filename = name or (
            f"INMET_SE_SP_{station}_SAO PAULO - MIRANTE_"
            f"01-01-{year}_A_31-12-{year}.CSV"
        )
        path = folder / filename
        if metadata is None:
            metadata = [row.copy() for row in metadata_rows]
            metadata[3][1] = station
        if rows is None:
            rows = [row.copy() for row in observation_rows]
            for row in rows:
                row[0] = f"{year}/01/01"
        with path.open("w", encoding="latin1", newline="") as stream:
            writer = csv.writer(stream, delimiter=delimiter)
            writer.writerows(metadata)
            writer.writerow(columns if header is None else header)
            writer.writerows(rows)
        return path

    return write
