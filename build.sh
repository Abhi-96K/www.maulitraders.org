#!/usr/bin/env bash
python manage.py collectstatic --no-input
Django>=5.2,<6.0
gunicorn
whitenoise
