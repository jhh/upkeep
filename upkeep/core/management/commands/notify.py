import logging

from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from upkeep.core.services import get_upcoming_due_tasks

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        tasks = get_upcoming_due_tasks(within_days=14)

        if not tasks:
            logger.info("No upcoming due tasks found")
            return

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
