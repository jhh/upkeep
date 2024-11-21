from django.contrib import admin

from .models import Area, Consumable, Schedule, Task, TaskConsumable

admin.site.register(Area)
admin.site.register(Consumable)
admin.site.register(TaskConsumable)
admin.site.register(Schedule)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["area__name", "name"]
    list_display_links = ["name"]
    list_select_related = True
