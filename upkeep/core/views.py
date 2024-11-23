# Create your views here.
from itertools import groupby
from operator import itemgetter

from django.db.models import Count
from django.http import Http404
from django.shortcuts import render

from .models import Area, Task


def areas_view(request):
    if request.method == "GET":
        areas = Area.objects.annotate(task_count=Count("tasks")).all()

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
        tasks = Task.objects.select_related("area")

        area = request.GET.get("area")
        if area:
            tasks = tasks.filter(area=area)

        tasks = tasks.values("area__name", "id", "name").order_by("area__name", "name")
        grouped_tasks = [
            {"area": key, "tasks": list(group)}
            for key, group in groupby(tasks, key=itemgetter("area__name"))
        ]

        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": grouped_tasks[0]["area"] if area else "Tasks", "url": None},
        ]

        return render(
            request,
            "core/task_list.html",
            {"grouped_tasks": grouped_tasks, "breadcrumbs": breadcrumbs},
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
