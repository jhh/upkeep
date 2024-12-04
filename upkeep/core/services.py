from operator import attrgetter

from django.db.models import Count

from .models import Area, Schedule


def get_areas_tasks_schedules() -> list[dict[str, int | str]]:
    area_queryset = (
        Area.objects.prefetch_related("tasks__schedules").annotate(task_count=Count("tasks")).all()
    )

    areas = []
    for area in area_queryset:
        row = {
            "id": area.id,
            "name": area.name,
            "task_count": area.task_count,
        }

        schedules: list[Schedule] = []
        for task in area.tasks.all():
            schedules += task.schedules.filter(completion_date__isnull=True).all()

        if schedules:
            first = min(schedules, key=attrgetter("due_date"))
            row |= {"due_date": first.due_date, "due_task_id": first.task_id}

        areas.append(row)

    return areas
