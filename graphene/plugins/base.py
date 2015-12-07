class Plugin(object):

    def contribute_to_schema(self, schema):
        self.schema = schema

    def transform_type(self, objecttype):
        return objecttype
