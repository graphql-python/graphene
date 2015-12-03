import django_filters

from .models import Article, Pet


class ArticleFilter(django_filters.FilterSet):

    class Meta:
        model = Article
        fields = {
            'headline': ['exact', 'icontains'],
            'pub_date': ['gt', 'lt', 'exact'],
            'reporter': ['exact'],
        }
        order_by = True


class PetFilter(django_filters.FilterSet):

    class Meta:
        model = Pet
        fields = ['name']
        order_by = False
