from __future__ import annotations

from celery import shared_task
from datetime import datetime, time
from django.utils.timezone import now
from .models import Schedule, Spend

@shared_task(bind=False) # type: ignore[misc]
def check_and_execute_campaigns() -> None:
    current_dt = now()
    current_weekday = current_dt.weekday()
    current_time = current_dt.time()

    schedules = Schedule.objects.filter(day_of_week=current_weekday)

    for schedule in schedules:
        campaign = schedule.campaign

        if not campaign.is_active:
            continue

        if not (schedule.start_time <= current_time < schedule.end_time):
            continue

        if schedule.last_execution and schedule.last_execution.date() == current_dt.date():
            continue

        if campaign.total_spend_today + campaign.cost_per_execution > campaign.brand.daily_budget:
            campaign.is_active = False
            campaign.save(update_fields=["is_active"])
            continue

        if campaign.total_spend_month + campaign.cost_per_execution > campaign.brand.monthly_budget:
            campaign.is_active = False
            campaign.save(update_fields=["is_active"])
            continue

        Spend.objects.create(
            campaign=campaign,
            amount=campaign.cost_per_execution,
        )

        campaign.total_spend_today += campaign.cost_per_execution
        campaign.total_spend_month += campaign.cost_per_execution
        campaign.save(update_fields=["total_spend_today", "total_spend_month"])

        schedule.last_execution = current_dt
        schedule.save(update_fields=["last_execution"])

@shared_task(bind=False) # type: ignore[misc]
def reset_daily_budgets() -> None:
    from .models import Campaign, Schedule

    Campaign.objects.update(total_spend_today=0)

    Schedule.objects.update(last_execution=None)

    campaigns = Campaign.objects.select_related("brand").all()
    for campaign in campaigns:
        brand = campaign.brand
        if campaign.total_spend_month < brand.monthly_budget:
            if not campaign.is_active:
                campaign.is_active = True
                campaign.save(update_fields=["is_active"])

@shared_task(bind=False) # type: ignore[misc]
def reset_monthly_budgets() -> None:
    from .models import Campaign

    Campaign.objects.update(total_spend_month=0)

    campaigns = Campaign.objects.select_related("brand").all()
    for campaign in campaigns:
        brand = campaign.brand
        if campaign.total_spend_today < brand.daily_budget:
            if not campaign.is_active:
                campaign.is_active = True
                campaign.save(update_fields=["is_active"])
