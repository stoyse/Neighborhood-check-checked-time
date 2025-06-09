#!/usr/bin/env bash

source venv/bin/activate

# ins Projektverzeichnis wechseln
cd "$(dirname "$0")"

# Gunicorn starten (4 Worker, Port 8923)
exec gunicorn --workers 4 --bind 0.0.0.0:8923 wsgi:application

