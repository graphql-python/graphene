from django.core.exceptions import ImproperlyConfigured

from graphene.contrib.django.filter.filterset import (custom_filterset_factory,
                                                      setup_filterset)
from graphene.contrib.django.resolvers import BaseQuerySetConnectionResolver


class FilterConnectionResolver(BaseQuerySetConnectionResolver):
    # Querying using django-filter

    def __init__(self, node, on=None, filterset_class=None,
                 fields=None, order_by=None, extra_filter_meta=None):
        self.filterset_class = filterset_class
        self.fields = fields or node._meta.filter_fields
        self.order_by = order_by or node._meta.filter_order_by
        self.extra_filter_meta = extra_filter_meta or {}
        self._filterset_class = None
        super(FilterConnectionResolver, self).__init__(node, on)

    def make_query(self):
        filterset_class = self.get_filterset_class()
        filterset = self.get_filterset(filterset_class)
        return filterset.qs

    def get_filterset_class(self):
        """Get the class to be used as the FilterSet"""
        if self._filterset_class:
            return self._filterset_class

        if self.filterset_class:
            # If were given a FilterSet class, then set it up and
            # return it
            self._filterset_class = setup_filterset(self.filterset_class)
        elif self.model:
            # If no filter class was specified then create one given the
            # other information provided
            meta = dict(
                model=self.model,
                fields=self.fields,
                order_by=self.order_by,
            )
            meta.update(self.extra_filter_meta)
            self._filterset_class = custom_filterset_factory(**meta)
        else:
            msg = "Neither 'filterset_class' or 'model' available in '%s'. " \
                  "Either pass in 'filterset_class' or 'model' when " \
                  "initialising, or extend this class and override " \
                  "get_filterset() or get_filterset_class()"
            raise ImproperlyConfigured(msg % self.__class__.__name__)

        return self._filterset_class

    def get_filterset(self, filterset_class):
        """Get an instance of the FilterSet"""
        kwargs = self.get_filterset_kwargs(filterset_class)
        return filterset_class(**kwargs)

    def get_filterset_kwargs(self, filterset_class):
        """Get the kwargs to use when initialising the FilterSet class"""
        kwargs = {
            'data': self.args or None,
            'queryset': self.get_manager()
        }
        return kwargs
