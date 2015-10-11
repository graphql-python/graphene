from graphene.utils import cached_property
from collections import OrderedDict

DEFAULT_NAMES = ('description', 'name', 'interface',
                 'type_name', 'interfaces', 'proxy')


class Options(object):

    def __init__(self, meta=None):
        self.meta = meta
        self.local_fields = []
        self.interface = False
        self.proxy = False
        self.interfaces = []
        self.parents = []
        self.valid_attrs = DEFAULT_NAMES

    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.parent = cls
        # First, construct the default values for these options.
        self.object_name = cls.__name__
        self.type_name = self.object_name

        self.description = cls.__doc__
        # Store the original user-defined values for each option,
        # for use when serializing the model definition
        self.original_attrs = {}

        # Next, apply any overridden values from 'class Meta'.
        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                # Ignore any private attributes that Django doesn't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in self.valid_attrs:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                    self.original_attrs[attr_name] = getattr(self, attr_name)
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))
                    self.original_attrs[attr_name] = getattr(self, attr_name)

            del self.valid_attrs

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError(
                    "'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs.keys()))
        else:
            self.proxy = False

        if self.interfaces != [] and self.interface:
            raise Exception("A interface cannot inherit from interfaces")

        del self.meta

    def add_field(self, field):
        self.local_fields.append(field)

    @cached_property
    def fields(self):
        fields = []
        for parent in self.parents:
            fields.extend(parent._meta.fields)
        return sorted(self.local_fields + fields)

    @cached_property
    def fields_map(self):
        return OrderedDict([(f.field_name, f) for f in self.fields])
