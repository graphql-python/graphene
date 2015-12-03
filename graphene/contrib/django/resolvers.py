from django.core.exceptions import ImproperlyConfigured

from graphene.contrib.django.filterset import setup_filterset, custom_filterset_factory


class BaseQuerySetConnectionResolver(object):

    def __init__(self, node, on=None):
        self.node = node
        self.model = node._meta.model
        # The name of the field on the model which contains the
        # manager upon which to perform the query. Optional.
        # If omitted the model's default manager will be used.
        self.on = on

    def __call__(self, inst, args, info):
        self.inst = inst
        self.args = args
        self.info = info
        return self.make_query()

    def get_manager(self):
        if self.on:
            return getattr(self.inst, self.on)
        else:
            return self.model._default_manager

    def make_query(self):
        raise NotImplemented()


class SimpleQuerySetConnectionResolver(BaseQuerySetConnectionResolver):
    # Simple querying without using django-filter (ported from previous gist)

    def make_query(self):
        filter_kwargs = self.get_filter_kwargs()
        query = self.get_manager().filter(**filter_kwargs)
        order = self.get_order()
        if order:
            query = query.order_by(order)
        return query

    def get_filter_kwargs(self):
        ignore = ['first', 'last', 'before', 'after', 'order']
        return {k: v for k, v in self.args.items() if k not in ignore}

    def get_order(self):
        return self.args.get('order', None)


class FilterConnectionResolver(BaseQuerySetConnectionResolver):
    # Querying using django-filter

    def __init__(self, node, on=None, filterset_class=None,
                 fields=None, order_by=None, extra_filter_meta=None):
        self.filterset_class = filterset_class
        self.fields = fields
        self.order_by = order_by
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
