# A Chinese Calendar Library in Pure Python

[![Python package](https://github.com/lidaobing/python-lunardate/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/lidaobing/python-lunardate/actions/workflows/python-package.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/lunardate)](https://pypi.org/project/lunardate/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/lunardate)](https://pypistats.org/packages/lunardate)

Chinese Calendar: http://en.wikipedia.org/wiki/Chinese_calendar

## Install

```bash
pip install lunardate
```

## Quick Start

```python
import datetime

from lunardate import LunarDate

lunar = LunarDate.from_solar_date(1976, 10, 1)
assert repr(lunar) == "LunarDate(1976, 8, 8, True)"

solar = lunar.to_solar_date()
assert solar == datetime.date(1976, 10, 1)

today = LunarDate.today()
```

## API Highlights

- `LunarDate.from_solar_date(year, month, day) -> LunarDate`
- `LunarDate.to_solar_date() -> datetime.date`
- `LunarDate.leap_month_for_year(year) -> int | None`
- Arithmetic with `datetime.timedelta`

## Migration Guide (0.2.x → 1.0.0)

Old camelCase names are still available as deprecated aliases and emit `DeprecationWarning`.

| Old Name | New Name |
|----------|----------|
| `fromSolarDate` | `from_solar_date` |
| `toSolarDate` | `to_solar_date` |
| `leapMonthForYear` | `leap_month_for_year` |
| `isLeapMonth` | `is_leap_month` |

## Development

```bash
pip install -e ".[dev]"
pytest
mypy src/
ruff check .
```

## Version History

- 1.0.0: Modernized package layout, typed API, pytest suite, PEP 8 method names
- 0.2.2: add LunarDate.leapMonthForYear; fix bug in year 1899
- 0.2.1: fix bug in year 1956
- 0.2.0: extend year to 2099, thanks to @FuGangqiang
- 0.1.5: fix bug in `==`
- 0.1.4: support '+', '-' and compare, fix bug in year 2050
- 0.1.3: support python 3.0

## Limits

This library can only deal with years from 1900 to 2099 (Chinese calendar years).

## Attribution

This project is a modernization of the original `python-lunardate` library by
LI Daobing (lidaobing@gmail.com). Upstream source:
https://github.com/lidaobing/python-lunardate

The conversion data and algorithms are derived from the C program `lunar`:
http://packages.qa.debian.org/l/lunar.html

See `NOTICE.md` for attribution details.

## License

Licensed under the GNU General Public License v3.0 only (GPL-3.0-only).
See `LICENSE.txt` and `NOTICE.md`.

## See also

- lunar: http://packages.qa.debian.org/l/lunar.html,
  A converter written in C, this program is derived from it.
- python-lunar: http://code.google.com/p/liblunar/
  Another library written in C, including a python binding.
