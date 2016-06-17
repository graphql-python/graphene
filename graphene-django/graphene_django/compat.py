from django.db import models


class MissingType(object):
    pass

try:
    UUIDField = models.UUIDField
except AttributeError:
    # Improved compatibility for Django 1.6
    UUIDField = MissingType

try:
    from django.db.models.related import RelatedObject
except:
    # Improved compatibility for Django 1.6
    RelatedObject = MissingType


try:
    # Postgres fields are only available in Django 1.8+
    from django.contrib.postgres.fields import ArrayField, HStoreField, JSONField, RangeField
except ImportError:
    ArrayField, HStoreField, JSONField, RangeField = (MissingType, ) * 4
