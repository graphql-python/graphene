from ..pyutils.init_subclass import InitSubclassMeta

class AbstractType(object):
    __metaclass__ = InitSubclassMeta

    def __init_subclass__(cls, *args, **kwargs):
        print("Abstract type is deprecated")
        super(AbstractType, cls).__init_subclass__(*args, **kwargs)
