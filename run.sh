#!/bin/sh
source ./env.sh
gunicorn --access-logfile - --error-logfile - -b 0.0.0.0:8000 --reload --worker-class eventlet decide_politics.flask:app
