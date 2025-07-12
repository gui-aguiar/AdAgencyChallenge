# AdAgencyChallenge

## Overview

This project implements a backend system for managing advertising campaign budgets using Django and Celery.

Each **Brand** has a daily and monthly budget. Campaigns are automatically activated/deactivated based on spend limits and dayparting schedules.

### Core Features

- Track and persist daily/monthly spend.
- Enforce budget constraints per brand.
- Enable/disable campaigns based on time-of-day rules (dayparting).
- Execute campaigns during scheduled time windows, once per window.
- Automatically reset daily and monthly spend counters via Celery.

---

## Design Decisions

- **Weekly-based Scheduling**: Schedules are defined by day of the week (e.g., Mondays 14:00–16:00), instead of exact calendar dates. This simplifies the model and avoids dealing with date-specific complexities (e.g., holidays, month lengths). A more advanced version could include interval-based or date-based schedules.

- **Fixed Execution Cost**: Each campaign defines a `cost_per_execution` (float) representing a fixed cost for each valid run. This avoids common complexities found in ad platforms such as CPC (Cost-Per-Click), CPM (Cost-Per-Mille), or dynamic pricing models.

- **Single Execution Per Time Window**: Even if multiple schedule entries exist for the same campaign at the same time window (e.g., duplicated entries for the same Monday 10–11 AM), the campaign is only executed once per valid window. However, if two schedules differ by even a minute, both are treated independently and executed.

- **Time Window Constraints**: All schedules must:
  - Start and end on 15-minute aligned intervals (e.g., 10:00, 10:15, 10:30).
  - Have a duration that is a multiple of 1 hour (e.g., 1h, 2h, 3h).
  
  This ensures that campaign executions can be efficiently verified at 5-minute intervals without dealing with granular or overlapping conditions. More granular schedules (e.g., every 5 minutes) were avoided to simplify validation and reduce execution frequency.

- **Execution Engine Simplicity**: The execution task runs every 5 minutes and checks only the current time window. This design avoids the need for complex tracking across sliding windows or queues.

---


## Pseudo-code

For a high-level pseudo-code overview of the system's entities and business logic, see [PSEUDOCODE.md](./PSEUDOCODE.md)

---

## Celery Tasks

- `check_and_execute_campaigns`: runs every 5 minutes, checks schedules and executes campaigns.
- `reset_daily_spend`: runs daily at 00:00.
- `reset_monthly_spend`: runs on the 1st of each month at 00:00.
- Campaigns are executed **once per schedule per day**.

---

## Static Typing

All code is statically typed using Python type hints. The project uses:

- `mypy`
- `django-stubs`

Configuration file: `mypy.ini`

The code passes type checks with **zero errors**.

---

## Tests 

A test suite is provided to demonstrate unit testing of model business logic (e.g., schedule validation rules) and integration testing of Celery task behavior. These tests serve as a foundation for expanding full coverage and were implemented using `pytest` and `pytest-django`.

--

## Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/gui-aguiar/AdAgencyChallenge.git
cd AdAgencyChallenge
```

### 2. Build and run the project with Docker

```
docker-compose up --build
```

- This will start:
  - Django app (on `http://localhost:8000`)
  - RabbitMQ (Celery broker)
  - Celery worker
  - Celery beat (scheduler)

### 3. Migrations

Migrations are automatically applied when the containers start.

If needed, you can re-run them manually with:

```
docker-compose exec web python manage.py migrate
```

### 4. (Optional) Create superuser

```
docker-compose exec web python manage.py createsuperuser
```

Then access Django Admin at: `http://localhost:8000/admin/`

---

## Tests

Run all tests using:

```
docker-compose exec web pytest
```

Includes:
- Model validations
- Schedule rules
- Celery task behavior

---

## Assumptions and Simplifications

- The project assumes a backend-only interface via Django Admin (no frontend or public API).
- Database used is SQLite for simplicity; can be replaced with Postgres.
- Each campaign is executed only once per valid schedule window per day.
- Campaign activation/deactivation is handled automatically, without manual overrides.
- `cost_per_execution` is defined per campaign and constant; advanced pricing models (CPC, CPM) were not implemented.

---

## Author

Guilherme Aguiar
