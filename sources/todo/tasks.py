from __future__ import absolute_import

from celery import shared_task

from . import redis


@shared_task
def increase(count):
    assert count > 0, 'count > 0'
    for _ in range(count):
        counter = redis.incr('counter')
    return counter
