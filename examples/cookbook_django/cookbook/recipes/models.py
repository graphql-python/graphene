from django.db import models

from cookbook.ingredients.models import Ingredient


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    instructions = models.TextField()


class RecipeIngredient(models.Model):
    recipes = models.ForeignKey(Recipe, related_name='amounts')
    ingredient = models.ForeignKey(Ingredient, related_name='used_by')
    amount = models.FloatField()
    unit = models.CharField(max_length=20, choices=(
        ('kg', 'Kilograms'),
        ('l', 'Litres'),
        ('', 'Units'),
    ))
