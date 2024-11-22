import datetime

from dateutil.relativedelta import relativedelta
from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


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
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="tasks")

    def is_recurring(self):
        return self.interval is not None

    def next_date(self, start_date=datetime.date.today()):
        if not self.is_recurring():
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

    def __str__(self):
        return f"{self.area.name} -> {self.name}"


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
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("task", "consumable")

    def __str__(self):
        return f"{self.task.name} -> {self.consumable.name}"


class Schedule(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="schedules")
    due_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    def is_complete(self):
        return self.completion_date is not None

    def reschedule(self):
        start_date = self.completion_date or datetime.date.today()
        next_date = self.task.next_date(start_date)
        if not next_date:
            raise ValueError("Cannot reschedule a non-recurring task")
        Schedule.objects.create(task=self.task, due_date=next_date)

    def __str__(self):
        if self.is_complete():
            return f"{self.task.area.name} -> {self.task.name} [completed: {self.completion_date}]"
        return f"{self.task.area.name} -> {self.task.name} [due: {self.due_date}]"
