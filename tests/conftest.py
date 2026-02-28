from __future__ import annotations

import datetime
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))


@pytest.fixture()
def known_pairs() -> list[tuple[datetime.date, int, int, int, bool]]:
    return [
        (datetime.date(1900, 1, 31), 1900, 1, 1, False),
        (datetime.date(1956, 12, 2), 1956, 11, 1, False),
        (datetime.date(1976, 10, 1), 1976, 8, 8, True),
        (datetime.date(2008, 10, 2), 2008, 9, 4, False),
        (datetime.date(2033, 10, 23), 2033, 10, 1, False),
        (datetime.date(2088, 5, 17), 2088, 4, 27, False),
        (datetime.date(2088, 6, 17), 2088, 4, 28, True),
        (datetime.date(2088, 7, 17), 2088, 5, 29, False),
    ]
