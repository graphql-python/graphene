
class InitSubclassMeta(type):
    """Metaclass that implements PEP 487 protocol"""
    def __new__(cls, name, bases, ns):
        __init_subclass__ = ns.pop('__init_subclass__', None)
        if __init_subclass__:
            __init_subclass__ = classmethod(__init_subclass__)
            ns['__init_subclass__'] = __init_subclass__
        return type.__new__(cls, name, bases, ns)

    def __init__(cls, name, bases, ns):
        super(InitSubclassMeta, cls).__init__(name, bases, ns)
        super_class = super(cls, cls)
        if hasattr(super_class, '__init_subclass__'):
            super_class.__init_subclass__.__func__(cls)
