from __future__ import absolute_import
import django
from django.conf import settings

settings.configure(
    DATABASES={
        'INSTALLED_APPS': [
            'graphql.contrib.django',
        ],
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db_test.sqlite',
        }
    }
)

from django.db import models

class Reporter(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):              # __unicode__ on Python 2
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        app_label = 'graphql'

class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(Reporter, related_name='articles')

    def __str__(self):              # __unicode__ on Python 2
        return self.headline

    class Meta:
        ordering = ('headline',)
        app_label = 'graphql'


django.setup()
