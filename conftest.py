from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.test.utils import override_settings

from upkeep.core.models import Area, Schedule, Task


@pytest.fixture(scope="session", autouse=True)
def test_settings():
    with override_settings(**TEST_SETTINGS):
        yield


TEST_SETTINGS = {
    "STATIC_ROOT": None,
    "STORAGES": {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
}


@pytest.fixture
def start_date():
    return date(2024, 1, 1)


# noinspection PyUnusedLocal
@pytest.fixture
def area(db, start_date):
    area = Area.objects.create(name="Test Area")

    for i in range(3):
        # create tasks 0, 1, 2
        task = Task.objects.create(name=f"{i}", area=area)
        for j in range(3):
            Schedule.objects.create(
                task=task,
                due_date=start_date + timedelta(days=i + j),
                notes=f"{i}.{j}",
            )
    # create task 4
    Task.objects.create(name="empty", area=area)

    return area
