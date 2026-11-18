"""Validações desejadas: falhas aqui representam trabalho ainda pendente.

Arquivos inválidos devem causar ValueError e informar o nome do arquivo.
O lote deve parar no primeiro arquivo inválido, sem ignorá-lo silenciosamente.
"""

import re
from pathlib import Path

import pytest


def rejected_file(path):
    """Aceita subclasses de ValueError, mas exige diagnóstico com o arquivo."""
    return pytest.raises(ValueError, match=re.escape(path.name))


@pytest.mark.parametrize(
    "year",
    [None, "2024", 2024.0, True, False, [], {}, Path("2024")],
    ids=["none", "string", "float", "true", "false", "list", "dict", "path"],
)
def test_rejects_non_integer_year(extractor_factory, year):
    with pytest.raises(TypeError):
        extractor_factory(year)


@pytest.mark.parametrize("year", [-1, 0, 10000])
def test_rejects_year_outside_calendar_range(extractor_factory, year):
    with pytest.raises(ValueError):
        extractor_factory(year)


@pytest.mark.parametrize(
    "name",
    [
        "unexpected.CSV",
        "INMET_SE_SP__TEST_01-01-2024_A_31-12-2024.CSV",
        "INMET_SE_SP_A702_TEST.CSV",
        "INMET_SE_SP_A702_TEST_01-01-2024_A_invalid.CSV",
    ],
)
def test_rejects_malformed_filename(extractor, write_inmet, name):
    path = write_inmet(name=name)
    with rejected_file(path):
        list(extractor.inmet_paths())


def test_rejects_filename_year_different_from_requested_year(extractor, write_inmet):
    path = write_inmet(name="INMET_SE_SP_A702_TEST_01-01-2023_A_31-12-2023.CSV")
    with rejected_file(path):
        list(extractor.inmet_paths())


def test_rejects_duplicate_station_year_identifiers(extractor, write_inmet):
    write_inmet()
    write_inmet(name="INMET_SE_SP_A702_OTHER_01-01-2024_A_31-12-2024.CSV")
    with pytest.raises(ValueError, match="A702_2024"):
        list(extractor.inmet_paths())


def test_rejects_station_mismatch_between_filename_and_metadata(
    extractor, write_inmet, metadata_rows,
):
    metadata_rows[3][1] = "A123"
    path = write_inmet(metadata=metadata_rows)
    with rejected_file(path):
        list(extractor.inmet_dataframes())


@pytest.mark.parametrize("method", ["inmet_metadata", "inmet_dataframe"])
def test_rejects_empty_file_with_filename_in_error(extractor, write_inmet, method):
    path = write_inmet()
    path.write_bytes(b"")
    with rejected_file(path):
        getattr(extractor, method)(path)


@pytest.mark.parametrize("method", ["inmet_metadata", "inmet_dataframe"])
def test_rejects_truncated_metadata(extractor, write_inmet, metadata_rows, method):
    path = write_inmet(metadata=metadata_rows[:-1])
    with rejected_file(path):
        getattr(extractor, method)(path)


def test_rejects_extra_metadata_line(extractor, write_inmet, metadata_rows):
    path = write_inmet(metadata=[*metadata_rows, ["UNEXPECTED:", "extra"]])
    with rejected_file(path):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize("problem", ["missing_key", "duplicate_key", "empty_value"])
def test_rejects_invalid_metadata_fields(
    extractor, write_inmet, metadata_rows, problem,
):
    if problem == "missing_key":
        metadata_rows[4][0] = "UNEXPECTED:"
    elif problem == "duplicate_key":
        metadata_rows[4][0] = metadata_rows[5][0]
    else:
        metadata_rows[2][1] = ""
    path = write_inmet(metadata=metadata_rows)
    with rejected_file(path):
        extractor.inmet_metadata(path)


@pytest.mark.parametrize("literal", ["NA", "NULL", "N/A"])
def test_metadata_does_not_convert_literal_text_to_nan(
    extractor, write_inmet, metadata_rows, literal,
):
    metadata_rows[2][1] = literal
    actual = extractor.inmet_metadata(write_inmet(metadata=metadata_rows))
    assert actual.iloc[2, 1] == literal


def test_rejects_missing_observation_header(extractor, write_inmet):
    path = write_inmet()
    metadata_only = "\n".join(path.read_text(encoding="latin1").splitlines()[:8])
    path.write_text(metadata_only + "\n", encoding="latin1")
    with rejected_file(path):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize(
    "problem", ["missing_column", "unexpected_column", "duplicate_column", "extra_column"]
)
def test_rejects_invalid_observation_header(
    extractor, write_inmet, columns, observation_rows, problem,
):
    if problem == "missing_column":
        columns.pop(7)
        for row in observation_rows:
            row.pop(7)
    elif problem == "unexpected_column":
        columns[2] = "UNKNOWN MEASUREMENT"
    elif problem == "duplicate_column":
        columns[3] = columns[2]
    else:
        columns.append("EXTRA MEASUREMENT")
        for row in observation_rows:
            row.append("1")
    path = write_inmet(header=columns, rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


def test_rejects_wrong_delimiter(extractor, write_inmet):
    path = write_inmet(delimiter=",")
    with rejected_file(path):
        extractor.inmet_dataframe(path)


def test_rejects_value_in_trailing_unnamed_column(
    extractor, write_inmet, observation_rows,
):
    observation_rows[0][-1] = "42"
    path = write_inmet(rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize("value", ["abc", "1.2.3"])
def test_rejects_non_numeric_measurement(extractor, write_inmet, observation_rows, value):
    observation_rows[0][2] = value
    path = write_inmet(rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize("value", ["", "invalid-date", "2024/02/30", "2024/04/31", "2024/13/01"])
def test_rejects_invalid_date(extractor, write_inmet, observation_rows, value):
    observation_rows[0][0] = value
    path = write_inmet(rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


def test_rejects_leap_day_in_non_leap_year(
    extractor_factory, write_inmet, observation_rows,
):
    for row in observation_rows:
        row[0] = "2023/02/29"
    path = write_inmet(year=2023, rows=observation_rows)
    with rejected_file(path):
        extractor_factory(2023).inmet_dataframe(path)


@pytest.mark.parametrize("value", ["", "2500 UTC", "0060 UTC", "0030 UTC", "0000", "noon"])
def test_rejects_invalid_utc_hour(extractor, write_inmet, observation_rows, value):
    observation_rows[0][1] = value
    path = write_inmet(rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


def test_rejects_observation_from_another_year(extractor, write_inmet, observation_rows):
    observation_rows[0][0] = "2023/01/01"
    path = write_inmet(rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


def test_rejects_duplicate_timestamps(extractor, write_inmet, observation_rows):
    observation_rows[1][:2] = observation_rows[0][:2]
    path = write_inmet(rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize("problem", ["too_many_fields", "too_few_fields"])
def test_rejects_inconsistent_observation_width(
    extractor, write_inmet, observation_rows, problem,
):
    if problem == "too_many_fields":
        observation_rows[1].append("unexpected")
    else:
        observation_rows[1] = observation_rows[1][:3]
    path = write_inmet(rows=observation_rows)
    with rejected_file(path):
        extractor.inmet_dataframe(path)


def test_batch_stops_at_corrupt_file_and_reports_its_name(extractor, write_inmet):
    first = write_inmet(station="A001")
    corrupt = write_inmet(station="A002")
    write_inmet(station="A003")
    corrupt.write_bytes(b"")
    iterator = extractor.inmet_dataframes()
    identifier, path, frame = next(iterator)
    assert (identifier, path) == ("A001_2024", first)
    assert len(frame) == 2
    with rejected_file(corrupt):
        next(iterator)
