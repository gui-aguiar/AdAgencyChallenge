import pytest
from decimal import Decimal
from datetime import time
from budgetcontrol.models import Brand, Campaign, Schedule, Spend


@pytest.mark.django_db
def test_create_brand() -> None:
    brand = Brand.objects.create(
        name="Coca-Cola",
        daily_budget=Decimal("100.00"),
        monthly_budget=Decimal("3000.00")
    )
    assert brand.pk is not None
    assert brand.name == "Coca-Cola"


@pytest.mark.django_db
def test_create_campaign() -> None:
    brand = Brand.objects.create(name="Pepsi", daily_budget=200, monthly_budget=6000)
    campaign = Campaign.objects.create(
        name="Pepsi Summer",
        brand=brand,
        is_active=True,
        cost_per_execution=Decimal("25.00"),
        total_spend_today=Decimal("0.00"),
        total_spend_month=Decimal("0.00"),
    )
    assert campaign.pk is not None
    assert campaign.brand == brand


@pytest.mark.django_db
def test_create_schedule() -> None:
    brand = Brand.objects.create(name="Sprite", daily_budget=100, monthly_budget=3000)
    campaign = Campaign.objects.create(
        name="Sprite Test",
        brand=brand,
        is_active=True,
        cost_per_execution=10,
        total_spend_today=0,
        total_spend_month=0,
    )
    schedule = Schedule.objects.create(
        campaign=campaign,
        day_of_week=2,
        start_time=time(12, 0),
        end_time=time(13, 0)
    )
    assert schedule.pk is not None
    assert schedule.day_of_week == 2


@pytest.mark.django_db
def test_create_spend() -> None:
    brand = Brand.objects.create(name="Fanta", daily_budget=150, monthly_budget=4000)
    campaign = Campaign.objects.create(
        name="Fanta Fun",
        brand=brand,
        is_active=True,
        cost_per_execution=15,
        total_spend_today=0,
        total_spend_month=0,
    )
    spend = Spend.objects.create(
        campaign=campaign,
        amount=Decimal("15.00")
    )
    assert spend.pk is not None
    assert spend.amount == Decimal("15.00")
