from django.contrib import admin

from cookbook.ingredients.models import Category, Ingredient

admin.site.register(Ingredient)
admin.site.register(Category)
