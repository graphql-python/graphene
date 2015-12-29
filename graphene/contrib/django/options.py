from ...core.classtypes.objecttype import ObjectTypeOptions
from ...relay.types import Node
from ...relay.utils import is_node
from .utils import DJANGO_FILTER_INSTALLED

VALID_ATTRS = ('model', 'only_fields', 'exclude_fields')

if DJANGO_FILTER_INSTALLED:
    VALID_ATTRS += ('filter_fields', 'filter_order_by')


class DjangoOptions(ObjectTypeOptions):

    def __init__(self, *args, **kwargs):
        super(DjangoOptions, self).__init__(*args, **kwargs)
        self.model = None
        self.valid_attrs += VALID_ATTRS
        self.only_fields = None
        self.exclude_fields = []
        self.filter_fields = None
        self.filter_order_by = None

    def contribute_to_class(self, cls, name):
        super(DjangoOptions, self).contribute_to_class(cls, name)
        if is_node(cls):
            self.exclude_fields = list(self.exclude_fields) + ['id']
            self.interfaces.append(Node)
