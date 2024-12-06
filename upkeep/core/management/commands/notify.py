from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from upkeep.core.models import Task


class Command(BaseCommand):
    def handle(self, *args, **options):
        tasks = Task.objects.get_upcoming_due_tasks()
        text_content = render_to_string("core/notify_email.txt", {"tasks": tasks})
        send_mail(
            "Upkeep Task Notification",
            text_content,
            "upkeep@j3ff.io",
            ["jeff@j3ff.io"],
            fail_silently=False,
        )
