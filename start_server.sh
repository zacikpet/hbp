#! /bin/bash

# Run scheduler in the background
python update_scheduler.py &

# Run WSGI service
gunicorn wsgi:app