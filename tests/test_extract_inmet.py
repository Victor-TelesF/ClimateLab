"""Contrato de leitura bruta: preservar os dados e carregar sob demanda."""

from unittest.mock import patch

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal


def test_metadata_preserves_all_eight_fields_as_strings(
    extractor, write_inmet, metadata_rows,
):
    actual = extractor.inmet_metadata(write_inmet())
    assert_frame_equal(actual, pd.DataFrame(metadata_rows), check_dtype=False)
    assert all(isinstance(value, str) for value in actual.to_numpy().flat)


def test_observations_match_independent_expected_values(extractor, write_inmet, columns):
    expected = pd.DataFrame(
        [
            [
                "2024/01/01", "0000 UTC", 0, 951.9, 952.1, 951.3, 0,
                23.6, 21, 24.1, 23.5, 21.5, 20.8, 86, 83, 85, 103, 8.4, 3.5,
                float("nan"),
            ],
            [
                "2024/01/01", "0100 UTC", 1.2, float("nan"), 952.2, 951.4,
                float("nan"), -2.5, -3, -2, -4, -2.8, -3.2, 90, 87, 89,
                120, 4.2, 1.7, float("nan"),
            ],
        ],
        columns=[*columns[:-1], "Unnamed: 19"],
    )
    assert_frame_equal(
        extractor.inmet_dataframe(write_inmet()), expected, check_dtype=False
    )


def test_latin1_accents_are_preserved(extractor, write_inmet):
    path = write_inmet()
    assert extractor.inmet_metadata(path).iloc[2, 1] == "SÃO PAULO - MIRANTE"
    assert "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)" in extractor.inmet_dataframe(path)


def test_missing_measurements_are_not_replaced_with_zero(extractor, write_inmet):
    frame = extractor.inmet_dataframe(write_inmet())
    assert frame.iloc[0, 2] == 0
    assert pd.isna(frame.iloc[1, 3])
    assert pd.isna(frame.iloc[1, 6])


def test_accepts_a_row_without_any_measurements(extractor, write_inmet):
    path = write_inmet(rows=[["2024/01/01", "0000 UTC", *[""] * 18]])
    frame = extractor.inmet_dataframe(path)
    assert len(frame) == 1
    assert frame.iloc[:, 2:].isna().all().all()


def test_accepts_header_without_the_trailing_empty_column(
    extractor, write_inmet, columns, observation_rows,
):
    path = write_inmet(
        header=columns[:-1], rows=[row[:-1] for row in observation_rows]
    )
    frame = extractor.inmet_dataframe(path)
    assert frame.shape == (2, 19)
    assert list(frame.columns) == columns[:-1]
    assert frame.iloc[1, 7] == -2.5


def test_accepts_valid_leap_day(extractor, write_inmet, observation_rows):
    for row in observation_rows:
        row[0] = "2024/02/29"
    frame = extractor.inmet_dataframe(write_inmet(rows=observation_rows))
    assert frame["Data"].tolist() == ["2024/02/29", "2024/02/29"]


@pytest.mark.parametrize("year", [2023, 2024, 2025])
def test_year_parameter_is_not_hardcoded(extractor_factory, write_inmet, year):
    path = write_inmet(year=year)
    identifier, actual_path, frame = next(extractor_factory(year).inmet_dataframes())
    assert identifier == f"A702_{year}"
    assert actual_path == path
    assert frame["Data"].tolist() == [f"{year}/01/01"] * 2


def test_paths_keep_station_identifier_and_sorted_order(extractor, write_inmet):
    last = write_inmet(station="A702")
    first = write_inmet(station="A001")
    assert list(extractor.inmet_paths()) == [("A001_2024", first), ("A702_2024", last)]


def test_station_name_can_contain_underscores(extractor, write_inmet):
    path = write_inmet(
        name="INMET_SE_SP_A702_SAO_PAULO_MIRANTE_01-01-2024_A_31-12-2024.CSV"
    )
    assert list(extractor.inmet_paths()) == [("A702_2024", path)]


def test_dataframe_iteration_returns_every_file(extractor, write_inmet):
    last = write_inmet(station="A702")
    first = write_inmet(station="A001")
    results = list(extractor.inmet_dataframes())
    assert [(identifier, path) for identifier, path, _ in results] == [
        ("A001_2024", first), ("A702_2024", last),
    ]
    for _, path, frame in results:
        assert_frame_equal(frame, extractor.inmet_dataframe(path))


def test_dataframes_are_read_only_as_the_iterator_is_consumed(extractor, write_inmet):
    first = write_inmet(station="A001")
    last = write_inmet(station="A702")
    with patch.object(extractor, "inmet_dataframe", wraps=extractor.inmet_dataframe) as read:
        iterator = extractor.inmet_dataframes()
        read.assert_not_called()
        next(iterator)
        read.assert_called_once_with(first)
        next(iterator)
        assert read.call_count == 2
        assert read.call_args.args == (last,)
        with pytest.raises(StopIteration):
            next(iterator)


def test_empty_year_has_no_paths_or_dataframes(extractor, inmet_root):
    (inmet_root / "2024").mkdir()
    assert list(extractor.inmet_paths()) == []
    assert list(extractor.inmet_dataframes()) == []


@pytest.mark.parametrize("method", ["inmet_metadata", "inmet_dataframe"])
def test_missing_file_raises_file_not_found(extractor, tmp_path, method):
    with pytest.raises(FileNotFoundError):
        getattr(extractor, method)(tmp_path / "missing.CSV")


@pytest.mark.parametrize("method", ["inmet_metadata", "inmet_dataframe"])
def test_directory_instead_of_csv_raises_is_a_directory(extractor, tmp_path, method):
    with pytest.raises(IsADirectoryError):
        getattr(extractor, method)(tmp_path)


def test_missing_year_raises_file_not_found(extractor):
    with pytest.raises(FileNotFoundError):
        list(extractor.inmet_paths())
