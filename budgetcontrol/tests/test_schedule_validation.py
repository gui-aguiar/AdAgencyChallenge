import pytest
from datetime import time
from django.core.exceptions import ValidationError
from budgetcontrol.models import Brand, Campaign, Schedule

@pytest.mark.django_db
def test_schedule_invalid_end_time_before_start():
    schedule = Schedule(
        campaign_id=1,
        day_of_week=0,
        start_time=time(10, 0),
        end_time=time(9, 0),
    )
    with pytest.raises(ValidationError):
        schedule.full_clean()


@pytest.mark.django_db
def test_schedule_invalid_interval_not_hour_multiple():
    schedule = Schedule(
        campaign_id=1,
        day_of_week=0,
        start_time=time(10, 0),
        end_time=time(10, 45),
    )
    with pytest.raises(ValidationError):
        schedule.full_clean()


@pytest.mark.django_db
def test_schedule_invalid_start_not_15min_interval():
    schedule = Schedule(
        campaign_id=1,
        day_of_week=0,
        start_time=time(10, 10),
        end_time=time(11, 10),
    )
    with pytest.raises(ValidationError):
        schedule.full_clean()


@pytest.mark.django_db
def test_schedule_valid_example():
    brand = Brand.objects.create(name="TestBrand", daily_budget=100.0, monthly_budget=3000.0)
    campaign = Campaign.objects.create(
        name="TestCampaign",
        brand=brand,
        is_active=True,
        cost_per_execution=10.0,
        total_spend_today=0.0,
        total_spend_month=0.0,
    )
    schedule = Schedule(
        campaign=campaign,
        day_of_week=0,
        start_time=time(10, 0),
        end_time=time(11, 0),
    )
    try:
        schedule.full_clean()
    except Exception as e:
        pytest.fail(f"ValidationError raised unexpectedly for valid schedule: {e}")
