from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from upkeep.core.views import (
    area_view,
    areas_view,
    edit_task_view,
    new_area_view,
    new_task_view,
    task_view,
    tasks_view,
)

urlpatterns = [
    path("", RedirectView.as_view(url="/areas"), name="home"),
    path("areas/", areas_view, name="areas"),
    path("areas/<int:pk>/", area_view, name="area"),
    path("areas/new/", new_area_view, name="area_new"),
    path("tasks/", tasks_view, name="tasks"),
    path("tasks/<int:pk>/", task_view, name="task"),
    path("tasks/<int:pk>/edit", edit_task_view, name="task_edit"),
    path("tasks/new/", new_task_view, name="task_new"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls  # type: ignore

    urlpatterns += debug_toolbar_urls()
