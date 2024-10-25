
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TBMS.settings')

app = Celery('TBMS')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-database-every-minute': {
        'task': 'Treasury.tasks.check_database',
        'schedule': crontab(minute='*/1'),  # Runs every minute
    },
}
