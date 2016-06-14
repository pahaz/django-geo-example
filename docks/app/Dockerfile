FROM python:3.5

# https://github.com/docker-library/django/blob/819c332058c3638ab8f4fa5b9f70518e9aaf6325/3.4/Dockerfile
RUN apt-get update && apt-get install -y \
        gcc \
        gettext \
        mysql-client libmysqlclient-dev \
        postgresql-client libpq-dev \
        sqlite3 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# http://pillow.readthedocs.io/en/3.1.x/installation.html#building-on-linux
RUN apt-get update && apt-get install -y \
        libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev \
        liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
