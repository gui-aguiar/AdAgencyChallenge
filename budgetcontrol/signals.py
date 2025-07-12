from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.utils.timezone import now
from datetime import datetime
from typing import Any
from django.apps import AppConfig
from django.db.models.signals import ModelSignal

@receiver(post_migrate)
def setup_periodic_tasks(sender: type[AppConfig], **kwargs: Any) -> None:
    if sender.name != "budgetcontrol":
        return

    interval, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)
    PeriodicTask.objects.get_or_create(
        name="Execute Campaigns",
        task="budgetcontrol.tasks.check_and_execute_campaigns",
        defaults={"interval": interval, "start_time": now()},
    )

    daily_cron, _ = CrontabSchedule.objects.get_or_create(
        minute="0", hour="0", day_of_week="*", day_of_month="*", month_of_year="*"
    )
    PeriodicTask.objects.get_or_create(
        name="Reset Daily Budgets",
        task="budgetcontrol.tasks.reset_daily_budgets",
        defaults={"crontab": daily_cron, "start_time": now()},
    )

    monthly_cron, _ = CrontabSchedule.objects.get_or_create(
        minute="0", hour="0", day_of_month="1", month_of_year="*", day_of_week="*"
    )
    PeriodicTask.objects.get_or_create(
        name="Reset Monthly Budgets",
        task="budgetcontrol.tasks.reset_monthly_budgets",
        defaults={"crontab": monthly_cron, "start_time": now()},
    )
