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


TODAY = date(2025, 3, 5)


def test_iso_format() -> None:
    assert parse("2025-12-01", today=TODAY) == date(2025, 12, 1)


def test_us_numeric_format() -> None:
    assert parse("12/25/2025", today=TODAY) == date(2025, 12, 25)


def test_month_name_day_year() -> None:
    assert parse("December 1st, 2025", today=TODAY) == date(2025, 12, 1)


def test_month_name_day_year_no_ordinal() -> None:
    assert parse("July 4 2025", today=TODAY) == date(2025, 7, 4)


def test_day_month_year() -> None:
    assert parse("1st December 2025", today=TODAY) == date(2025, 12, 1)


def test_abbreviated_month() -> None:
    assert parse("Jan 15, 2026", today=TODAY) == date(2026, 1, 15)


def test_month_no_year_future() -> None:
    assert parse("June 10", today=TODAY) == date(2025, 6, 10)


def test_month_no_year_past_wraps() -> None:
    assert parse("January 1", today=TODAY) == date(2026, 1, 1)


def test_today() -> None:
    assert parse("today", today=TODAY) == TODAY


def test_tomorrow() -> None:
    assert parse("tomorrow", today=TODAY) == date(2025, 3, 6)


def test_day_after_tomorrow() -> None:
    assert parse("the day after tomorrow", today=TODAY) == date(2025, 3, 7)


def test_day_before_yesterday() -> None:
    assert parse("the day before yesterday", today=TODAY) == date(2025, 3, 3)


def test_next_tuesday() -> None:
    assert parse("next Tuesday", today=TODAY) == date(2025, 3, 11)


def test_next_wednesday_skips_week() -> None:
    assert parse("next Wednesday", today=TODAY) == date(2025, 3, 12)


def test_last_monday() -> None:
    assert parse("last Monday", today=TODAY) == date(2025, 3, 3)


def test_this_friday() -> None:
    assert parse("this Friday", today=TODAY) == date(2025, 3, 7)


def test_bare_weekday() -> None:
    assert parse("Saturday", today=TODAY) == date(2025, 3, 8)


def test_in_n_days() -> None:
    assert parse("in 3 days", today=TODAY) == date(2025, 3, 8)


def test_in_one_week() -> None:
    assert parse("in one week", today=TODAY) == date(2025, 3, 12)


def test_in_a_week() -> None:
    assert parse("in a week", today=TODAY) == date(2025, 3, 12)


def test_n_days_ago() -> None:
    assert parse("7 days ago", today=TODAY) == date(2025, 2, 26)


def test_n_days_from_now() -> None:
    assert parse("10 days from now", today=TODAY) == date(2025, 3, 15)


def test_in_n_months() -> None:
    assert parse("in 2 months", today=TODAY) == date(2025, 5, 5)


def test_in_n_years() -> None:
    assert parse("in 1 year", today=TODAY) == date(2026, 3, 5)


def test_n_weeks_ago() -> None:
    assert parse("2 weeks ago", today=TODAY) == date(2025, 2, 19)


def test_compound_offset_and() -> None:
    assert parse("1 year and 2 months from now", today=TODAY) == date(2026, 5, 5)


def test_days_before_date() -> None:
    assert parse("5 days before December 1st, 2025", today=TODAY) == date(2025, 11, 26)


def test_days_after_date() -> None:
    assert parse("10 days after January 1, 2026", today=TODAY) == date(2026, 1, 11)


def test_weeks_before_date() -> None:
    assert parse("2 weeks before March 20, 2025", today=TODAY) == date(2025, 3, 6)


def test_months_after_date() -> None:
    assert parse("3 months after July 4 2025", today=TODAY) == date(2025, 10, 4)


def test_year_after_date() -> None:
    assert parse("1 year after June 15, 2024", today=TODAY) == date(2025, 6, 15)


def test_days_before_tomorrow() -> None:
    assert parse("3 days before tomorrow", today=TODAY) == date(2025, 3, 3)


def test_days_after_yesterday() -> None:
    assert parse("2 days after yesterday", today=TODAY) == date(2025, 3, 6)


def test_days_before_next_tuesday() -> None:

    assert parse("1 day before next Tuesday", today=TODAY) == date(2025, 3, 10)


def test_compound_year_and_month_before() -> None:
    assert parse("1 year and 2 months before December 1, 2026", today=TODAY) == date(
        2025, 10, 1
    )


def test_next_week() -> None:
    assert parse("next week", today=TODAY) == date(2025, 3, 12)


def test_last_week() -> None:
    assert parse("last week", today=TODAY) == date(2025, 2, 26)


def test_next_month() -> None:
    assert parse("next month", today=TODAY) == date(2025, 4, 5)


def test_last_month() -> None:
    assert parse("last month", today=TODAY) == date(2025, 2, 5)


def test_next_year() -> None:
    assert parse("next year", today=TODAY) == date(2026, 3, 5)


def test_last_year() -> None:
    assert parse("last year", today=TODAY) == date(2024, 3, 5)


def test_default_today() -> None:
    result = parse("today")
    assert result == date.today()


def test_invalid_raises() -> None:
    with pytest.raises(ValueError):
        parse("banana phone", today=TODAY)


def test_empty_raises() -> None:
    with pytest.raises(ValueError):
        parse("", today=TODAY)
