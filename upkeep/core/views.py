# Create your views here.
from itertools import groupby
from operator import itemgetter

from django.shortcuts import render

from .models import Area, Task


def areas_view(request):
    if request.method == "GET":
        areas = Area.objects.all()
        return render(request, "core/area_list.html", {"areas": areas})


def tasks_view(request):
    if request.method == "GET":
        tasks = Task.objects.select_related("area")

        area = request.GET.get("area")
        if area:
            tasks = tasks.filter(area=area)

        tasks = tasks.values("area__name", "name").order_by("area__name", "name")
        grouped_tasks = [
            {"area": key, "tasks": list(group)}
            for key, group in groupby(tasks, key=itemgetter("area__name"))
        ]
        return render(request, "core/task_list.html", {"grouped_tasks": grouped_tasks})
