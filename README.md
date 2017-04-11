## Django Development With Docker Compose

Include:

 - Python + Node.js 
 - Django
 - WebSocket server
 - Celery worker + Celery beat
 - PostgreSQL
 - Redis

Requirements:

 - Docker >= v1.10.3
 - Docker Compose >= v1.7.1
 - Python >= 3.5

### OS X Docker Native Instruction

1. Start Docker Native
1. Build images - `docker-compose build`
1. Create the database migrations - `docker-compose run web python manage.py migrate`
1. Start services - `docker-compose up`
1. View in browser http://127.0.0.1:8000/

### OS X Docker Machine Instruction

1. Start new machine - `docker-machine create -d virtualbox dev;`
1. Build images - `docker-compose build`
1. Create the database migrations - `docker-compose run web python manage.py migrate`
1. Start services - `docker-compose up -d`
1. Grab IP - `docker-machine ip dev` - and view in your browser
