"""Contrato de estrutura do CSV e tratamento de falhas durante o lote."""

import logging
import re
from unittest.mock import patch

import pytest


@pytest.fixture
def batch_log(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


def assert_file_failure(log, path, reason):
    messages = []
    for record in log.records:
        message = record.getMessage()
        if record.exc_info:
            message = f"{message} {record.exc_info[1]}"
        if path.name in message:
            messages.append(message.replace(path.name, ""))

    assert any(re.search(reason, message, re.IGNORECASE) for message in messages), (
        f"Esperado diagnóstico com {path.name!r} e motivo compatível com {reason!r}. "
        f"Registros capturados: {log.text!r}"
    )


@pytest.mark.parametrize("method", ["inmet_metadata", "inmet_dataframe"])
def test_rejects_empty_file(extractor, write_inmet, method):
    path = write_inmet()
    path.write_bytes(b"")
    with pytest.raises(ValueError):
        getattr(extractor, method)(path)


@pytest.mark.parametrize("method", ["inmet_metadata", "inmet_dataframe"])
def test_rejects_truncated_metadata(extractor, write_inmet, metadata_rows, method):
    path = write_inmet(metadata=metadata_rows[:-1])
    with pytest.raises(ValueError):
        getattr(extractor, method)(path)


def test_rejects_extra_metadata_line(extractor, write_inmet, metadata_rows):
    path = write_inmet(metadata=[*metadata_rows, ["UNEXPECTED:", "extra"]])
    with pytest.raises(ValueError):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize(
    "replacement",
    [
        pytest.param(["UNEXPECTED:", "-23,496294"], id="missing_key"),
        pytest.param(["LONGITUDE:", "-23,496294"], id="duplicate_key"),
        pytest.param(["LATITUDE:"], id="missing_field"),
        pytest.param(["LATITUDE:", "-23,496294", "extra"], id="extra_field"),
    ],
)
def test_rejects_invalid_metadata_row(extractor, write_inmet, metadata_rows, replacement):
    metadata_rows[4] = replacement
    path = write_inmet(metadata=metadata_rows)
    with pytest.raises(ValueError):
        extractor.inmet_metadata(path)


def test_rejects_missing_observation_header(extractor, write_inmet):
    path = write_inmet()
    metadata_only = "\n".join(path.read_text(encoding="latin1").splitlines()[:8])
    path.write_text(metadata_only + "\n", encoding="latin1")
    with pytest.raises(ValueError):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize(
    "problem",
    ["missing_column", "missing_time_column", "duplicate_column", "extra_column"],
)
def test_rejects_invalid_observation_header(
    extractor, write_inmet, columns, observation_rows, problem,
):
    if problem == "missing_column":
        columns.pop(7)
        for row in observation_rows:
            row.pop(7)
    elif problem == "missing_time_column":
        columns[1] = "UNKNOWN TEMPORAL FIELD"
    elif problem == "duplicate_column":
        columns[3] = columns[2]
    else:
        columns.insert(-1, "EXTRA MEASUREMENT")
        for row in observation_rows:
            row.insert(-1, "1")
    path = write_inmet(header=columns, rows=observation_rows)
    with pytest.raises(ValueError):
        extractor.inmet_dataframe(path)


def test_rejects_wrong_delimiter(extractor, write_inmet):
    path = write_inmet(delimiter=",")
    with pytest.raises(ValueError):
        extractor.inmet_dataframe(path)


def test_rejects_value_in_trailing_unnamed_column(
    extractor, write_inmet, observation_rows,
):
    observation_rows[0][-1] = "42"
    path = write_inmet(rows=observation_rows)
    with pytest.raises(ValueError):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize("problem", ["too_many_fields", "too_few_fields"])
def test_rejects_inconsistent_observation_width(
    extractor, write_inmet, observation_rows, problem,
):
    if problem == "too_many_fields":
        observation_rows[1].append("unexpected")
    else:
        observation_rows[1].pop(-2)
    path = write_inmet(rows=observation_rows)
    with pytest.raises(ValueError):
        extractor.inmet_dataframe(path)


@pytest.mark.parametrize(
    ("problem", "reason"),
    [
        pytest.param("row_width", r"colun|column|campo|field|largura|width", id="row_width"),
        pytest.param("metadata", r"metadad|metadata|chave|key|duplic|repet", id="metadata"),
    ],
)
def test_batch_continues_after_malformed_csv(
    extractor, write_inmet, observation_rows, metadata_rows, batch_log, problem, reason,
):
    last = write_inmet(station="A003", rows=observation_rows[:1])
    first = write_inmet(station="A001")
    if problem == "row_width":
        observation_rows[1].append("unexpected")
    else:
        metadata_rows[4][0] = metadata_rows[5][0]
    metadata_rows[3][1] = "A002"
    corrupt = write_inmet(station="A002", rows=observation_rows, metadata=metadata_rows)

    results = [
        (identifier, path, frame["Hora UTC"].tolist())
        for identifier, path, frame in extractor.inmet_dataframes()
    ]

    assert results == [
        ("A001_2024", first, ["0000 UTC", "0100 UTC"]),
        ("A003_2024", last, ["0000 UTC"]),
    ]
    assert_file_failure(batch_log, corrupt, reason)


def test_batch_with_only_invalid_files_reports_each_failure(
    extractor, write_inmet, batch_log,
):
    empty = write_inmet(station="A001")
    empty.write_bytes(b"")
    wrong_delimiter = write_inmet(station="A002", delimiter=",")

    assert list(extractor.inmet_dataframes()) == []

    assert_file_failure(batch_log, empty, r"vazi[oa]|empty|no columns to parse")
    assert_file_failure(
        batch_log, wrong_delimiter, r"delimit|separador|separator|cabeçalho|header|colun|column"
    )


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("A002.CSV", id="short_name"),
        pytest.param(
            "INMET_SE_RJ__TEST_01-01-2024_A_31-12-2024.CSV", id="missing_station"
        ),
        pytest.param("INMET_SE_SP_A002_TEST.CSV", id="missing_year"),
        pytest.param(
            "INMET_SE_SP_A002_TEST_01-01-2024_A_invalid.CSV", id="invalid_year"
        ),
    ],
)
def test_batch_continues_after_malformed_filename(
    extractor, write_inmet, batch_log, name,
):
    invalid = write_inmet(station="A002", name=name)
    valid = write_inmet(station="A003")
    results = list(extractor.inmet_dataframes())

    assert [(identifier, path) for identifier, path, _ in results] == [
        ("A003_2024", valid),
    ]
    assert_file_failure(
        batch_log, invalid, r"nome|file\s*name|estaç[aã]o|station|identific|padr[aã]o|ano|year"
    )


def test_batch_rejects_filename_year_different_from_requested_year(
    extractor, write_inmet, batch_log,
):
    valid = write_inmet(station="A003")
    misplaced = write_inmet(year=2023, station="A002")
    misplaced = misplaced.rename(valid.parent / misplaced.name)

    results = list(extractor.inmet_dataframes())

    assert [(identifier, path) for identifier, path, _ in results] == [
        ("A003_2024", valid),
    ]
    assert_file_failure(batch_log, misplaced, r"\bano\b|\byear\b|2023.*2024|2024.*2023")


def test_batch_does_not_deliver_duplicate_station_year_identifiers(
    extractor, write_inmet, batch_log,
):
    first = write_inmet(station="A001")
    other = write_inmet(
        station="A001", name="INMET_SE_SP_A001_OTHER_01-01-2024_A_31-12-2024.CSV"
    )
    unrelated = write_inmet(station="A002")

    results = [(identifier, path) for identifier, path, _ in extractor.inmet_dataframes()]

    assert [result for result in results if result[0] != "A001_2024"] == [
        ("A002_2024", unrelated),
    ]
    delivered = [path for identifier, path in results if identifier == "A001_2024"]
    assert len(delivered) <= 1, f"Identificador A001_2024 repetido: {delivered!r}"
    assert set(delivered) <= {first, other}
    for excluded in {first, other}.difference(delivered):
        assert_file_failure(batch_log, excluded, r"duplic|repet|colis|já existe|already exists")


@pytest.mark.parametrize(
    "expected_error",
    [
        pytest.param(FileNotFoundError, id="missing_year"),
        pytest.param(NotADirectoryError, id="year_is_a_file"),
    ],
)
def test_batch_propagates_invalid_year_directory(extractor, inmet_root, expected_error):
    if expected_error is NotADirectoryError:
        (inmet_root / "2024").write_text("not a directory")

    with pytest.raises(expected_error):
        list(extractor.inmet_dataframes())


def test_batch_reads_on_demand_when_skipping_invalid_file(
    extractor, write_inmet, batch_log,
):
    first = write_inmet(station="A001")
    empty = write_inmet(station="A002")
    empty.write_bytes(b"")
    last = write_inmet(station="A003")

    with patch.object(extractor, "inmet_dataframe", wraps=extractor.inmet_dataframe) as read:
        iterator = extractor.inmet_dataframes()
        read.assert_not_called()
        assert next(iterator)[:2] == ("A001_2024", first)
        read.assert_called_once_with(first)

        assert next(iterator)[:2] == ("A003_2024", last)
        assert read.call_args.args == (last,)
        assert_file_failure(batch_log, empty, r"vazi[oa]|empty|no columns to parse")
        with pytest.raises(StopIteration):
            next(iterator)
