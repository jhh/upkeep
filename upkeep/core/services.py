import logging
from operator import attrgetter
from typing import Any

from django.db.models import Count

from .models import Area, Schedule, Task

logger = logging.getLogger(__name__)


def get_areas_tasks_schedules() -> list[dict[str, Any]]:
    area_queryset = (
        Area.objects.prefetch_related("tasks__schedules").annotate(task_count=Count("tasks")).all()
    )

    areas = []
    for area in area_queryset:
        row = {"id": area.id, "name": area.name, "task_count": area.task_count}

        schedules: list[Schedule] = []
        for task in area.tasks.all():
            schedules += task.schedules.filter(completion_date__isnull=True).all()

        if schedules:
            first = min(schedules, key=attrgetter("due_date"))
            row |= {"due_date": first.due_date, "due_task_id": first.task_id}

        areas.append(row)
    return areas


def get_tasks_schedules(area=None) -> list[dict[str, Any]]:
    tasks_queryset = Task.objects.select_related("area").prefetch_related("schedules")

    if area:
        tasks_queryset = tasks_queryset.filter(area=area)

    tasks = []
    for task in tasks_queryset:
        row = {"id": task.id, "area_name": task.area.name, "name": task.name}

        schedules = task.schedules.filter(completion_date__isnull=True).all()
        if schedules:
            first = min(schedules, key=attrgetter("due_date"))
            row |= {"due_date": first.due_date}

        tasks.append(row)
    return tasks
