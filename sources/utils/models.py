from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

__author__ = 'pahaz'
user_model_name = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Dated(models.Model):
    """
    Provides created and updated timestamps on models.
    """

    class Meta:
        abstract = True

    created = models.DateTimeField(
        editable=False, auto_now_add=True,
        verbose_name=_('Created')
    )

    updated = models.DateTimeField(
        editable=False, auto_now=True,
        verbose_name=_('Updated')
    )


class Owned(models.Model):
    user = models.ForeignKey(user_model_name, verbose_name=_("User"),
                             related_name="%(class)ss", db_index=True)

    class Meta:
        abstract = True
