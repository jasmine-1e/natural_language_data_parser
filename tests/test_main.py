from datetime import date
import pytest
from nldate import parse


tester_data = date(2026, 5, 13)  ## today


def test_normal_date():
    assert parse("January 5th, 2025") == date(2025, 1, 5)


def test_abbrev_date():
    assert parse("jan 5th, 2025") == date(2025, 1, 5)


def test_yesterday():
    assert parse("yesterday", today=tester_data) == date(2026, 5, 12)


def test_tmr():
    assert parse("tomorrow", today=tester_data) == date(2026, 5, 14)


def test_num_days_before_day():
    assert parse("14 days before May 13, 2026") == date(2026, 4, 29)
    assert parse("14 days before May 13th, 2026") == date(2026, 4, 29)
    assert parse("14 days before Dec 13th, 2026") == date(2026, 11, 29)


def test_num_days_after_day():
    assert parse("14 days after May 13, 2026") == date(2026, 5, 27)
    assert parse("14 days after May 13th, 2026") == date(2026, 5, 27)
    assert parse("14 days after Dec 13th, 2026") == date(2026, 12, 27)


def test_num_days_before_today():
    assert parse("14 days before today", today=tester_data) == date(2026, 4, 29)


def test_num_days_after_today():
    assert parse("14 days after today", today=tester_data) == date(2026, 5, 27)


def test_num_days_before_yesterday():
    assert parse("14 days before yesterday", today=tester_data) == date(2026, 4, 28)


def test_num_days_after_yesterday():
    assert parse("14 days after yesterday", today=tester_data) == date(2026, 5, 26)


def test_num_days_before_tomorrow():
    assert parse("14 days before tomorrow", today=tester_data) == date(2026, 4, 30)


def test_num_days_after_tomorrow():
    assert parse("14 days after tomorrow", today=tester_data) == date(2026, 5, 28)


def test_last_whatever():
    assert parse("last Tuesday", today=tester_data) == date(2026, 5, 12)


def test_next_whatever():
    assert parse("next Tuesday, today= tester_data") == date(2026, 5, 19)


def test_bad_input():
    with pytest.raises(ValueError):
        parse("not valid input")
