from __future__ import annotations

from lunardate._data import END_YEAR, START_YEAR, YEAR_DAYS, YEAR_INFOS, _year_info_to_days


def test_year_infos_length() -> None:
    assert len(YEAR_INFOS) == 200


def test_year_days_length() -> None:
    assert len(YEAR_DAYS) == 200


def test_year_days_range() -> None:
    for days in YEAR_DAYS:
        assert 348 <= days <= 390


def test_year_days_match_year_infos() -> None:
    for info, days in zip(YEAR_INFOS, YEAR_DAYS, strict=True):
        assert _year_info_to_days(info) == days


def test_start_end_year_constants() -> None:
    assert START_YEAR == 1900
    assert END_YEAR == 2100
