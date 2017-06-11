from django.conf import settings
from django.db import models


class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 7)
        kwargs.setdefault('choices', settings.LANGUAGES)
        super(LanguageField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"
