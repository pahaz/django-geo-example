import os


def import_django_settings():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project_.settings")
    import django; django.setup()  # noqa
    from django.conf import settings  # noqa
    return settings
