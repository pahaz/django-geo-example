from collections import OrderedDict
from random import randint

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.test import TestCase
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_gis.fields import GeoJsonDict

from utils.testing import AssertionsMixin, ANYTHING
from .models import Provider, ServiceArea
from .serializers import ServiceAreaSerializer

P1 = Polygon([
    [2.109375, 15.29296875],
    [16.083984375, 16.34765625],
    [25.576171875, 0.87890625],
    [-3.69140625, -8.4375],
    [-13.623046875, 12.041015625],
    [-12.568359375, 15.1171875],
    [-11.25, 16.435546875],
    [-8.876953125, 16.611328125],
    [2.109375, 15.29296875]
])

P2 = Polygon([
    [4.5703125, 13.623046875],
    [2.900390625, 9.66796875],
    [5.888671875, 4.658203125],
    [14.58984375, 4.658203125],
    [15.380859375, 14.94140625],
    [6.416015625, 15.64453125],
    [4.5703125, 13.623046875]
])


class ModelFactoryMixin:
    def create_provider(self, name=None, email=None, language=None,
                        currency=None):
        if not name:
            name = get_random_string()
        if not email:
            email = get_random_string() + "@test.com"
        if not language:
            lng = randint(0, len(settings.LANGUAGES) - 1)
            language = settings.LANGUAGES[lng][0]
        if not currency:
            currency = Provider._meta.get_field('currency').default  # noqa
        return Provider.objects.create(
            name=name, language=language, email=email,
            currency=currency)

    def create_service_area(self, poly=None, provider=None, name=None,
                            price=None):
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
        return ServiceArea.objects.create(
            poly=poly, provider=provider,
            name=name, price=price)


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
            'bbox': (0.0, 0.0, 10.0, 10.0),
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


class TestAPI(AssertionsMixin, ModelFactoryMixin, TestCase):
    client_class = APIClient

    def test_api_v1_index(self):
        r = self.client.get('/api/v1/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, OrderedDict([
            ('providers', 'http://testserver/api/v1/providers/'),
            ('service-areas', 'http://testserver/api/v1/service-areas/')]))

    def test_api_v1_providers(self):
        r = self.client.get('/api/v1/providers/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, OrderedDict([
            ('count', 0),
            ('next', None),
            ('previous', None),
            ('results', [])]))

    def test_api_v1_service_areas(self):
        r = self.client.get('/api/v1/service-areas/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, OrderedDict([
            ('type', 'FeatureCollection'),
            ('count', 0),
            ('next', None),
            ('previous', None),
            ('features', [])]))

    def test_api_v1_create_providers(self):
        r = self.client.post('/api/v1/providers/', {'name': 'test'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertContainsSubset(r.data, {
            'id': ANYTHING, 'language': 'en', 'email': '',
            'phone': '', 'name': 'test', 'currency': 'USD'})
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(Provider.objects.get().name, 'test')

    def test_api_v1_create_service_areas(self):
        provider = self.create_provider()
        r = self.client.post('/api/v1/service-areas/', {
            'poly': GeoJsonDict([
                ('type', 'Polygon'),
                ('coordinates', (
                    ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0),
                     (0.0, 10.0), (0.0, 0.0)),
                    ((4.0, 4.0), (4.0, 6.0), (6.0, 6.0),
                     (6.0, 4.0), (4.0, 4.0))))]),
            'provider_id': provider.id,
            'name': 'test'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertContainsSubset(r.data, {
            'bbox': (0.0, 0.0, 10.0, 10.0),
            'id': ANYTHING,
            'type': 'Feature',
            'properties': OrderedDict([
                ('name', 'test'),
                ('provider', OrderedDict([
                    ('id', provider.id), ('name', provider.name),
                    ('email', provider.email), ('phone', provider.phone),
                    ('language', provider.language),
                    ('currency', provider.currency)])),
                ('price', '0.00000000')]),
            'geometry': GeoJsonDict([
                ('type', 'Polygon'),
                ('coordinates', (
                    ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0),
                     (0.0, 10.0), (0.0, 0.0)),
                    ((4.0, 4.0), (4.0, 6.0), (6.0, 6.0),
                     (6.0, 4.0), (4.0, 4.0))))])})
        self.assertEqual(ServiceArea.objects.count(), 1)
        self.assertEqual(ServiceArea.objects.get().name, 'test')

    def test_api_v1_list_providers(self):
        providers = [self.create_provider() for _ in range(20)]
        r = self.client.get('/api/v1/providers/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, OrderedDict([
            ('count', 20),
            ('next', None),
            ('previous', None),
            ('results', [
                OrderedDict([
                    ('id', x.id), ('name', x.name),
                    ('email', x.email), ('phone', x.phone),
                    ('language', x.language), ('currency', x.currency)])
                for x in providers])]))

    def test_api_v1_list_service_areas(self):
        areas = [self.create_service_area() for _ in range(20)]
        r = self.client.get('/api/v1/service-areas/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, OrderedDict([
            ('type', 'FeatureCollection'),
            ('count', 20),
            ('next', None), ('previous', None),
            ('features', [
                OrderedDict([
                    ('id', x.id),
                    ('type', 'Feature'),
                    ('geometry', GeoJsonDict([
                        ('type', 'Polygon'),
                        ('coordinates', (
                            ((0.0, 0.0), (0.0, 10.0), (10.0, 10.0),
                             (0.0, 10.0), (0.0, 0.0)),
                            ((4.0, 4.0), (4.0, 6.0), (6.0, 6.0),
                             (6.0, 4.0), (4.0, 4.0))))])),
                    ('bbox', (0.0, 0.0, 10.0, 10.0)),
                    ('properties', OrderedDict([
                        ('name', x.name),
                        ('provider', OrderedDict([
                            ('id', x.provider.id), ('name', x.provider.name),
                            ('email', x.provider.email),
                            ('phone', x.provider.phone),
                            ('language', x.provider.language),
                            ('currency', x.provider.currency)])),
                        ('price', format(x.price.amount, '.8f'))]))])
                for x in areas
            ])]))

    def test_api_v1_service_areas_filter_by_provider_id(self):
        s1 = self.create_service_area(P1)
        s2 = self.create_service_area(P2)
        [self.create_service_area(provider=s2.provider) for _ in range(10)]

        filters = 'provider_id=' + str(s1.provider_id)
        r = self.client.get('/api/v1/service-areas/?' + filters)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['features']), 1)

        filters = 'provider_id=' + str(s2.provider_id)
        r = self.client.get('/api/v1/service-areas/?' + filters)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['features']), 11)

    def test_api_v1_service_areas_filter_by_poly_contains(self):
        s1 = self.create_service_area(P1)
        s2 = self.create_service_area(P2)
        [self.create_service_area() for _ in range(10)]

        filters = 'poly__contains={"type":"Point","coordinates":' \
                  '[9.26436996459961,10.564178042345375]}'
        r = self.client.get('/api/v1/service-areas/?' + filters)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['features']), 2)
        self.assertEqual(set([x['id'] for x in r.data['features']]), {
            s1.id, s2.id
        })

    def test_api_v1_areas_filter_by_poly_contains_and_provider_id(self):
        s1 = self.create_service_area(P1)
        self.create_service_area(P2)
        [self.create_service_area() for _ in range(10)]

        filters = 'poly__contains={"type":"Point","coordinates":' \
                  '[9.26436996459961,10.564178042345375]}'
        filters += '&provider_id=' + str(s1.provider_id)
        r = self.client.get('/api/v1/service-areas/?' + filters)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['features']), 1)
        self.assertEqual(set([x['id'] for x in r.data['features']]), {s1.id})

    def test_api_v1_areas_filter_format_error(self):
        [self.create_service_area() for _ in range(10)]

        filters = 'poly__contains={"type":"Point","coordinates":' \
                  '[9.26436996459961 10.564178042345375]}'
        r = self.client.get('/api/v1/service-areas/?' + filters)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data, [
            "invalid poly__contains: Expecting ',' delimiter: "
            "line 1 column 49 (char 48)"])
