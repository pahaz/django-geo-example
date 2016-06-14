from django.db import models


class Item(models.Model):
    text = models.TextField(blank=False, null=False)
    created = models.DateField(auto_now=True)
