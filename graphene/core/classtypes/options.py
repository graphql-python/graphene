class Options(object):

    def __init__(self, meta=None, **defaults):
        self.meta = meta
        self.abstract = False
        for name, value in defaults.items():
            setattr(self, name, value)
        self.valid_attrs = list(defaults.keys()) + ['type_name', 'description', 'abstract']

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
                    "'class Meta' got invalid attribute(s): %s" %
                    ','.join(
                        meta_attrs.keys()))

        del self.meta
