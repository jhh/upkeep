import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Sum


class Area(models.Model):
    name = models.CharField("area name", max_length=200)
    notes = models.TextField(blank=True)

    def first_due_schedule(self) -> "Schedule | None":
        schedules: list["Schedule"] = []
        for task in self.tasks.prefetch_related("schedules").all():
            schedules += task.schedules.filter(completion_date__isnull=True).all()
        return min(schedules, key=lambda s: s.due_date) if schedules else None

    def __str__(self):
        return self.name


class TaskManager(models.Manager):
    def get_upcoming_due_tasks(self, within_days: int = 14, start_date=datetime.date.today()):
        return self.filter(
            schedules__due_date__lte=start_date + datetime.timedelta(days=within_days),
            schedules__completion_date__isnull=True,
        )


class Task(models.Model):
    name = models.CharField("task name", max_length=200)
    notes = models.TextField(blank=True)
    duration = models.DurationField(blank=True, null=True)
    interval = models.PositiveIntegerField(blank=True, null=True)
    frequency = models.CharField(
        max_length=10,
        choices=[("days", "Days"), ("weeks", "Weeks"), ("months", "Months")],
        default="months",
    )
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="tasks")
    objects = TaskManager()

    def is_recurring(self) -> bool:
        return self.interval is not None

    def next_date(self, start_date=datetime.date.today()) -> datetime.date:
        if not self.interval:
            return start_date

        match self.frequency:
            case "days":
                return start_date + relativedelta(days=self.interval)
            case "weeks":
                return start_date + relativedelta(weeks=self.interval)
            case "months":
                return start_date + relativedelta(months=self.interval)
            case _:
                raise ValueError("bad frequency")

    def first_due_schedule(self) -> "Schedule | None":
        return self.schedules.filter(completion_date__isnull=True).order_by("due_date").first()

    def __str__(self):
        return f"{self.name} ({self.id})"


class Consumable(models.Model):
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    url = models.URLField("consumable url", blank=True)
    unit = models.CharField(max_length=25)
    quantity = models.PositiveIntegerField("quantity on-hand")
    updated_at = models.DateTimeField(auto_now=True)
    tasks = models.ManyToManyField(
        Task,
        through="core.TaskConsumable",
        related_name="consumables",
    )

    def quantity_needed(self) -> int:
        return TaskConsumable.objects.filter(consumable=self).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]

    def __str__(self):
        return self.name


class TaskConsumable(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("quantity required", default=1)

    class Meta:
        unique_together = ("task", "consumable")


class Schedule(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="schedules")
    due_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    def is_complete(self) -> bool:
        return self.completion_date is not None

    def reschedule(self):
        start_date = self.completion_date or datetime.date.today()
        next_date = self.task.next_date(start_date)
        if not next_date:
            raise ValueError("Cannot reschedule a non-recurring task")
        Schedule.objects.create(task=self.task, due_date=next_date)

    class Meta:
        ordering = ("due_date",)
