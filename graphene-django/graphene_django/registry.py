class Registry(object):
    def __init__(self):
        self._registry = {}
        self._registry_models = {}

    def register(self, cls):
        from .types import DjangoObjectType
        assert issubclass(cls, DjangoObjectType), 'Only DjangoObjectTypes can be registered, received "{}"'.format(cls.__name__)
        assert cls._meta.registry == self, 'Registry for a Model have to match.'
        # assert self.get_type_for_model(cls._meta.model) == cls, 'Multiple DjangoObjectTypes registered for "{}"'.format(cls._meta.model)
        self._registry[cls._meta.model] = cls

    def get_type_for_model(self, model):
        return self._registry.get(model)


registry = None


def get_global_registry():
    global registry
    if not registry:
        registry = Registry()
    return registry


def reset_global_registry():
    global registry
    registry = None
