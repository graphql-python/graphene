from functools import partial
from ..fields import DjangoConnectionField
from .utils import get_filtering_args_from_filterset, get_filterset_class


class DjangoFilterConnectionField(DjangoConnectionField):

    def __init__(self, type, fields=None, order_by=None,
                 extra_filter_meta=None, filterset_class=None,
                 *args, **kwargs):

        self.order_by = order_by or type._meta.filter_order_by
        self.fields = fields or type._meta.filter_fields
        meta = dict(model=type._meta.model,
                    fields=self.fields,
                    order_by=self.order_by)
        if extra_filter_meta:
            meta.update(extra_filter_meta)
        self.filterset_class = get_filterset_class(filterset_class, **meta)
        self.filtering_args = get_filtering_args_from_filterset(self.filterset_class, type)
        kwargs.setdefault('args', {})
        kwargs['args'].update(self.filtering_args)
        super(DjangoFilterConnectionField, self).__init__(type, *args, **kwargs)

    @staticmethod
    def connection_resolver(resolver, connection, default_manager, filterset_class, filtering_args,
                            root, args, context, info):
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        order = args.get('order_by', None)
        qs = default_manager.get_queryset()
        if order:
            qs = qs.order_by(order)
        qs = filterset_class(data=filter_kwargs, queryset=qs)

        return DjangoConnectionField.connection_resolver(resolver, connection, qs, root, args, context, info)

    def get_resolver(self, parent_resolver):
        return partial(self.connection_resolver, parent_resolver, self.type, self.get_manager(),
                       self.filterset_class, self.filtering_args)
