import pytest
from datetime import time, timedelta
from decimal import Decimal
from django.utils.timezone import now
from budgetcontrol.models import Brand, Campaign, Schedule
from budgetcontrol.tasks import (
    check_and_execute_campaigns,
    reset_daily_budgets,
    reset_monthly_budgets,
)


@pytest.mark.django_db
def test_campaign_executes_within_budget_and_window() -> None:
    brand = Brand.objects.create(name="Brand1", daily_budget=100, monthly_budget=1000)
    campaign = Campaign.objects.create(
        brand=brand,
        name="Campaign1",
        is_active=True,
        cost_per_execution=25,
        total_spend_today=0,
        total_spend_month=0,
    )
    Schedule.objects.create(
        campaign=campaign,
        day_of_week=now().weekday(),
        start_time=(now() - timedelta(minutes=10)).time(),
        end_time=(now() + timedelta(minutes=10)).time(),
    )

    check_and_execute_campaigns()

    campaign.refresh_from_db()
    assert campaign.total_spend_today == 25
    assert campaign.total_spend_month == 25


@pytest.mark.django_db
def test_campaign_not_executed_outside_schedule() -> None:
    brand = Brand.objects.create(name="Brand2", daily_budget=100, monthly_budget=1000)
    campaign = Campaign.objects.create(
        brand=brand,
        name="Campaign2",
        is_active=True,
        cost_per_execution=25,
        total_spend_today=0,
        total_spend_month=0,
    )
    Schedule.objects.create(
        campaign=campaign,
        day_of_week=now().weekday(),
        start_time=time(0, 0),
        end_time=time(1, 0),
    )

    check_and_execute_campaigns()

    campaign.refresh_from_db()
    assert campaign.total_spend_today == 0
    assert campaign.total_spend_month == 0


@pytest.mark.django_db
def test_campaign_deactivates_on_daily_budget_exceed() -> None:
    brand = Brand.objects.create(name="Brand3", daily_budget=20, monthly_budget=1000)
    campaign = Campaign.objects.create(
        brand=brand,
        name="Campaign3",
        is_active=True,
        cost_per_execution=25,
        total_spend_today=0,
        total_spend_month=0,
    )
    Schedule.objects.create(
        campaign=campaign,
        day_of_week=now().weekday(),
        start_time=(now() - timedelta(minutes=10)).time(),
        end_time=(now() + timedelta(minutes=10)).time(),
    )

    check_and_execute_campaigns()

    campaign.refresh_from_db()
    assert not campaign.is_active
    assert campaign.total_spend_today == 0


@pytest.mark.django_db
def test_campaign_reactivation_on_daily_reset() -> None:
    brand = Brand.objects.create(name="Brand4", daily_budget=100, monthly_budget=1000)
    campaign = Campaign.objects.create(
        brand=brand,
        name="Campaign4",
        is_active=False,
        cost_per_execution=50,
        total_spend_today=50,
        total_spend_month=50,
    )
    reset_daily_budgets()

    campaign.refresh_from_db()
    assert campaign.is_active
    assert campaign.total_spend_today == 0


@pytest.mark.django_db
def test_campaign_reactivation_on_monthly_reset() -> None:
    brand = Brand.objects.create(name="Brand5", daily_budget=100, monthly_budget=1000)
    campaign = Campaign.objects.create(
        brand=brand,
        name="Campaign5",
        is_active=False,
        cost_per_execution=50,
        total_spend_today=50,
        total_spend_month=1000,
    )
    reset_monthly_budgets()

    campaign.refresh_from_db()
    assert campaign.is_active
    assert campaign.total_spend_month == 0
