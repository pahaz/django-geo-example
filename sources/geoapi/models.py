from django.contrib.gis.db import models
from django.core.validators import MinValueValidator

from djmoney.models.fields import MoneyField, MoneyPatched, CurrencyField
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
    email = models.EmailField()
    phone = PhoneNumberField()
    language = LanguageField()
    currency = CurrencyField()

    def __str__(self):
        return self.name


class ServiceArea(Dated):
    provider = models.ForeignKey(Provider)
    name = models.CharField(max_length=255)
    poly = models.PolygonField()
    price = MoneyField(
        max_digits=19, decimal_places=8,
        validators=[MinValueValidator(MoneyPatched(100, 'GBP'))])

    def __str__(self):
        return self.name
