from graphene.relay import ConnectionField
from graphene.contrib.django.filter.resolvers import FilterConnectionResolver
from graphene.contrib.django.utils import get_filtering_args_from_filterset


class DjangoFilterConnectionField(ConnectionField):

    def __init__(self, type, on=None, fields=None, order_by=None,
                 extra_filter_meta=None, filterset_class=None, resolver=None,
                 *args, **kwargs):

        if not resolver:
            resolver = FilterConnectionResolver(
                node=type,
                on=on,
                filterset_class=filterset_class,
                fields=fields,
                order_by=order_by,
                extra_filter_meta=extra_filter_meta,
            )

        filtering_args = get_filtering_args_from_filterset(resolver.get_filterset_class(), type)
        kwargs.setdefault('args', {})
        kwargs['args'].update(**filtering_args)
        super(DjangoFilterConnectionField, self).__init__(type, resolver, *args, **kwargs)
