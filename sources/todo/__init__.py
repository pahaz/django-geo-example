from django.conf import settings
from redis import Redis

redis = Redis(host=settings.REDIS_HOST, port=6379)
