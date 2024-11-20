import datetime

from dateutil.relativedelta import relativedelta
from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)


class Task(models.Model):
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    duration = models.DurationField(blank=True, null=True)
    interval = models.PositiveIntegerField(blank=True, null=True)
    frequency = models.CharField(
        max_length=10,
        choices=[("days", "Days"), ("weeks", "Weeks"), ("months", "Months")],
        default="months",
    )
    areas = models.ManyToManyField(Area, related_name="tasks")

    def is_recurring(self):
        return self.interval is not None

    def next_date(self, start_date=datetime.date.today()):
        if not self.is_recurring():
            return None

        match self.frequency:
            case "days":
                return start_date + relativedelta(days=self.interval)
            case "weeks":
                return start_date + relativedelta(weeks=self.interval)
            case "months":
                return start_date + relativedelta(months=self.interval)

    def __str__(self):
        return self.name


class Consumable(models.Model):
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    unit = models.CharField(max_length=25)
    quantity = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    tasks = models.ManyToManyField(
        Task,
        through="TaskConsumable",
        related_name="consumables",
    )

    def __str__(self):
        return self.name


class TaskConsumable(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("task", "consumable")


class Schedule(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    due_date = models.DateField()


class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
