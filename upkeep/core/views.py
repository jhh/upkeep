from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from django_htmx.http import HttpResponseLocation

from .forms import AreaForm, ConsumableForm, ScheduleForm, TaskConsumableForm, TaskForm
from .models import Area, Consumable, Schedule, Task, TaskConsumable
from .services import get_areas_tasks_schedules, get_tasks_schedules


@require_GET
def areas_view(request):
    areas = get_areas_tasks_schedules()
    return render(request, "core/area_list.html", {"areas": areas})


@require_http_methods(["GET", "POST"])
def new_area_view(request):
    if request.method == "GET":
        form = AreaForm()
        return render(request, "core/form.html", {"title": "area form", "form": form})

    if request.method == "POST":
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("areas"), target="body")
        return render(request, "core/form.html", {"title": "area form", "form": form})


@require_http_methods(["GET", "POST", "DELETE"])
def edit_area_view(request, pk):
    area = get_object_or_404(Area, pk=pk)

    if request.method == "GET":
        form = AreaForm(instance=area)
        return render(request, "core/form.html", {"title": "area form", "form": form})

    if request.method == "POST":
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("areas"), target="body")
        return render(request, "core/form.html", {"title": "area form", "form": form})

    if request.method == "DELETE":
        area.delete()
        return HttpResponseLocation(reverse("areas"), target="body")


@require_GET
def tasks_view(request):
    area = request.GET.get("area")
    tasks = get_tasks_schedules(area)
    return render(request, "core/task_list.html", {"tasks": tasks})


@require_http_methods(["GET", "POST"])
def new_task_view(request):
    if request.method == "GET":
        form = TaskForm()
        return render(request, "core/form.html", {"title": "task form", "form": form})

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tasks")
        return render(request, "core/form.html", {"title": "task form", "form": form})


@require_http_methods(["GET", "POST", "DELETE"])
def edit_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "GET":
        form = TaskForm(instance=task)
        return render(request, "core/form.html", {"title": "task form", "form": form})

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("tasks"), target="body")
        return render(request, "core/form.html", {"title": "task form", "form": form})

    if request.method == "DELETE":
        task.delete()
        return HttpResponseLocation(reverse("tasks"), target="body")


@require_GET
def task_view(request, pk):
    try:
        task = (
            Task.objects.select_related("area")
            .prefetch_related("schedules")
            .order_by("schedules__due_date")
            .get(pk=pk)
        )
        task_consumables = TaskConsumable.objects.filter(task=task)
    except Task.DoesNotExist:
        raise Http404

    return render(
        request,
        "core/task.html",
        {"task": task, "task_consumables": task_consumables},
    )


@require_http_methods(["GET", "POST"])
def new_schedule_view(request):
    if request.method == "GET":
        task_id = request.GET.get("task")
        form = ScheduleForm(initial={"task": task_id})
        return render(request, "core/form.html", {"form": form})

    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(
                reverse("task", args=[form.instance.task.id]),
                target="body",
            )
        return render(request, "core/form.html", {"form": form})


@require_http_methods(["GET", "POST", "DELETE"])
def edit_schedule_view(request, pk):
    try:
        schedule = Schedule.objects.select_related("task").get(pk=pk)
    except Task.DoesNotExist:
        raise Http404

    if request.method == "GET":
        form = ScheduleForm(instance=schedule)
        return render(request, "core/form.html", {"form": form})

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(
                reverse("task", args=[form.instance.task.id]),
                target="body",
            )
        return render(request, "core/form.html", {"form": form})

    if request.method == "DELETE":
        task_id = schedule.task.id
        schedule.delete()
        return HttpResponseLocation(reverse("task", args=[task_id]), target="body")


@require_GET
def consumables_view(request):
    consumables = Consumable.objects.all()
    return render(request, "core/consumable_list.html", {"consumables": consumables})


@require_http_methods(["GET", "POST"])
def new_consumable_view(request):
    if request.method == "GET":
        form = ConsumableForm()
        return render(request, "core/form.html", {"title": "consumable form", "form": form})

    if request.method == "POST":
        form = ConsumableForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("consumables"), target="body")
        return render(request, "core/form.html", {"title": "consumable form", "form": form})


@require_http_methods(["GET", "POST", "DELETE"])
def edit_consumable_view(request, pk):
    consumable = get_object_or_404(Consumable, pk=pk)

    if request.method == "GET":
        form = ConsumableForm(instance=consumable)
        return render(request, "core/form.html", {"form": form})

    if request.method == "POST":
        form = ConsumableForm(request.POST, instance=consumable)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("consumables"), target="body")
        return render(request, "core/form.html", {"title": "consumable form", "form": form})

    if request.method == "DELETE":
        consumable.delete()
        return HttpResponseLocation(reverse("consumables"), target="body")


@require_http_methods(["GET", "POST"])
def new_task_consumable_view(request, task):
    task = get_object_or_404(Task, pk=task)

    if request.method == "GET":
        form = TaskConsumableForm(initial={"task": task})
        return render(request, "core/form.html", {"title": "task consumable form", "form": form})

    if request.method == "POST":
        form = TaskConsumableForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(
                reverse("task", args=[form.instance.task.id]),
                target="body",
            )
        return render(request, "core/form.html", {"title": "task consumable form", "form": form})


@require_http_methods(["GET", "POST", "DELETE"])
def edit_task_consumable_view(request, pk):
    task_consumable = get_object_or_404(TaskConsumable, pk=pk)

    if request.method == "GET":
        form = TaskConsumableForm(instance=task_consumable)
        return render(request, "core/form.html", {"form": form})

    if request.method == "POST":
        form = TaskConsumableForm(request.POST, instance=task_consumable)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(
                reverse("task", args=[form.instance.task.id]),
                target="body",
            )
        return render(request, "core/form.html", {"title": "task consumable form", "form": form})

    if request.method == "DELETE":
        task_id = task_consumable.task.id
        task_consumable.delete()
        return HttpResponseLocation(reverse("task", args=[task_id]), target="body")
