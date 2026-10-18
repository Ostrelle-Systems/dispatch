# dispatch

Job scheduling and SLA monitoring service for the Ostrelle Systems logistics platform. Tracks scheduled checks against carrier and route SLAs, and fires alerts when jobs miss their expected windows.

**Stack:** Python, Django

## Prerequisites

- Python 3.12+
- PostgreSQL

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cp hc/local_settings.py.example hc/local_settings.py   # set DB creds + secrets
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Background jobs

SLA checks and notification sending run as management commands, typically under a process supervisor:

```bash
python manage.py sendalerts
python manage.py sendreports
```

## Testing

```bash
python manage.py test
mypy hc
```

## Related services

- `shipment-tracker` — event source for SLA evaluation
- `carrier-portal` — surfaces SLA/alert status to customers
