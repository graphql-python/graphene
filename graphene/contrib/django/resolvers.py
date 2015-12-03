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
