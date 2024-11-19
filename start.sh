#!/bin/bash

python sicame/manage.py makemigrations --no-input
python sicame/manage.py migrate --no-input
python sicame/manage.py runserver 0.0.0.0:8000