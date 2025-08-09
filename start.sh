#!/bin/bash

#wait for DB
sleep 10

#migrate
python manage.py migrate

#start server
exec gunicorn ecommerce_backend.wsgi:application --bind 0.0.0.0:8000


