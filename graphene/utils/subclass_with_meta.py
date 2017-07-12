from .props import props
from ..pyutils.init_subclass import InitSubclassMeta


class SubclassWithMeta(object):
    """This class improves __init_subclass__ to receive automatically the options from meta"""
    # We will only have the metaclass in Python 2
    __metaclass__ = InitSubclassMeta

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
