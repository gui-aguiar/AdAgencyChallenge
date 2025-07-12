from __future__ import annotations

import os
from celery import Celery
from celery import shared_task
from typing import Any

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AdAgency.settings')

app = Celery('AdAgency')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True) # type: ignore[misc]
def debug_task(*args: Any, **kwargs: Any) -> None:
    print(f'Task executed with args={args}, kwargs={kwargs}')
