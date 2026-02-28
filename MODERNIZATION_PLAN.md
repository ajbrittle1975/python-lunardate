# Audit & Modernization Plan: python-lunardate

## Overview

`python-lunardate` is a pure-Python Chinese calendar library that converts between Solar (Gregorian) and Lunar (Chinese) dates for years 1900–2099. The current codebase is a single 457-line file with legacy Python 2 patterns, no type hints, no proper test suite, and outdated packaging. This plan refactors it into a modern, well-structured, fully-typed, well-tested Python package following current best practices.

## Stack

Python (pure library — no framework dependencies)

## Prerequisites

- [ ] Python 3.10+ installed (target minimum version)
- [ ] `pip` capable of building from `pyproject.toml`
- [ ] `pytest` and `mypy` available (will be declared as dev dependencies)

---

## Audit Findings

### Critical Issues

| # | Issue | Location | Severity |
|---|-------|----------|----------|
| 1 | **Dead code**: `day2LunarDate()` (lines 441–449) is incomplete — calls `LunarDate()` with no args, which would crash | `lunardate.py:441` | High |
| 2 | **No `__hash__`**: `__eq__` is defined without `__hash__`, breaking the hash contract. `LunarDate` instances cannot be reliably used in sets or as dict keys | `lunardate.py:256` | High |
| 3 | **No input validation in `__init__`**: Can create nonsensical dates like `LunarDate(9999, 99, 99)` with no error until `toSolarDate()` is called | `lunardate.py:121` | High |
| 4 | **Expensive `__eq__`**: Converts both operands to solar dates via `toSolarDate()` then diffs. Should compare `(year, month, day, isLeapMonth)` tuples directly | `lunardate.py:256-264` | Medium |
| 5 | **Expensive comparisons**: `__lt__` also converts to solar. Should compare tuples with proper leap-month ordering | `lunardate.py:266-278` | Medium |

### Style / Best Practices Issues

| # | Issue | Location |
|---|-------|----------|
| 6 | `class LunarDate(object)` — Python 2 explicit base class | `lunardate.py:118` |
| 7 | camelCase method names: `fromSolarDate`, `toSolarDate`, `isLeapMonth`, `leapMonthForYear` — violates PEP 8 | Throughout |
| 8 | No type hints anywhere | Throughout |
| 9 | `__str__` returns repr-style output (`LunarDate(1976, 8, 8, 1)`); `__repr__` is aliased to `__str__` | `lunardate.py:127-130` |
| 10 | No `__slots__` — unnecessary memory overhead for a value type | `lunardate.py:118` |
| 11 | Mutable public attributes on what should be an immutable value type | `lunardate.py:121-125` |
| 12 | Nested functions `_calcDays` and `_calcMonthDay` should be proper methods or module-level helpers | `lunardate.py:206`, `lunardate.py:332` |
| 13 | `yearInfo2yearDay` is a public module-level function but not in `__all__` | `lunardate.py:407` |
| 14 | Module docstring doubles as PyPI long_description, mixing concerns | `lunardate.py:9-111` |

### Packaging Issues

| # | Issue |
|---|-------|
| 15 | Legacy `setup.py` — should use `pyproject.toml` |
| 16 | Python 2.7 and 3.4–3.7 classifiers — all EOL |
| 17 | No `requires-python` constraint |
| 18 | No dev dependencies defined |
| 19 | `lunardate.egg-info/` committed to repo |
| 20 | Version string managed manually in source |

### Testing Issues

| # | Issue |
|---|-------|
| 21 | Only doctests embedded in source — no proper test suite |
| 22 | No edge case tests (year boundaries, invalid inputs, data table integrity) |
| 23 | No CI workflow file in repository (referenced in README badge but missing from `.github/`) |

### Architecture Issues

| # | Issue |
|---|-------|
| 24 | Single monolithic file mixing data table, conversion logic, and public API |
| 25 | 200-element `yearInfos` hex data embedded inline — hard to audit or extend |
| 26 | No caching strategy documentation (though `yearDays` pre-computation is good) |

---

## Architecture Decisions

### Decision 1: Convert to proper package structure

- **Choice**: Refactor from single `lunardate.py` module to a `lunardate/` package directory with `__init__.py`, `_data.py`, `_conversions.py`, and `lunardate.py` (class definition).
- **Rationale**: Separates the 200-element data table from logic, makes the codebase navigable, and allows independent testing of conversion functions vs. the `LunarDate` class API. The public API (`from lunardate import LunarDate`) remains unchanged via `__init__.py` re-exports.
- **Alternatives considered**:
  - *Keep single file*: Rejected — mixing 50 lines of data, 150 lines of bit-manipulation helpers, and 200 lines of class API in one file hurts maintainability.
  - *Move data to JSON/TOML file*: Rejected — the hex data is compact, static, and benefits from being importable Python for pre-computation at module load. A data file adds I/O overhead for no gain.
- **Conport key**: Decision logged as `package-structure`

### Decision 2: Make LunarDate immutable with `__slots__`

- **Choice**: Use `__slots__` and read-only properties (backed by private attributes) to make `LunarDate` an immutable value type. Implement `__hash__` based on `(year, month, day, is_leap_month)`.
- **Rationale**: A date is fundamentally a value object. Immutability enables hashing (sets, dict keys), prevents bugs from accidental mutation, and `__slots__` reduces memory footprint per instance.
- **Alternatives considered**:
  - *`@dataclass(frozen=True)`*: Attractive but would require Python 3.10+ `__slots__=True` parameter. Also doesn't give us control over `__repr__` format without overriding it anyway. The manual approach with `__slots__` is equally clean and explicit.
  - *`NamedTuple`*: Rejected — doesn't support custom methods, `@staticmethod`, or `@classmethod` cleanly. Would require a wrapper class, adding complexity.
- **Conport key**: Decision logged as `immutable-lunardate`

### Decision 3: Add PEP 8 snake_case API with deprecation aliases

- **Choice**: Rename all public methods to snake_case (`from_solar_date`, `to_solar_date`, `is_leap_month`, `leap_month_for_year`). Provide camelCase aliases that emit `DeprecationWarning` for one major version, then remove.
- **Rationale**: PEP 8 compliance is expected in modern Python. The aliases preserve backward compatibility for existing users while guiding migration.
- **Alternatives considered**:
  - *Break API immediately*: Rejected — existing users (PyPI shows downloads) would break with no migration path.
  - *Keep camelCase forever*: Rejected — violates Python conventions and signals an unmaintained library.
- **Conport key**: Decision logged as `pep8-naming-migration`

### Decision 4: Migrate to `pyproject.toml` with setuptools backend

- **Choice**: Replace `setup.py` with `pyproject.toml` using `setuptools` as the build backend. Target Python ≥ 3.10.
- **Rationale**: `pyproject.toml` is the PEP 621 standard. setuptools is the most compatible backend for an existing PyPI package. Python 3.10+ gives us `match` statements, `|` union types in annotations, and `__slots__` in dataclasses — all of which are worth the minimum version bump.
- **Alternatives considered**:
  - *Hatchling/Flit*: Viable but setuptools is already the implicit backend and requires no new tooling knowledge. The package is simple enough that backend choice is immaterial.
  - *Target Python 3.8+*: Rejected — 3.8 and 3.9 are EOL or near-EOL. The library has no users who would reasonably be stuck on 3.8 for a calendar utility.
- **Conport key**: Decision logged as `pyproject-toml-migration`

### Decision 5: Optimize comparisons to avoid solar conversion

- **Choice**: Implement `__eq__` and `__lt__` by comparing `(year, month, day, is_leap_month)` tuples directly, with leap month ordering correctly placed after its regular month.
- **Rationale**: Current `__eq__` calls `toSolarDate()` on both operands (which iterates `yearDays` and `_enumMonth`), making every comparison O(N) where N is the year offset. Tuple comparison is O(1).
- **Alternatives considered**:
  - *Cache solar date internally*: Would speed up repeated comparisons but adds memory overhead. Direct tuple comparison is simpler and universally fast.
- **Conport key**: Decision logged as `optimize-comparisons`

### Decision 6: Add comprehensive pytest test suite

- **Choice**: Create a `tests/` directory with pytest-based tests organized by concern: `test_lunardate.py` (class API), `test_conversions.py` (round-trip and edge cases), `test_data.py` (data table integrity). Migrate existing doctests to proper test functions. Keep a minimal set of doctests in source only for documentation purposes.
- **Rationale**: Doctests are brittle and limited. pytest provides parametrization, fixtures, clear failure messages, and is the Python community standard.
- **Alternatives considered**:
  - *Keep doctests as primary tests*: Rejected — they can't handle edge cases, parametrization, or expected exceptions cleanly.
- **Conport key**: Decision logged as `pytest-test-suite`

---

## Data Model Changes

Not applicable — this is a pure library with no persistence layer.

---

## Target Package Structure

```
python-lunardate/
├── pyproject.toml              # PEP 621 metadata + build config
├── README.md                   # Updated documentation
├── LICENSE.txt                 # GPLv3 (unchanged)
├── .gitignore                  # Updated to cover modern Python artifacts
├── src/
│   └── lunardate/
│       ├── __init__.py         # Public API re-exports: LunarDate, __version__
│       ├── _data.py            # yearInfos table + yearDays pre-computation
│       ├── _conversions.py     # _enum_month(), _from_offset(), _year_info_to_days()
│       └── lunardate.py        # LunarDate class definition
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   ├── test_lunardate.py       # LunarDate class unit tests
│   ├── test_conversions.py     # Conversion round-trip + edge cases
│   └── test_data.py            # Data table integrity checks
└── .github/
    └── workflows/
        └── ci.yml              # GitHub Actions CI
```

Uses `src` layout per [setuptools recommendations](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout) — prevents accidental import of the source tree instead of the installed package during testing.

---

## Implementation Sequence

### Step 1: Create `pyproject.toml` and remove `setup.py`

- **Scope**: `pyproject.toml` (new), `setup.py` (delete), `lunardate.egg-info/` (delete), `.gitignore` (update)
- **Details**:
  - Create `pyproject.toml` with:
    ```toml
    [build-system]
    requires = ["setuptools>=68.0"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "lunardate"
    version = "1.0.0"
    description = "A Chinese Calendar Library in Pure Python"
    readme = "README.md"
    license = "GPL-3.0-only"
    requires-python = ">=3.10"
    authors = [
        {name = "LI Daobing", email = "lidaobing@gmail.com"},
    ]
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ]
    keywords = ["chinese", "lunar", "calendar", "date", "conversion"]

    [project.optional-dependencies]
    dev = ["pytest>=8.0", "mypy>=1.8", "ruff>=0.3"]

    [project.urls]
    Homepage = "https://github.com/lidaobing/python-lunardate"
    Repository = "https://github.com/lidaobing/python-lunardate"
    Issues = "https://github.com/lidaobing/python-lunardate/issues"

    [tool.setuptools.packages.find]
    where = ["src"]

    [tool.pytest.ini_options]
    testpaths = ["tests"]

    [tool.mypy]
    strict = true

    [tool.ruff]
    target-version = "py310"
    line-length = 99

    [tool.ruff.lint]
    select = ["E", "F", "W", "I", "N", "UP", "B", "SIM", "RUF"]
    ```
  - Delete `setup.py`
  - Delete `lunardate.egg-info/` directory
  - Update `.gitignore` to include: `*.egg-info/`, `dist/`, `build/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `*.egg`, `.venv/`
- **Tests**: Verify `pip install -e ".[dev]"` succeeds
- **Commit message**: `build: migrate from setup.py to pyproject.toml`

### Step 2: Create `src/lunardate/_data.py` — extract data table

- **Scope**: `src/lunardate/_data.py` (new)
- **Details**:
  - Move `yearInfos` list from `lunardate.py` → `_data.py` and rename to `YEAR_INFOS` (constant naming)
  - Move `yearInfo2yearDay()` → `_data.py` and rename to `_year_info_to_days()`
  - Move `yearDays` → `_data.py` and rename to `YEAR_DAYS`
  - Add module docstring explaining the bit-encoding format of the year info values
  - Add type annotations: `YEAR_INFOS: tuple[int, ...]` (convert list to tuple for immutability), `YEAR_DAYS: tuple[int, ...]`
  - Add constants: `START_YEAR: int = 1900`, `END_YEAR: int = 2100` (computed from `START_YEAR + len(YEAR_INFOS)`)
  - Add `__all__: list[str] = []` (all symbols are private)
- **Tests**: `test_data.py` — verify `len(YEAR_INFOS) == 200`, verify `len(YEAR_DAYS) == 200`, verify `YEAR_DAYS[i]` is in valid range (348–390), verify `START_YEAR == 1900` and `END_YEAR == 2100`
- **Commit message**: `refactor(data): extract calendar data table to _data module`

### Step 3: Create `src/lunardate/_conversions.py` — extract conversion logic

- **Scope**: `src/lunardate/_conversions.py` (new)
- **Details**:
  - Move `_enumMonth()` → `_conversions.py` as `enum_month(year_info: int) -> Iterator[tuple[int, int, bool]]`
    - Yields `(month, days, is_leap_month)` tuples
    - Add full docstring explaining the bit-extraction logic
  - Create `offset_to_lunar(offset: int) -> tuple[int, int, int, bool]`:
    - Refactored from `LunarDate._fromOffset()`
    - Returns `(year, month, day, is_leap_month)` — no `LunarDate` construction here
    - Eliminates the nested `_calcMonthDay` function
  - Create `lunar_to_offset(year: int, month: int, day: int, is_leap_month: bool) -> int`:
    - Refactored from the offset calculation in `LunarDate.toSolarDate()`
    - Returns the day offset from `START_DATE`
    - Eliminates the nested `_calcDays` function
    - Raises `ValueError` for invalid year/month/day
  - Create `validate_lunar_date(year: int, month: int, day: int, is_leap_month: bool) -> None`:
    - Raises `ValueError` with descriptive messages for invalid dates
    - Used by `LunarDate.__init__()` in lazy or eager mode
  - All functions fully typed with return annotations
  - Import data from `_data.py`: `from lunardate._data import YEAR_INFOS, YEAR_DAYS, START_YEAR, END_YEAR`
- **Tests**: `test_conversions.py` —
  - `test_enum_month_no_leap`: Verify 12 months yielded for a non-leap year
  - `test_enum_month_with_leap`: Verify 13 months yielded for a leap year, correct insertion position
  - `test_offset_to_lunar_roundtrip`: Parametrize over known solar↔lunar pairs
  - `test_lunar_to_offset_invalid`: Verify `ValueError` for out-of-range year/month/day
  - `test_validate_lunar_date_rejects_invalid`: Test various invalid dates
- **Commit message**: `refactor(core): extract conversion functions to _conversions module`

### Step 4: Create `src/lunardate/lunardate.py` — modernized LunarDate class

- **Scope**: `src/lunardate/lunardate.py` (new)
- **Details**:
  - Define `class LunarDate` with:
    - `__slots__ = ('_year', '_month', '_day', '_is_leap_month')`
    - Read-only properties: `year`, `month`, `day`, `is_leap_month`
    - `__init__(self, year: int, month: int, day: int, is_leap_month: bool = False)` — stores validated values
      - Call `validate_lunar_date()` from `_conversions` for eager validation
    - `__repr__` returns `LunarDate(1976, 8, 8, True)` (note: `True`/`False` not `1`/`0`)
    - `__str__` returns `1976-08-08 (leap)` or `1976-08-08` — human-readable format
    - `__hash__` returns `hash((self._year, self._month, self._day, self._is_leap_month))`
    - `__eq__` compares field tuples directly (O(1), not solar conversion)
    - `__lt__` compares `(year, month, _leap_sort_key, day)` where `_leap_sort_key` ensures the regular month sorts before its leap variant
    - `__le__`, `__gt__`, `__ge__` via `@functools.total_ordering`
    - `from_solar_date(cls, year: int, month: int, day: int) -> LunarDate` (classmethod)
    - `to_solar_date(self) -> datetime.date`
    - `today(cls) -> LunarDate` (classmethod)
    - `leap_month_for_year(year: int) -> int | None` (staticmethod)
    - `__add__`, `__radd__`, `__sub__`, `__rsub__` — same semantics as current, using `_conversions` functions
  - **Deprecation aliases**: Define `fromSolarDate = from_solar_date` etc., wrapped with `warnings.warn("fromSolarDate is deprecated, use from_solar_date", DeprecationWarning, stacklevel=2)`. Consider using a descriptor or simple wrapper function for each alias.
  - **Property alias**: `isLeapMonth` property that warns and delegates to `is_leap_month`
- **Tests**: `test_lunardate.py` — full test suite (see Testing Strategy below)
- **Commit message**: `refactor(api): modernize LunarDate class with slots, types, and snake_case`

### Step 5: Create `src/lunardate/__init__.py` — public API surface

- **Scope**: `src/lunardate/__init__.py` (new), delete old root `lunardate.py`
- **Details**:
  - ```python
    """A Chinese Calendar Library in Pure Python."""
    from lunardate.lunardate import LunarDate

    __version__ = "1.0.0"
    __all__ = ["LunarDate"]
    ```
  - Delete the original root-level `lunardate.py`
  - Verify `from lunardate import LunarDate` still works
  - Add `py.typed` marker file at `src/lunardate/py.typed` for PEP 561
- **Tests**: `test_lunardate.py::test_import` — verify `from lunardate import LunarDate` and `lunardate.__version__`
- **Commit message**: `refactor(pkg): establish package structure with public API`

### Step 6: Write comprehensive test suite

- **Scope**: `tests/conftest.py`, `tests/test_lunardate.py`, `tests/test_conversions.py`, `tests/test_data.py` (all new)
- **Details**:
  - **`conftest.py`**:
    - Fixture: `known_pairs` — list of `(solar_date, lunar_year, lunar_month, lunar_day, is_leap)` tuples from the existing doctests plus additional edge cases
  - **`test_data.py`**:
    - `test_year_infos_length`: 200 entries
    - `test_year_days_range`: Each between 348 and 390
    - `test_year_days_matches_year_infos`: `YEAR_DAYS[i] == _year_info_to_days(YEAR_INFOS[i])` for all i
    - `test_start_end_year_constants`: `START_YEAR == 1900`, `END_YEAR == 2100`
  - **`test_conversions.py`**:
    - `test_enum_month_count_no_leap`: Parametrize across non-leap years
    - `test_enum_month_count_leap`: Parametrize across leap years, verify 13 yields
    - `test_enum_month_leap_position`: Verify leap month appears after its regular counterpart
    - `test_offset_roundtrip`: For each known pair, verify `offset_to_lunar(lunar_to_offset(...)) == original`
    - `test_validate_rejects_bad_year/month/day/leap`
  - **`test_lunardate.py`**:
    - `test_construction_valid`: Basic construction and property access
    - `test_construction_invalid`: Parametrize invalid dates, verify `ValueError`
    - `test_repr`: Verify `repr(LunarDate(1976, 8, 8, True)) == "LunarDate(1976, 8, 8, True)"`
    - `test_str`: Verify human-readable format
    - `test_from_solar_date`: Parametrize known conversions
    - `test_to_solar_date`: Parametrize known conversions (reverse direction)
    - `test_roundtrip_solar_lunar_solar`: For a range of dates, verify `ld.to_solar_date()` → `from_solar_date()` → same `ld`
    - `test_today`: Verify type and that it doesn't raise
    - `test_leap_month_for_year`: Known leap years + non-leap years
    - `test_hash_consistency`: Equal dates have equal hashes; can be used in sets
    - `test_eq_same/different/non_lunardate`
    - `test_ordering`: Parametrize pairs and verify `<`, `<=`, `>`, `>=`
    - `test_add_timedelta/sub_timedelta/sub_lunardate/sub_date`
    - `test_radd/rsub`
    - `test_deprecated_camel_case_warns`: Verify `DeprecationWarning` for old names
    - `test_immutability`: Verify `AttributeError` when trying to set `year`/`month`/`day`/`is_leap_month`
    - `test_slots`: Verify no `__dict__` on instances
    - **Edge cases**:
      - Year boundaries (Dec 31 → Jan 1 crossing in both calendars)
      - First and last supported dates (1900-01-31, ~2100-02-08)
      - Leap month boundaries (day before, first day, last day, day after)
- **Commit message**: `test: add comprehensive pytest test suite`

### Step 7: Update documentation

- **Scope**: `README.md` (rewrite)
- **Details**:
  - Modern README structure:
    - Brief description
    - Installation: `pip install lunardate`
    - Quick start with updated API examples (snake_case)
    - Migration guide: table mapping old camelCase → new snake_case names
    - API reference section with all public methods documented
    - Development section: `pip install -e ".[dev]"`, `pytest`, `mypy src/`, `ruff check .`
    - Version history (keep existing, add 1.0.0 entry)
    - Limits section (1900–2099)
    - License
  - Keep badges, update if needed
- **Tests**: N/A
- **Commit message**: `docs: rewrite README with modern API and migration guide`

### Step 8: Add GitHub Actions CI

- **Scope**: `.github/workflows/ci.yml` (new)
- **Details**:
  - Matrix: Python 3.10, 3.11, 3.12, 3.13
  - Steps: checkout, setup-python, `pip install -e ".[dev]"`, `ruff check .`, `mypy src/`, `pytest --tb=short -q`
  - Trigger on push to `main` and pull requests
- **Tests**: CI itself validates tests pass
- **Commit message**: `ci: add GitHub Actions workflow for lint, type-check, and test`

### Step 9: Final cleanup

- **Scope**: Various
- **Details**:
  - Remove old `lunardate.egg-info/` from git tracking: `git rm -r lunardate.egg-info/`
  - Verify `.gitignore` covers all generated artifacts
  - Run full suite: `ruff check .`, `mypy src/`, `pytest -v`
  - Verify `python -m build` produces a clean sdist and wheel
- **Tests**: Full CI pass
- **Commit message**: `chore: remove build artifacts and finalize cleanup`

---

## Testing Strategy

### Unit Tests
- **`test_data.py`**: Data table structural integrity — correct lengths, value ranges, constant correctness
- **`test_conversions.py`**: Pure function tests — `enum_month`, `offset_to_lunar`, `lunar_to_offset`, `validate_lunar_date`
- **`test_lunardate.py`**: Class API tests — construction, conversion, arithmetic, comparison, hashing, immutability, deprecation warnings

### Parametrized Test Data
Known solar ↔ lunar pairs (from existing doctests + supplementary):
| Solar Date | Lunar Year | Month | Day | Leap? |
|------------|-----------|-------|-----|-------|
| 1900-01-31 | 1900 | 1 | 1 | No |
| 1976-10-01 | 1976 | 8 | 8 | Yes |
| 2008-10-02 | 2008 | 9 | 4 | No |
| 2033-10-23 | 2033 | 10 | 1 | No |
| 1956-12-02 | 1956 | 11 | 1 | No |
| 2088-05-17 | 2088 | 4 | 27 | No |
| 2088-06-17 | 2088 | 4 | 28 | Yes |
| 2088-07-17 | 2088 | 5 | 29 | No |

### Edge Cases to Cover
- First supported date: solar 1900-01-31 = lunar 1900/1/1
- Last supported year: lunar 2099/12/last-day
- Invalid year: 1899, 2100
- Invalid month: 0, 13
- Invalid day: 0, 31 (for 29-day months)
- Leap month that doesn't exist for the year
- Arithmetic across year boundaries
- Comparison between leap and non-leap month of same year/month

### Type Checking
- `mypy --strict src/` must pass with zero errors
- All public methods fully annotated with parameter and return types

---

## Risks & Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing users who depend on camelCase API | High | Medium | Deprecation aliases with `DeprecationWarning` for at least one version cycle |
| `__repr__` format change (`1` → `True` for leap month) breaks code that `eval()`s repr output | Low | Low | Document the change; `eval(repr(x))` was never a supported contract |
| `__eq__` behavior change if any currently-"equal" dates differ by field but coincide in solar conversion | Very Low | Medium | This would indicate a bug in the original, not a regression. Test thoroughly. |
| Validation in `__init__` could break code that constructs invalid dates intentionally | Low | Low | Can't construct invalid dates with the current API without hitting an error at `toSolarDate()` anyway |

### Open Questions

1. **Version number**: Should this be `1.0.0` (indicating a mature, stable release) or `0.3.0` (indicated incremental improvement)? **Recommendation**: `1.0.0` — the library is 15+ years old and functionally complete.
2. **`__str__` format**: The proposed `"1976-08-08 (leap)"` format is new. Should it use ISO-like format `"L1976-08-08"` or something else? **Recommendation**: `"LunarDate(1976, 8, 8, True)"` for both `__repr__` **and** `__str__` initially to minimize surprises, then add a `strftime()`-like method later.
3. **Eager vs. lazy validation**: Should `LunarDate(9999, 1, 1)` raise in `__init__` or defer to `to_solar_date()`? **Recommendation**: Eager — fail fast. This is a breaking change but improves correctness.

---

## Conport Updates

After implementation, the following should be recorded:

| Type | Key/Tag | Content |
|------|---------|---------|
| Decision | `package-structure` | Convert to `src/lunardate/` package layout |
| Decision | `immutable-lunardate` | Make `LunarDate` immutable with `__slots__` and `__hash__` |
| Decision | `pep8-naming-migration` | snake_case API with deprecation aliases |
| Decision | `pyproject-toml-migration` | Replace `setup.py` with `pyproject.toml`, target Python ≥3.10 |
| Decision | `optimize-comparisons` | Direct tuple comparison instead of solar conversion |
| Decision | `pytest-test-suite` | Comprehensive pytest suite replacing doctests |
| Progress | `audit-complete` | Full codebase audit done |
| Progress | `plan-complete` | Modernization plan written |
| System Pattern | `src-layout` | Using src/ layout for package structure |
| System Pattern | `deprecation-alias` | Pattern for migrating public API names with warnings |
| Active Context | `current_focus` | Modernization of python-lunardate |
