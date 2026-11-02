from eu_ecom.eurostat import parse_cell, read_wide_tsv


def test_parse_cell_number_only():
    assert parse_cell("23.92 ") == (23.92, None)


def test_parse_cell_number_with_flag():
    assert parse_cell("76.02 b") == (76.02, "b")


def test_parse_cell_missing_with_flag():
    assert parse_cell(": u") == (None, "u")


def test_parse_cell_missing_and_empty():
    assert parse_cell(": ") == (None, None)
    assert parse_cell("") == (None, None)


def test_read_wide_tsv_gives_one_row_per_cell(tmp_path):
    path = tmp_path / "sample.tsv"
    path.write_text(
        "freq,indic_is,unit,geo\\TIME_PERIOD\t2020 \t2021 \n"
        "A,E_AESELL,PC_ENT,DE\t19.95 \t21.75 b\n"
    )

    rows = list(read_wide_tsv(path))

    assert rows == [
        {"freq": "A", "indic_is": "E_AESELL", "unit": "PC_ENT", "geo": "DE", "year": 2020, "value": 19.95, "flag": None},
        {"freq": "A", "indic_is": "E_AESELL", "unit": "PC_ENT", "geo": "DE", "year": 2021, "value": 21.75, "flag": "b"},
    ]
