#!/usr/bin/env bash

echo "PWD=$PWD"
STATIC_ROOT=/static python manage.py collectstatic --noinput
