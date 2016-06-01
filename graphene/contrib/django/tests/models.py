from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

CHOICES = (
    (1, 'this'),
    (2, _('that'))
)


class Pet(models.Model):
    name = models.CharField(max_length=30)


class FilmDetails(models.Model):
    location = models.CharField(max_length=30)
    film = models.OneToOneField('Film', related_name='details')


class Film(models.Model):
    reporters = models.ManyToManyField('Reporter',
                                       related_name='films')


class Reporter(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    pets = models.ManyToManyField('self')
    a_choice = models.CharField(max_length=30, choices=CHOICES)

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
