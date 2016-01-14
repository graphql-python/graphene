from django.contrib import admin

from cookbook.recipes.models import Recipe, RecipeIngredient

admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
