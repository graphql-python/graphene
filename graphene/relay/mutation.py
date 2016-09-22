import re
from functools import partial

import six

from promise import Promise

from ..types import AbstractType, Argument, Field, InputObjectType, String
from ..types.objecttype import ObjectType, ObjectTypeMeta
from ..utils.is_base_type import is_base_type
from ..utils.props import props


class ClientIDMutationMeta(ObjectTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # Mutation
        if not is_base_type(bases, ClientIDMutationMeta):
            return type.__new__(cls, name, bases, attrs)

        input_class = attrs.pop('Input', None)
        base_name = re.sub('Payload$', '', name)
        if 'client_mutation_id' not in attrs:
            attrs['client_mutation_id'] = String(name='clientMutationId')
        cls = ObjectTypeMeta.__new__(cls, '{}Payload'.format(base_name), bases, attrs)
        mutate_and_get_payload = getattr(cls, 'mutate_and_get_payload', None)
        if cls.mutate and cls.mutate.__func__ == ClientIDMutation.mutate.__func__:
            assert mutate_and_get_payload, (
                "{}.mutate_and_get_payload method is required"
                " in a ClientIDMutation."
            ).format(name)
        input_attrs = {}
        bases = ()
        if not input_class:
            input_attrs = {}
        elif not issubclass(input_class, AbstractType):
            input_attrs = props(input_class)
        else:
            bases += (input_class, )
        input_attrs['client_mutation_id'] = String(name='clientMutationId')
        cls.Input = type('{}Input'.format(base_name), bases + (InputObjectType,), input_attrs)
        cls.Field = partial(Field, cls, resolver=cls.mutate, input=Argument(cls.Input, required=True))
        return cls


class ClientIDMutation(six.with_metaclass(ClientIDMutationMeta, ObjectType)):

    @classmethod
    def mutate(cls, root, args, context, info):
        input = args.get('input')

        def on_resolve(payload):
            try:
                payload.client_mutation_id = input.get('clientMutationId')
            except:
                raise Exception((
                    'Cannot set client_mutation_id in the payload object {}'
                ).format(repr(payload)))
            return payload

        return Promise.resolve(
            cls.mutate_and_get_payload(input, context, info)
        ).then(on_resolve)
