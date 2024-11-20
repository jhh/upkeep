from django.contrib import admin

from .models import Area, Consumable, Schedule, Task, TaskHistory

admin.site.register(Area)
admin.site.register(Task)
admin.site.register(Consumable)
admin.site.register(Schedule)
admin.site.register(TaskHistory)
