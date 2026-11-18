"""Descoberta de arquivos, sem depender do diretório de execução."""

import pytest

from climatelab.utils.data_paths import DataPaths


def test_finds_csv_extensions_case_insensitively(inmet_root, write_inmet):
    paths = [
        write_inmet(name=f"station{suffix}") for suffix in (".csv", ".CSV", ".CsV")
    ]
    assert DataPaths(inmet=inmet_root).csv_paths(2024) == sorted(paths)


def test_ignores_other_extensions_and_directories(inmet_root, write_inmet):
    expected = write_inmet()
    expected.with_name("notes.txt").write_text("ignored")
    expected.with_name("station.csv.bak").write_text("ignored")
    expected.with_name("directory.CSV").mkdir()
    assert DataPaths(inmet=inmet_root).csv_paths(2024) == [expected]


def test_sorts_paths_independently_of_creation_order(inmet_root, write_inmet):
    last = write_inmet(station="A999")
    first = write_inmet(station="A001")
    assert DataPaths(inmet=inmet_root).csv_paths(2024) == [first, last]


def test_only_reads_the_requested_year(inmet_root, write_inmet):
    expected = write_inmet(year=2024)
    write_inmet(year=2023)
    assert DataPaths(inmet=inmet_root).csv_paths(2024) == [expected]


def test_empty_year_returns_empty_list(inmet_root):
    (inmet_root / "2024").mkdir()
    assert DataPaths(inmet=inmet_root).csv_paths(2024) == []


def test_missing_year_raises_file_not_found(inmet_root):
    with pytest.raises(FileNotFoundError):
        DataPaths(inmet=inmet_root).csv_paths(2024)


def test_year_path_that_is_a_file_raises_not_a_directory(inmet_root):
    (inmet_root / "2024").write_text("not a directory")
    with pytest.raises(NotADirectoryError):
        DataPaths(inmet=inmet_root).csv_paths(2024)


def test_explicit_root_works_from_another_directory(
    inmet_root, write_inmet, monkeypatch, tmp_path,
):
    expected = write_inmet()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert DataPaths(inmet=inmet_root).csv_paths(2024) == [expected]
