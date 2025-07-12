from django.db import models
from datetime import time, timedelta, datetime
from django.core.exceptions import ValidationError


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return self.name

class Campaign(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    total_spend_today = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_spend_month = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_per_execution = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.name} ({self.brand.name})"

class Schedule(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField()  # 0 = Monday, 6 = Sunday
    start_time = models.TimeField()
    end_time = models.TimeField()
    last_execution = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.campaign.name} - {self.day_of_week} [{self.start_time}–{self.end_time}]"

    def clean(self) -> None:        
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

        duration = (
            timedelta(
                hours=self.end_time.hour,
                minutes=self.end_time.minute
            ) - timedelta(
                hours=self.start_time.hour,
                minutes=self.start_time.minute
            )
        )

        if duration.total_seconds() % 3600 != 0:
            raise ValidationError("Schedule duration must be a multiple of 1 hour.")

        for t in [self.start_time, self.end_time]:
            if t.minute % 15 != 0:
                raise ValidationError("Start and end time must align with 15-minute intervals.")

class Spend(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='spends')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.campaign.name} - R${self.amount} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
