#!/bin/bash

python sicame/manage.py makemigrations
python sicame/manage.py migrate
python sicame/manage.py runserver 0.0.0.0:8000