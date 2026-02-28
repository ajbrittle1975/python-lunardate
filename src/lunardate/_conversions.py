"""Conversion helpers for Chinese lunar calendar calculations."""

from __future__ import annotations

import datetime
from typing import Iterator

from lunardate._data import END_YEAR, START_YEAR, YEAR_DAYS, YEAR_INFOS

_START_DATE = datetime.date(1900, 1, 31)


def enum_month(year_info: int) -> Iterator[tuple[int, int, bool]]:
    """Yield (month, days, is_leap_month) tuples for the given lunar year info."""
    months = [(i, False) for i in range(1, 13)]
    leap_month = year_info % 16
    if leap_month == 0:
        pass
    elif 1 <= leap_month <= 12:
        months.insert(leap_month, (leap_month, True))
    else:
        raise ValueError(f"yearInfo {year_info!r} mod 16 should be in [0, 12]")

    for month, is_leap_month in months:
        if is_leap_month:
            days = (year_info >> 16) % 2 + 29
        else:
            days = (year_info >> (16 - month)) % 2 + 29
        yield month, days, is_leap_month


def leap_month_for_year(year: int) -> int | None:
    """Return the leap month for the given year, or None if no leap month."""
    if year < START_YEAR or year >= END_YEAR:
        raise ValueError(f"year out of range [{START_YEAR}, {END_YEAR})")
    year_info = YEAR_INFOS[year - START_YEAR]
    leap_month = year_info % 16
    if leap_month == 0:
        return None
    if 1 <= leap_month <= 12:
        return leap_month
    raise ValueError(f"yearInfo {year_info!r} mod 16 should be in [0, 12]")


def validate_lunar_date(year: int, month: int, day: int, is_leap_month: bool) -> None:
    """Validate lunar date components, raising ValueError for invalid inputs."""
    if year < START_YEAR or year >= END_YEAR:
        raise ValueError(f"year out of range [{START_YEAR}, {END_YEAR})")
    if month < 1 or month > 12:
        raise ValueError("month out of range")

    year_info = YEAR_INFOS[year - START_YEAR]
    leap_month = year_info % 16
    if is_leap_month and leap_month != month:
        raise ValueError("month out of range")
    if is_leap_month and leap_month == 0:
        raise ValueError("month out of range")

    for enum_month_value, days, enum_is_leap in enum_month(year_info):
        if (enum_month_value, enum_is_leap) == (month, bool(is_leap_month)):
            if 1 <= day <= days:
                return
            raise ValueError("day out of range")

    raise ValueError("month out of range")


def lunar_to_offset(year: int, month: int, day: int, is_leap_month: bool) -> int:
    """Convert a lunar date to day offset from the lunar epoch start date."""
    validate_lunar_date(year, month, day, is_leap_month)

    offset = 0
    year_index = year - START_YEAR
    for i in range(year_index):
        offset += YEAR_DAYS[i]

    year_info = YEAR_INFOS[year_index]
    for enum_month_value, days, enum_is_leap in enum_month(year_info):
        if (enum_month_value, enum_is_leap) == (month, bool(is_leap_month)):
            offset += day - 1
            return offset
        offset += days

    raise ValueError("month out of range")


def offset_to_lunar(offset: int) -> tuple[int, int, int, bool]:
    """Convert a day offset from the lunar epoch start date into a lunar date tuple."""
    offset = int(offset)

    for idx, year_days in enumerate(YEAR_DAYS):
        if offset < year_days:
            break
        offset -= year_days
    year = START_YEAR + idx

    year_info = YEAR_INFOS[idx]
    for month, days, is_leap_month in enum_month(year_info):
        if offset < days:
            return year, month, offset + 1, is_leap_month
        offset -= days

    raise ValueError("offset out of range")


def solar_to_lunar(year: int, month: int, day: int) -> tuple[int, int, int, bool]:
    """Convert a solar (Gregorian) date to a lunar date tuple."""
    solar_date = datetime.date(year, month, day)
    offset = (solar_date - _START_DATE).days
    return offset_to_lunar(offset)


def lunar_to_solar(year: int, month: int, day: int, is_leap_month: bool) -> datetime.date:
    """Convert a lunar date to a solar (Gregorian) date."""
    offset = lunar_to_offset(year, month, day, is_leap_month)
    return _START_DATE + datetime.timedelta(days=offset)
