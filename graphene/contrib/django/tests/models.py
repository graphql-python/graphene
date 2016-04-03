from __future__ import absolute_import

from django.db import models


class Pet(models.Model):
    name = models.CharField(max_length=30)


class Film(models.Model):
    reporters = models.ManyToManyField('Reporter',
                                       related_name='films')


class Reporter(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    pets = models.ManyToManyField('self')

    def __str__(self):              # __unicode__ on Python 2
        return "%s %s" % (self.first_name, self.last_name)


class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(Reporter, related_name='articles')
    lang = models.CharField(max_length=2, help_text='Language', choices=[
        ('es', 'Spanish'),
        ('en', 'English')
    ], default='es')
    importance = models.IntegerField('Importance', null=True, blank=True,
                                     choices=[(1, u'Very important'), (2, u'Not as important')])

    def __str__(self):              # __unicode__ on Python 2
        return self.headline

    class Meta:
        ordering = ('headline',)
