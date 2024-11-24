# Create your views here.

from django.db.models import Count
from django.http import Http404
from django.shortcuts import render

from .models import Area, Task


def areas_view(request):
    if request.method == "GET":
        area_queryset = (
            Area.objects.prefetch_related("tasks__schedules")
            .annotate(task_count=Count("tasks"))
            .all()
        )

        areas = []
        for area in area_queryset:
            row = {
                "id": area.id,
                "name": area.name,
                "task_count": area.task_count,
            }

            schedules = []
            for task in area.tasks.all():
                schedules += task.schedules.filter(completion_date__isnull=True).all()

            if schedules:
                first = min(schedules, key=lambda s: s.due_date)
                row.update({"due_date": first.due_date, "due_task_id": first.task_id})

            areas.append(row)

        breadcrumbs = [
            {"name": "Home", "url": None},
        ]

        return render(
            request,
            "core/area_list.html",
            {"areas": areas, "breadcrumbs": breadcrumbs},
        )


def tasks_view(request):
    if request.method == "GET":
        tasks_queryset = Task.objects.select_related("area").prefetch_related(
            "schedules",
        )

        area = request.GET.get("area")
        if area:
            tasks_queryset = tasks_queryset.filter(area=area)

        tasks = []
        for task in tasks_queryset:
            row = {
                "id": task.id,
                "area_name": task.area.name,
                "name": task.name,
            }

            schedules = task.schedules.filter(completion_date__isnull=True).all()
            if schedules:
                first = min(schedules, key=lambda s: s.due_date)
                row.update({"due_date": first.due_date})

            tasks.append(row)

        return render(
            request,
            "core/task_list.html",
            {"tasks": tasks},
        )


def task_view(request, pk):
    try:
        task = Task.objects.select_related("area").get(pk=pk)
    except Task.DoesNotExist:
        raise Http404

    if request.method == "GET":
        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": task.area.name, "url": f"/tasks/?area={task.area.pk}"},
            {"name": task.name, "url": None},
        ]

        return render(
            request,
            "core/task.html",
            {"task": task, "breadcrumbs": breadcrumbs},
        )
