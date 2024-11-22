# celery_custom_task.py
from django.conf import settings
from celery import Task
from django.core.mail import send_mail
import traceback

from django.conf import settings
class BaseTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        stack_trace = traceback.format_exc()
        send_mail(
            f'Celery Task {self.name} Failed',
            f'Task {task_id} failed: {exc}\n\nStack Trace:\n{stack_trace}',
            "cicscapstone@gmail.com",
            ['cicscapstone@gmail.com'],
            fail_silently=True,
        )

    def on_success(self, retval, task_id, args, kwargs):
        send_mail(
            f'Celery Task {self.name} Succeeded',
            f'Task {task_id} succeeded',
            "cicscapstone@gmail.com",
            ['cicscapstone@gmail.com'],
            fail_silently=True,
        )