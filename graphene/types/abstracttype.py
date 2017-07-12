class AbstractTypeMeta(type):
    pass


class AbstractType(object):
    def __init_subclass__(cls, *args, **kwargs):
        print("Abstract type is deprecated")
        super(AbstractType, cls).__init_subclass__(*args, **kwargs)
