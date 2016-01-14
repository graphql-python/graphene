import django_filters

from graphene.contrib.django.tests.models import Article, Pet, Reporter


class ArticleFilter(django_filters.FilterSet):

    class Meta:
        model = Article
        fields = {
            'headline': ['exact', 'icontains'],
            'pub_date': ['gt', 'lt', 'exact'],
            'reporter': ['exact'],
        }
        order_by = True


class ReporterFilter(django_filters.FilterSet):

    class Meta:
        model = Reporter
        fields = ['first_name', 'last_name', 'email', 'pets']
        order_by = False


class PetFilter(django_filters.FilterSet):

    class Meta:
        model = Pet
        fields = ['name']
        order_by = False
