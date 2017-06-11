from django.contrib.gis.db import models
from djmoney.models.fields import MoneyField, CurrencyField
from phonenumber_field.modelfields import PhoneNumberField

from utils.fields import LanguageField
from utils.models import Dated


class Provider(Dated):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = PhoneNumberField(blank=True)
    language = LanguageField(default='en')
    currency = CurrencyField(default='USD')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class ServiceArea(Dated):
    provider = models.ForeignKey(Provider)
    name = models.CharField(max_length=255)
    poly = models.PolygonField()
    price = MoneyField(max_digits=19, decimal_places=8)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']