#!/bin/bash

cd /srv/app
./manage.py migrate
./manage.py collectstatic -c
exec gunicorn core.wsgi:application -w 5 --timeout 300 --worker-class gevent --max-requests-jitter 50 --max-requests 500 --access-logfile - --user nobody -b :8000

