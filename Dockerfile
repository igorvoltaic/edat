FROM python:3.8.6-slim

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt
RUN echo "SECRET_KEY=$(python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())')" > .env
