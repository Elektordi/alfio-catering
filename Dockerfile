FROM python:3.8-slim

COPY requirements.txt /etc/
RUN pip install -r /etc/requirements.txt

COPY src /srv/app

EXPOSE 8000
CMD ["/srv/app/runserver.sh"]

