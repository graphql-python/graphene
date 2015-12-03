import six
from django.db import models
from django_filters import Filter
from django_filters.filterset import FilterSetMetaclass, FilterSet
from graphql_relay.node.node import from_global_id

from graphene.contrib.django.forms import GlobalIDFormField


class GlobalIDFilter(Filter):
    field_class = GlobalIDFormField

    def filter(self, qs, value):
        gid = from_global_id(value)
        return super(GlobalIDFilter, self).filter(qs, gid.id)


GRAPHENE_FILTER_SET_OVERRIDES = {
    models.AutoField: {
        'filter_class': GlobalIDFilter,
    },
    models.OneToOneField: {
        'filter_class': GlobalIDFilter,
    },
    models.ForeignKey: {
        'filter_class': GlobalIDFilter,
    }
    # TODO: Support ManyToManyFields. GlobalIDFilterList?
}


class GrapheneFilterSetMetaclass(FilterSetMetaclass):
    def __new__(cls, name, bases, attrs):
        new_class = super(GrapheneFilterSetMetaclass, cls).__new__(cls, name, bases, attrs)
        # Customise the filter_overrides for Graphene
        for k, v in GRAPHENE_FILTER_SET_OVERRIDES.items():
            new_class.filter_overrides.setdefault(k, v)
        return new_class


class GrapheneFilterSet(six.with_metaclass(GrapheneFilterSetMetaclass, FilterSet)):
    """ Base class for FilterSets used by Graphene

    You shouldn't usually need to use this class. The
    DjangoFilterConnectionField will wrap FilterSets with this class as
    necessary
    """
    pass


def setup_filterset(filterset_class):
    """ Wrap a provided filterset in Graphene-specific functionality
    """
    return type(
        'Graphene{}'.format(filterset_class.__name__),
        (six.with_metaclass(GrapheneFilterSetMetaclass, filterset_class),),
        {},
    )


def custom_filterset_factory(model, filterset_base_class=GrapheneFilterSet,
                             **meta):
    """ Create a filterset for the given model using the provided meta data
    """
    meta.update({
        'model': model,
    })
    meta_class = type(str('Meta'), (object,), meta)
    filterset = type(str('%sFilterSet' % model._meta.object_name),
                     (filterset_base_class,), {'Meta': meta_class})
    return filterset
