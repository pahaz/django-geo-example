from __future__ import absolute_import
import warnings

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
try:
    from .celery import app as celery_app  # noqa
except (ImportError, TypeError, ValueError):
    warnings.warn("problem with 'from .celery import app as celery_app'")
