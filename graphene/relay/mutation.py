import re
from collections import OrderedDict

from promise import Promise, is_thenable

from ..types import Field, InputObjectType, String, Context, ResolveInfo
from ..types.mutation import Mutation
from ..utils.annotate import annotate


class ClientIDMutation(Mutation):

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, output=None, input_fields=None, arguments=None, name=None, abstract=False, **options):
        if abstract:
            return

        input_class = getattr(cls, 'Input', None)
        name = name or cls.__name__
        base_name = re.sub('Payload$', '', name)

        assert not output, "Can't specify any output"
        assert not arguments, "Can't specify any arguments"

        bases = (InputObjectType, )
        if input_class:
            bases += (input_class, )
        
        if not input_fields:
            input_fields = {}

        cls.Input = type(
            '{}Input'.format(base_name),
            bases,
            OrderedDict(input_fields, client_mutation_id=String(name='clientMutationId'))
        )

        arguments = OrderedDict(
            input=cls.Input(required=True)
            # 'client_mutation_id': String(name='clientMutationId')
        )
        mutate_and_get_payload = getattr(cls, 'mutate_and_get_payload', None)
        if cls.mutate and cls.mutate.__func__ == ClientIDMutation.mutate.__func__:
            assert mutate_and_get_payload, (
                "{name}.mutate_and_get_payload method is required"
                " in a ClientIDMutation.").format(name=name)

        if not name:
            name = '{}Payload'.format(base_name)

        super(ClientIDMutation, cls).__init_subclass_with_meta__(output=None, arguments=arguments, name=name, **options)
        cls._meta.fields['client_mutation_id'] = (
            Field(String, name='clientMutationId')
        )

    @classmethod
    @annotate(context=Context, info=ResolveInfo)
    def mutate(cls, root, input, context, info):
        def on_resolve(payload):
            try:
                payload.client_mutation_id = input.get('clientMutationId')
            except:
                raise Exception(
                    ('Cannot set client_mutation_id in the payload object {}'
                     ).format(repr(payload)))
            return payload

        result = cls.mutate_and_get_payload(input, context, info)
        if is_thenable(result):
            return Promise.resolve(result).then(on_resolve)

        return on_resolve(result)
