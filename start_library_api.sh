#!/bin/bash
source venv/bin/activate
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi
#gunicorn --bind 0.0.0.0:5000 wsgi
deactivate
