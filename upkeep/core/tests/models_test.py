import datetime
from datetime import date, timedelta

import pytest

from upkeep.core.models import Area, Schedule, Task

START_DATE = date(2024, 1, 1)


@pytest.fixture
@pytest.mark.django_db
def area():
    area = Area.objects.create(name="Test Area")

    for i in range(3):
        task = Task.objects.create(name=f"{i}", area=area)
        for j in range(3):
            Schedule.objects.create(
                task=task,
                due_date=START_DATE + timedelta(days=i + j),
                notes=f"{i}.{j}",
            )
    Task.objects.create(name="empty", area=area)

    return area


@pytest.mark.django_db
def test_area(area):
    areas = Area.objects.all()
    assert len(Area.objects.all()) == 1
    assert areas[0].tasks.count() == 4
    assert areas[0].name == area.name


@pytest.mark.django_db
def test_area_first_due_no_tasks():
    area = Area.objects.create(name="Test Area")
    assert area.first_due_schedule() is None


@pytest.mark.django_db
def test_area_first_due_no_schedules():
    area = Area.objects.create(name="Test Area")
    Task.objects.create(name="Test Task", area=area)
    assert area.tasks.count() == 1
    task = area.tasks.first()
    assert task
    assert task.schedules.count() == 0
    assert area.first_due_schedule() is None


@pytest.mark.django_db
def test_first_due_schedule(area):
    assert area.first_due_schedule().due_date == START_DATE


@pytest.mark.django_db
def test_first_due_equality(area):
    first_due_schedule = area.first_due_schedule()
    task: Task = area.tasks.first()
    assert first_due_schedule == task.first_due_schedule()


def test_task_is_recurring():
    task = Task(name="test", interval=None)
    assert not task.is_recurring()


# https://www.timeanddate.com/date/dateadded.html
@pytest.mark.parametrize(
    "interval, frequency, expected_delta",
    [
        (1, "days", timedelta(days=1)),
        (2, "weeks", timedelta(days=14)),
        (4, "weeks", timedelta(days=28)),
        (1, "months", timedelta(days=31)),
        (2, "months", timedelta(days=60)),  # 2024 is leap year
    ],
)
def test_task_next_date(interval, frequency, expected_delta):
    task = Task(name="test", interval=interval, frequency=frequency)
    start_date = datetime.datetime(year=2024, month=1, day=1)
    delta: datetime.timedelta = task.next_date(start_date) - start_date
    assert delta == expected_delta


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
