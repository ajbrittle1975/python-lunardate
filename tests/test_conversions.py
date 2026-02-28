from __future__ import annotations

import datetime

import pytest

from lunardate._conversions import (
    enum_month,
    leap_month_for_year,
    lunar_to_offset,
    lunar_to_solar,
    offset_to_lunar,
    solar_to_lunar,
    validate_lunar_date,
)


@pytest.mark.parametrize("year", [1900, 1910, 1956, 2008, 2022])
def test_enum_month_count_no_leap(year: int) -> None:
    leap = leap_month_for_year(year)
    if leap is not None:
        pytest.skip("year has leap month")

    months = list(enum_month(_year_info_for(year)))
    assert len(months) == 12


@pytest.mark.parametrize("year", [1976, 2033, 2088])
def test_enum_month_count_with_leap(year: int) -> None:
    leap = leap_month_for_year(year)
    assert leap is not None

    months = list(enum_month(_year_info_for(year)))
    assert len(months) == 13
    leap_positions = [idx for idx, (m, _, is_leap) in enumerate(months) if is_leap]
    assert len(leap_positions) == 1
    assert months[leap_positions[0]][0] == leap


@pytest.mark.parametrize(
    "year, month, day, is_leap",
    [
        (1900, 1, 1, False),
        (1976, 8, 8, True),
        (2008, 9, 4, False),
        (2088, 4, 27, False),
    ],
)
def test_offset_roundtrip(year: int, month: int, day: int, is_leap: bool) -> None:
    offset = lunar_to_offset(year, month, day, is_leap)
    assert offset_to_lunar(offset) == (year, month, day, is_leap)


def test_validate_rejects_bad_year() -> None:
    with pytest.raises(ValueError, match="year out of range"):
        validate_lunar_date(1899, 1, 1, False)


def test_validate_rejects_bad_month() -> None:
    with pytest.raises(ValueError, match="month out of range"):
        validate_lunar_date(1900, 13, 1, False)


def test_validate_rejects_bad_day() -> None:
    with pytest.raises(ValueError, match="day out of range"):
        validate_lunar_date(1900, 1, 40, False)


def test_solar_to_lunar_known_pairs(
    known_pairs: list[tuple[datetime.date, int, int, int, bool]],
) -> None:
    for solar, year, month, day, is_leap in known_pairs:
        assert solar_to_lunar(solar.year, solar.month, solar.day) == (year, month, day, is_leap)


def test_lunar_to_solar_known_pairs(
    known_pairs: list[tuple[datetime.date, int, int, int, bool]],
) -> None:
    for solar, year, month, day, is_leap in known_pairs:
        assert lunar_to_solar(year, month, day, is_leap) == solar


def _year_info_for(year: int) -> int:
    from lunardate._data import START_YEAR, YEAR_INFOS

    return YEAR_INFOS[year - START_YEAR]
