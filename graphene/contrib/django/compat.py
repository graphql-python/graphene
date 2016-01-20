from django.db import models

try:
    UUIDField = models.UUIDField
except AttributeError:
    # Improved compatibility for Django 1.6
    class UUIDField(object):
        pass

try:
    from django.db.models.related import RelatedObject
except:
    # Improved compatibility for Django 1.6
    class RelatedObject(object):
        pass
