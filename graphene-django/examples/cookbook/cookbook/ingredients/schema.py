from cookbook.ingredients.models import Category, Ingredient
from graphene import ObjectType, relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoNode, DjangoObjectType


# Graphene will automatically map the User model's fields onto the UserType.
# This is configured in the UserType's Meta class (as you can see below)
class CategoryNode(DjangoNode, DjangoObjectType):

    class Meta:
        model = Category
        filter_fields = ['name', 'ingredients']
        filter_order_by = ['name']


class IngredientNode(DjangoNode, DjangoObjectType):

    class Meta:
        model = Ingredient
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'category': ['exact'],
            'category__name': ['exact'],
        }
        filter_order_by = ['name', 'category__name']


class Query(ObjectType):
    category = relay.NodeField(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    ingredient = relay.NodeField(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)
