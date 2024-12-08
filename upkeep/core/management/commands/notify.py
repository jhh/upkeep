import logging

from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from upkeep.core.models import Task, TaskConsumable

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        tasks_queryset = Task.objects.get_upcoming_due_tasks(within_days=14)
        if not tasks_queryset:
            logger.info("No upcoming due tasks found")
            return

        tasks = []
        for task in tasks_queryset:
            task_consumables = TaskConsumable.objects.filter(task=task).all()
            is_ready = True
            for tc in task_consumables:
                if tc.quantity > tc.consumable.quantity:
                    is_ready = False

            tasks.append(
                {
                    "id": task.id,
                    "name": task.name,
                    "due_date": task.first_due_schedule().due_date,
                    "is_ready": is_ready,
                },
            )

        context = {
            "tasks": tasks,
            "period": "within the next two weeks",
        }
        text_content = render_to_string("core/notify_email.txt", context)
        html_content = render_to_string("core/notify_email.html", context)
        send_mail(
            "Upkeep Task Notification",
            text_content,
            html_message=html_content,
            from_email="Upkeep Home Maintenance Tracker <upkeep@j3ff.io>",
            recipient_list=["jeff@j3ff.io"],
            fail_silently=False,
        )
