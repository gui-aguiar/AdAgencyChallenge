# Pseudo-code and Data Model – Django + Celery Budget Management System

This document contains the high-level pseudo-code and data model design used to implement the budget management backend system.

---

## Entities

### Brand
- `name`: Name of the brand.
- `daily_budget`: Float, in currency units.
- `monthly_budget`: Float, in currency units.

### Campaign
- `brand`: FK to Brand.
- `name`: Campaign name.
- `is_active`: Boolean. Automatically toggled based on budgets.
- `total_spend_today`: Cached daily spend.
- `total_spend_month`: Cached monthly spend.
- `cost_per_execution`: Base cost for a campaign execution.

### Schedule
- `campaign`: FK to Campaign.
- `day_of_week`: 0 = Monday, ..., 6 = Sunday.
- `start_time`: TimeField aligned to 15-minute intervals.
- `end_time`: TimeField aligned to 15-minute intervals.
- `last_execution`: datetime of last valid execution.

**Validation Rules:**
- `end_time` must be greater than `start_time`
- Duration between `start_time` and `end_time` must be a multiple of 1 hour
- `start_time` and `end_time` must align with 15-minute intervals
- Each Schedule is tied to a weekday (0–6) — not specific dates — for simplicity

### Spend
- `campaign`: FK to Campaign.
- `amount`: Float, value spent during the execution.
- `timestamp`: datetime of the execution.

---

## Business Logic


### Spend Tracking

```
Every 5 minutes

For each active campaign:
    For each schedule attached to that campaign:
        If today matches the schedule's day_of_week:
            If current time is between start_time and end_time:
                If campaign has not executed this schedule today:
                    If daily and monthly spend are within limits:
                        Create a Spend record
                        Update campaign's cached spend totals
                        Mark last_execution
                    Else:
                        Deactivate campaign (is_active = False)
```

---

### Budget Enforcement

```
Triggered during execution logic:
  If campaign exceeds either daily or monthly budget:
    → Set is_active = False
```

---

### Dayparting Check

```
A campaign can only execute during a time window defined by a Schedule
AND only once per schedule per day.

Execution is skipped if current time does not fall within a valid Schedule.
```

---

## Reset Logic

### Daily Reset

```
Every day at 00:00:

For each campaign:
    Reset total_spend_today to 0
    
    If monthly budget is still within limits:
        Reactivate campaign (is_active = True)
```

### Monthly Reset

```
Every month on day 1 at 00:00:

For each campaign:
    Reset total_spend_month to 0
    Reset total_spend_today to 0
    Reactivate campaign (is_active = True)
```

---

## Additional Notes

- Only one execution is allowed per campaign per schedule per day.
- Two schedules for the same campaign with slightly different start times (e.g., 10:00 and 10:01) are considered distinct and both will trigger execution.
- Cost per execution is fixed per campaign, not per click or per impression.
- The use of weekday-based scheduling avoids complexity with calendar dates or exceptions.

---
