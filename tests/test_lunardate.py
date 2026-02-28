from __future__ import annotations

import datetime

import pytest

from lunardate import LunarDate


def test_import_version() -> None:
    import lunardate

    assert lunardate.__version__ == "1.0.0"


def test_construction_valid() -> None:
    lunar = LunarDate(1976, 8, 8, True)
    assert lunar.year == 1976
    assert lunar.month == 8
    assert lunar.day == 8
    assert lunar.is_leap_month is True


@pytest.mark.parametrize(
    "year, month, day, is_leap",
    [
        (1899, 1, 1, False),
        (2100, 1, 1, False),
        (2000, 0, 1, False),
        (2000, 13, 1, False),
        (2000, 1, 0, False),
        (2000, 1, 40, False),
    ],
)
def test_construction_invalid(year: int, month: int, day: int, is_leap: bool) -> None:
    with pytest.raises(ValueError):
        LunarDate(year, month, day, is_leap)


def test_repr_str() -> None:
    lunar = LunarDate(1976, 8, 8, True)
    assert repr(lunar) == "LunarDate(1976, 8, 8, True)"
    assert str(lunar) == "LunarDate(1976, 8, 8, True)"


def test_hash_consistency() -> None:
    a = LunarDate(2008, 9, 4, False)
    b = LunarDate(2008, 9, 4, False)
    assert a == b
    assert hash(a) == hash(b)
    assert len({a, b}) == 1


def test_today() -> None:
    today = LunarDate.today()
    assert isinstance(today, LunarDate)


def test_from_solar_date(known_pairs: list[tuple[datetime.date, int, int, int, bool]]) -> None:
    for solar, year, month, day, is_leap in known_pairs:
        lunar = LunarDate.from_solar_date(solar.year, solar.month, solar.day)
        assert (lunar.year, lunar.month, lunar.day, lunar.is_leap_month) == (
            year,
            month,
            day,
            is_leap,
        )


def test_to_solar_date(known_pairs: list[tuple[datetime.date, int, int, int, bool]]) -> None:
    for solar, year, month, day, is_leap in known_pairs:
        lunar = LunarDate(year, month, day, is_leap)
        assert lunar.to_solar_date() == solar


def test_roundtrip(known_pairs: list[tuple[datetime.date, int, int, int, bool]]) -> None:
    for solar, _, _, _, _ in known_pairs:
        lunar = LunarDate.from_solar_date(solar.year, solar.month, solar.day)
        assert lunar.to_solar_date() == solar


def test_leap_month_for_year() -> None:
    assert LunarDate.leap_month_for_year(2023) == 2
    assert LunarDate.leap_month_for_year(2022) is None


def test_arithmetic() -> None:
    lunar = LunarDate(1976, 8, 8, True)
    delta = datetime.timedelta(days=10)
    assert lunar + delta == LunarDate(1976, 8, 18, True)
    assert delta + lunar == LunarDate(1976, 8, 18, True)

    solar = datetime.date(2008, 1, 1)
    assert (lunar - solar).days == -11414
    assert (solar - lunar).days == 11414


def test_comparison() -> None:
    a = LunarDate(1976, 8, 8, False)
    b = LunarDate(1976, 8, 8, True)
    c = LunarDate(1976, 8, 9, True)
    assert a < b < c


def test_immutability() -> None:
    lunar = LunarDate(1976, 8, 8, True)
    with pytest.raises(AttributeError):
        lunar.year = 2000  # type: ignore[misc]


def test_deprecated_aliases() -> None:
    with pytest.warns(DeprecationWarning):
        LunarDate.fromSolarDate(1976, 10, 1)
    with pytest.warns(DeprecationWarning):
        LunarDate(1976, 8, 8, True).toSolarDate()
    with pytest.warns(DeprecationWarning):
        LunarDate.leapMonthForYear(2023)


def test_deprecated_property() -> None:
    lunar = LunarDate(1976, 8, 8, True)
    with pytest.warns(DeprecationWarning):
        assert lunar.isLeapMonth is True
