from __future__ import annotations

from django.contrib import admin
from .models import Brand, Campaign, Schedule, Spend

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin as BaseAdmin
    class BrandAdmin(BaseAdmin[Brand]): ...
    class CampaignAdmin(BaseAdmin[Campaign]): ...
    class ScheduleAdmin(BaseAdmin[Schedule]): ...
    class SpendAdmin(BaseAdmin[Spend]): ...
else:
    @admin.register(Brand)
    class BrandAdmin(admin.ModelAdmin):
        list_display = ("name", "daily_budget", "monthly_budget")

    @admin.register(Campaign)
    class CampaignAdmin(admin.ModelAdmin):
        list_display = ("name", "brand", "is_active", "cost_per_execution", "total_spend_today", "total_spend_month")
        list_filter = ("is_active", "brand")

    @admin.register(Schedule)
    class ScheduleAdmin(admin.ModelAdmin):
        list_display = ("campaign", "day_of_week", "start_time", "end_time", "last_execution")
        list_filter = ("day_of_week", "campaign")

    @admin.register(Spend)
    class SpendAdmin(admin.ModelAdmin):
        list_display = ("campaign", "amount", "timestamp")
        list_filter = ("campaign",)
