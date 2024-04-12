from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "walnuteq.settings")

app = Celery("walnuteq")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


# Celery Beat Schedule Configuration
"""This configuration sets up periodic tasks for sending survey questions and curriculum messages every hour
within the specified time range (8 AM to 8 PM)."""

app.conf.beat_schedule = {
    "send-survey-every-hour": {
        "task": "scheduler.tasks.send_survey_questions",
        "schedule": crontab(
            minute=0, hour="8-20"
        ),  # Run every hour from 8 AM to 8 PM
        "options": {
            "timezone": os.environ.get("TIME_ZONE", "UTC")
        },  # Set the timezone fo scheduling
    },
    "send-curriculum-every-hour": {
        "task": "scheduler.tasks.send_curriculum_schedule",
        "schedule": crontab(
            minute=0, hour="8-20"
        ),  # Run every hour from 8 AM to 8 PM
        "options": {
            "timezone": os.environ.get("TIME_ZONE", "UTC")
        },  # Set the timezone for scheduling
    },
}
# Load task modules from all registered Django apps.
app.autodiscover_tasks()
