import re
from collections import OrderedDict

from promise import Promise

from ..types import Field, InputObjectType, String
from ..types.mutation import Mutation


class ClientIDMutation(Mutation):

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, output=None, arguments=None, name=None, **options):
        input_class = getattr(cls, 'Input', None)
        name = name or cls.__name__
        base_name = re.sub('Payload$', '', name)

        assert not output, "Can't specify any output"
        assert not arguments, "Can't specify any arguments"

        bases = (InputObjectType, )
        if input_class:
            bases += (input_class, )

        cls.Input = type('{}Input'.format(base_name),
                         bases, {
                             'client_mutation_id': String(name='clientMutationId')
        })

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
    def mutate(cls, root, args, context, info):
        input = args.get('input')

        def on_resolve(payload):
            try:
                payload.client_mutation_id = input.get('clientMutationId')
            except:
                raise Exception(
                    ('Cannot set client_mutation_id in the payload object {}'
                     ).format(repr(payload)))
            return payload

        return Promise.resolve(
            cls.mutate_and_get_payload(input, context, info)).then(on_resolve)
