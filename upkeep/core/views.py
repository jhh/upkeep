# Create your views here.

from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from django_htmx.http import HttpResponseLocation

from .forms import AreaForm
from .models import Area, Schedule, Task


@require_http_methods(["GET", "POST"])
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

            schedules: list[Schedule] = []
            for task in area.tasks.all():
                schedules += task.schedules.filter(completion_date__isnull=True).all()

            if schedules:
                first = min(schedules, key=lambda s: s.due_date)
                row.update({"due_date": first.due_date, "due_task_id": first.task_id})

            areas.append(row)

        return render(
            request,
            "core/area_list.html",
            {"areas": areas},
        )

    elif request.method == "POST":
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("areas")
        return render(request, "core/area_form.html", {"area_form": form})

    elif request.method == "DELETE":
        return HttpResponseLocation(reverse("areas"))


@require_GET
def new_area_view(request):
    form = AreaForm()
    return render(request, "core/area_form.html", {"area_form": form})


@require_http_methods(["GET", "POST", "DELETE"])
def area_view(request, pk):
    area = get_object_or_404(Area, pk=pk)
    if request.method == "GET":
        form = AreaForm(instance=area)
        return render(request, "core/area_form.html", {"area_form": form})
    if request.method == "POST":
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("areas"))
        return render(request, "core/area_form.html", {"area_form": form})
    if request.method == "DELETE":
        area.delete()
        return HttpResponseLocation(reverse("areas"))


def tasks_view(request):
    if request.method == "GET":
        tasks_queryset = Task.objects.select_related("area").prefetch_related("schedules")

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
        return render(
            request,
            "core/task.html",
            {"task": task},
        )
