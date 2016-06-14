from django.test import TestCase
from django.utils.crypto import get_random_string

from .models import Item


class TestView(TestCase):
    def test_home_displaying_items(self):
        text = get_random_string()
        Item.objects.create(text=text)
        response = self.client.get('/')
        self.assertContains(response, text)
