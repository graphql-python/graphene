from django.contrib import admin

from cookbook.ingredients.models import Ingredient, Category

admin.site.register(Ingredient)
admin.site.register(Category)
