import os

from celery import Celery
from celery.utils.log import get_task_logger
from decouple import config
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'braikout.settings')

app = Celery('braikout', broker=config('REDISCLOUD_URL', default='redis://localhost:6379'))

app.conf.timezone = 'UTC'

logger = get_task_logger(__name__)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.broker_url = config('REDISCLOUD_URL', default='redis://localhost:6379')
app.conf.result_backend = config('REDISCLOUD_URL', default='redis://localhost:6379')

