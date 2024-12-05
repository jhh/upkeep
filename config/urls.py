from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from upkeep.core.views import (
    areas_view,
    consumables_view,
    edit_area_view,
    edit_consumable_view,
    edit_schedule_view,
    edit_task_consumable_view,
    edit_task_view,
    home_view,
    new_area_view,
    new_consumable_view,
    new_schedule_view,
    new_task_consumable_view,
    new_task_view,
    task_view,
    tasks_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("areas/", areas_view, name="areas"),
    path("areas/<int:pk>/edit", edit_area_view, name="area_edit"),
    path("areas/new/", new_area_view, name="area_new"),
    path("tasks/", tasks_view, name="tasks"),
    path("tasks/<int:pk>/", task_view, name="task"),
    path("tasks/<int:pk>/edit", edit_task_view, name="task_edit"),
    path("tasks/new/", new_task_view, name="task_new"),
    path("schedules/<int:pk>/edit", edit_schedule_view, name="schedule_edit"),
    path("schedules/new/", new_schedule_view, name="schedule_new"),
    path("consumables/", consumables_view, name="consumables"),
    path("consumables/<int:pk>/edit", edit_consumable_view, name="consumable_edit"),
    path("consumables/new/", new_consumable_view, name="consumable_new"),
    path(
        "task/consumables/<int:pk>/edit",
        edit_task_consumable_view,
        name="task_consumable_edit",
    ),
    path("task/<int:task>/consumables/new/", new_task_consumable_view, name="task_consumable_new"),
    path("favicon.ico", RedirectView.as_view(url="/static/ui/favicon.ico", permanent=True)),
    path("icon.svg", RedirectView.as_view(url="/static/ui/icon.svg", permanent=True)),
    path(
        "apple-touch-icon.png",
        RedirectView.as_view(url="/static/ui/apple-touch-icon.png", permanent=True),
    ),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls  # type: ignore

    urlpatterns += debug_toolbar_urls()
