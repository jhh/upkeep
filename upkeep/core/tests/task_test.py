import datetime
from datetime import timedelta

import pytest

from upkeep.core.models import Task


def test_task_is_recurring():
    task = Task(name="test", interval=None)
    assert not task.is_recurring()


# https://www.timeanddate.com/date/dateadded.html
@pytest.mark.parametrize(
    "interval, frequency, timedelta",
    [
        (1, "days", timedelta(days=1)),
        (2, "weeks", timedelta(days=14)),
        (4, "weeks", timedelta(days=28)),
        (1, "months", timedelta(days=31)),
        (2, "months", timedelta(days=60)),  # 2024 is leap year
    ],
)
def test_task_next_date(interval, frequency, timedelta):
    task = Task(name="test", interval=interval, frequency=frequency)
    start_date = datetime.datetime(year=2024, month=1, day=1)
    delta: datetime.timedelta = task.next_date(start_date) - start_date
    assert delta == timedelta


def test_task_next_date_today():
    task = Task(name="test", interval=1, frequency="days")
    next_date = task.next_date()
    expected_next_date = datetime.datetime.today() + timedelta(days=1)
    assert next_date.year == expected_next_date.year
    assert next_date.month == expected_next_date.month
    assert next_date.day == expected_next_date.day


def test_task_not_recurring():
    task = Task(name="test", frequency="days")
    start_date = datetime.datetime(year=2024, month=1, day=1)
    assert task.next_date(start_date) == start_date


def test_task_bad_frequency():
    task = Task(name="test", interval=1, frequency="bad")
    with pytest.raises(ValueError):
        task.next_date()
