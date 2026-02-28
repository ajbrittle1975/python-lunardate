"""Public LunarDate API."""

from __future__ import annotations

import datetime
import functools
import warnings

from lunardate import _conversions


@functools.total_ordering
class LunarDate:
    """Value type representing a Chinese lunar date."""

    __slots__ = ("_year", "_month", "_day", "_is_leap_month")

    def __init__(self, year: int, month: int, day: int, is_leap_month: bool = False) -> None:
        _conversions.validate_lunar_date(year, month, day, is_leap_month)
        self._year = int(year)
        self._month = int(month)
        self._day = int(day)
        self._is_leap_month = bool(is_leap_month)

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day

    @property
    def is_leap_month(self) -> bool:
        return self._is_leap_month

    @property
    def isLeapMonth(self) -> bool:  # noqa: N802
        warnings.warn(
            "isLeapMonth is deprecated; use is_leap_month",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._is_leap_month

    def __repr__(self) -> str:
        return (
            f"LunarDate({self._year}, {self._month}, {self._day}, {self._is_leap_month})"
        )

    __str__ = __repr__

    def __hash__(self) -> int:
        return hash((self._year, self._month, self._day, self._is_leap_month))

    def _sort_key(self) -> tuple[int, int, int, int]:
        leap_sort = 1 if self._is_leap_month else 0
        return self._year, self._month, leap_sort, self._day

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LunarDate):
            return False
        return self._sort_key() == other._sort_key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LunarDate):
            raise TypeError(f"can't compare LunarDate to {type(other).__name__}")
        return self._sort_key() < other._sort_key()

    def __add__(self, other: datetime.timedelta) -> LunarDate:
        if isinstance(other, datetime.timedelta):
            solar = self.to_solar_date() + other
            return self.from_solar_date(solar.year, solar.month, solar.day)
        raise TypeError

    def __radd__(self, other: datetime.timedelta) -> LunarDate:
        return self + other

    def __sub__(self, other: object) -> datetime.timedelta | LunarDate:
        if isinstance(other, LunarDate):
            return self.to_solar_date() - other.to_solar_date()
        if isinstance(other, datetime.date):
            return self.to_solar_date() - other
        if isinstance(other, datetime.timedelta):
            solar = self.to_solar_date() - other
            return self.from_solar_date(solar.year, solar.month, solar.day)
        raise TypeError

    def __rsub__(self, other: object) -> datetime.timedelta:
        if isinstance(other, datetime.date):
            return other - self.to_solar_date()
        raise TypeError

    @classmethod
    def today(cls) -> LunarDate:
        today = datetime.date.today()
        return cls.from_solar_date(today.year, today.month, today.day)

    @classmethod
    def from_solar_date(cls, year: int, month: int, day: int) -> LunarDate:
        lunar_year, lunar_month, lunar_day, is_leap_month = _conversions.solar_to_lunar(
            year, month, day
        )
        return cls(lunar_year, lunar_month, lunar_day, is_leap_month)

    @staticmethod
    def leap_month_for_year(year: int) -> int | None:
        return _conversions.leap_month_for_year(year)

    def to_solar_date(self) -> datetime.date:
        return _conversions.lunar_to_solar(
            self._year,
            self._month,
            self._day,
            self._is_leap_month,
        )

    @classmethod
    def fromSolarDate(cls, year: int, month: int, day: int) -> LunarDate:  # noqa: N802
        warnings.warn(
            "fromSolarDate is deprecated; use from_solar_date",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.from_solar_date(year, month, day)

    def toSolarDate(self) -> datetime.date:  # noqa: N802
        warnings.warn(
            "toSolarDate is deprecated; use to_solar_date",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.to_solar_date()

    @staticmethod
    def leapMonthForYear(year: int) -> int | None:  # noqa: N802
        warnings.warn(
            "leapMonthForYear is deprecated; use leap_month_for_year",
            DeprecationWarning,
            stacklevel=2,
        )
        return _conversions.leap_month_for_year(year)
