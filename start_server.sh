#! /bin/bash

# Run scheduler in the background
python update_scheduler.py &

# Run WSGI service
gunicorn --bind 0.0.0.0:8080 wsgi:app