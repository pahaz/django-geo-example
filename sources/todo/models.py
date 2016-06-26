import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import redis


class Item(models.Model):
    text = models.TextField(blank=False, null=False)
    created = models.DateField(auto_now=True)

    def as_json(self):
        return {
            'created': self.created.strftime('%Y-%m-%d'),
            'text': self.text,
        }


@receiver(post_save, sender=Item, dispatch_uid="publish_item_info")
def publish_item_info(sender, instance, **kwargs):
    redis.publish('messages', json.dumps(instance.as_json()))
