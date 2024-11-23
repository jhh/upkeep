from datetime import date, timedelta

import pytest

from upkeep.core.models import Area, Schedule, Task

START_DATE = date(2024, 1, 1)


@pytest.fixture
def area(db):
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
    assert area.tasks.first().schedules.count() == 0
    assert area.first_due_schedule() is None


@pytest.mark.django_db
def test_first_due_schedule(area):
    assert area.first_due_schedule().due_date == START_DATE
