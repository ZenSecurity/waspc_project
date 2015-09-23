from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings


if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

waspc_celery = Celery('waspc')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
waspc_celery.config_from_object('django.conf:settings')
waspc_celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
