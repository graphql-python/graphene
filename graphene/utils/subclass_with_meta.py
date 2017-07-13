import six

from ..pyutils.init_subclass import InitSubclassMeta
from .props import props


class SubclassWithMeta_Meta(InitSubclassMeta):

    def __repr__(cls):
        return cls._meta.name


class SubclassWithMeta(six.with_metaclass(SubclassWithMeta_Meta)):
    """This class improves __init_subclass__ to receive automatically the options from meta"""
    # We will only have the metaclass in Python 2
    def __init_subclass__(cls, **meta_options):
        """This method just terminates the super() chain"""
        _Meta = getattr(cls, "Meta", None)
        _meta_props = {}
        if _Meta:
            _meta_props = props(_Meta)
            delattr(cls, "Meta")
        options = dict(meta_options, **_meta_props)
        super_class = super(cls, cls)
        if hasattr(super_class, '__init_subclass_with_meta__'):
            super_class.__init_subclass_with_meta__(**options)

    @classmethod
    def __init_subclass_with_meta__(cls, **meta_options):
        """This method just terminates the super() chain"""
