#!/usr/bin/env bash

echo "PWD=$PWD"
python manage.py collectstatic -l --noinput
