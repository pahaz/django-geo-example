from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from random import randint
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils.crypto import get_random_string
from django.test.utils import override_settings
from rest_framework_gis.fields import GeoJsonDict

from geoapi.models import Provider, ServiceArea
from geoapi.serializers import ServiceAreaSerializer


class ModelFactoryMixin:
    def create_user(self, username=None, email=None):
        if not username:
            username = get_random_string()
        if not email:
            email = get_random_string() + "@test.com"
        return get_user_model().objects.create(username=username, email=email)

    def create_provider(self, name=None, email=None, language=None,
                        currency=None):
        if not name:
            name = get_random_string()
        if not email:
            email = get_random_string() + "@test.com"
        user = self.create_user()
        if not language:
            lng = randint(0, len(settings.LANGUAGES))
            language = settings.LANGUAGES[lng][0]
        if not currency:
            currency = Provider._meta.get_field('currency').default  # noqa
        return Provider.objects.create(
            name=name, language=language, email=email, user=user,
            currency=currency)

    def create_service_area(self, poly=None, provider=None, name=None,
                            price=None, user=None):
        if not poly:
            poly = Polygon(
                ((0, 0), (0, 10), (10, 10), (0, 10), (0, 0)),
                ((4, 4), (4, 6), (6, 6), (6, 4), (4, 4)))
        if not provider:
            provider = self.create_provider()
        if not name:
            name = get_random_string()
        if not price:
            price = randint(1, 1000)
        if not user:
            user = provider.user
        return ServiceArea.objects.create(
            poly=poly, provider=provider,
            name=name, price=price, user=user)


class TestModels(ModelFactoryMixin, TestCase):
    def test_create_provider_and_two_equal_areas(self):
        provider = self.create_provider()
        poly = Polygon(
            ((0, 0), (0, 10), (10, 10), (0, 10), (0, 0)),
            ((4, 4), (4, 6), (6, 6), (6, 4), (4, 4)))
        area1 = self.create_service_area(poly, provider=provider)
        area2 = self.create_service_area(poly, provider=provider)

        self.assertEqual(area1.provider, provider)
        self.assertEqual(area2.provider, provider)
        self.assertEqual(area2.poly, area1.poly)


class TestSerializers(ModelFactoryMixin, TestCase):
    def test_serialize_service_area(self):
        name = get_random_string()
        email = name + '@test.com'
        language = 'en'
        currency = 'USD'
        provider = self.create_provider(
            name=name, email=email, language=language, currency=currency)
        area = self.create_service_area(
            name=name, provider=provider, price=48)

        serializer = ServiceAreaSerializer(area)

        self.assertEqual(serializer.data, {
            'geometry': GeoJsonDict([
                ('type', 'Polygon'),
                ('coordinates', (
                    ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0),
                     (0.0, 10.0), (0.0, 0.0)),
                    ((4.0, 4.0), (4.0, 6.0), (6.0, 6.0),
                     (6.0, 4.0), (4.0, 4.0))))]),
            'type': 'Feature',
            'id': area.id,
            'properties': OrderedDict([
                ('name', name),
                ('provider', OrderedDict([
                    ('id', provider.id),
                    ('name', name),
                    ('email', email),
                    ('phone', ''),
                    ('language', language),
                    ('currency', currency)])),
                ('price', '48.00000000')])})
