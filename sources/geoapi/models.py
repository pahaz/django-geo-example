from django.contrib.gis.db import models
from djmoney.models.fields import MoneyField, CurrencyField
from phonenumber_field.modelfields import PhoneNumberField

from utils.fields import LanguageField
from utils.models import Dated


class WorldBorder(models.Model):
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    def __str__(self):
        return self.name


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