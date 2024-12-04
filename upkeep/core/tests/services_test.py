import pytest

from upkeep.core.services import get_areas_tasks_schedules


@pytest.mark.django_db
def test_get_areas_tasks_schedules(area, start_date):
    a = get_areas_tasks_schedules()
    assert len(a) == 1
    row = a[0]
    assert row["name"] == area.name
    assert row["id"] == area.id
    assert row["task_count"] == 4
    assert row["due_date"] == start_date
    assert row["due_task_id"] == area.tasks.first().id
