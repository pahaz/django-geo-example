from unittest.mock import patch

from django.test import TestCase
from django.utils.crypto import get_random_string
from django.test.utils import override_settings

from . import redis
from .models import Item
from .tasks import increase


class TestViews(TestCase):
    def test_home_displaying_items(self):
        text = get_random_string()
        Item.objects.create(text=text)
        response = self.client.get('/')
        self.assertContains(response, text)

    @patch('todo.views.increase')
    def test_incr(self, mock_increase):
        self.client.get('/incr?value=33')
        mock_increase.delay.assert_called_with(33)


class TestTasks(TestCase):
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_incr_increase_redis_counter(self):
        value = int(redis.get('counter'))
        increase.delay(3, delay=0)
        self.assertEqual(int(redis.get('counter')), value + 3)
