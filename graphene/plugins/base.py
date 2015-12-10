from functools import partial, reduce


class Plugin(object):

    def contribute_to_schema(self, schema):
        self.schema = schema


def apply_function(a, b):
    return b(a)


class PluginManager(object):

    PLUGIN_FUNCTIONS = ('get_default_namedtype_name', )

    def __init__(self, schema, plugins=[]):
        self.schema = schema
        self.plugins = []
        for plugin in plugins:
            self.add_plugin(plugin)

    def add_plugin(self, plugin):
        if hasattr(plugin, 'contribute_to_schema'):
            plugin.contribute_to_schema(self.schema)
        self.plugins.append(plugin)

    def get_plugin_functions(self, function):
        for plugin in self.plugins:
            if not hasattr(plugin, function):
                continue
            yield getattr(plugin, function)

    def __getattr__(self, name):
        functions = self.get_plugin_functions(name)
        return partial(reduce, apply_function, functions)

    def __contains__(self, name):
        return name in self.PLUGIN_FUNCTIONS
