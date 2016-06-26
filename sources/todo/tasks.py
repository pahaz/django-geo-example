from __future__ import absolute_import

from time import sleep

from celery import shared_task

from . import redis


@shared_task
def increase(count, delay=1):
    assert count > 0, 'count > 0'
    assert delay >= 0, 'delay >= 0'
    for _ in range(count):
        counter = redis.incr('counter')
        sleep(delay)
    return counter
