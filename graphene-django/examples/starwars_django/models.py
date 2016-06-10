from __future__ import absolute_import

from django.db import models


class Character(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Faction(models.Model):
    name = models.CharField(max_length=50)
    hero = models.ForeignKey(Character)

    def __str__(self):
        return self.name


class Ship(models.Model):
    name = models.CharField(max_length=50)
    faction = models.ForeignKey(Faction, related_name='ships')

    def __str__(self):
        return self.name
