#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

**`Procfile`** — a separate file called exactly `Procfile` (no extension):
```
web: gunicorn config.wsgi:application
```

**`requirements.txt`** — a separate file:
```
Django>=4.2,<5.0
psycopg2-binary>=2.9.9
Pillow>=10.0.0
django-widget-tweaks>=1.5.0
gunicorn>=21.2.0
whitenoise>=6.6.0
dj-database-url>=2.1.0
python-decouple>=3.8