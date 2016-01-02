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
        kwargs['args'].update(**self.filtering_args)
        super(DjangoFilterConnectionField, self).__init__(type, *args, **kwargs)

    def get_queryset(self, qs, args, info):
        filterset_class = self.filterset_class
        filter_kwargs = self.get_filter_kwargs(args)
        order = self.get_order(args)
        if order:
            qs = qs.order_by(order)
        return filterset_class(data=filter_kwargs, queryset=qs)

    def get_filter_kwargs(self, args):
        return {k: v for k, v in args.items() if k in self.filtering_args}

    def get_order(self, args):
        return args.get('order_by', None)
