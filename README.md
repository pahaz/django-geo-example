## Django Development With Docker Compose and Machine

Featuring:

- Docker v1.10.3
- Docker Compose v1.7.1
- Docker Machine v0.6.0
- Python 3.5

Blog post -> https://realpython.com/blog/python/django-development-with-docker-compose-and-machine/

### OS X Instructions

1. Start new machine - `docker-machine create -d virtualbox dev;`
1. Build images - `docker-compose build`
1. Create the database migrations - `docker-compose run web python manage.py migrate`
1. Start services - `docker-compose up -d`
1. Grab IP - `docker-machine ip dev` - and view in your browser
