from functools import partial

import six

from graphql_relay import mutation_with_client_mutation_id

from ..types.field import Field, InputField
from ..types.inputobjecttype import InputObjectType
from ..types.mutation import Mutation, MutationMeta
from ..types.objecttype import ObjectType
from ..types.options import Options
from ..utils.copy_fields import copy_fields
from ..utils.get_fields import get_fields
from ..utils.is_base_type import is_base_type
from ..utils.props import props


class ClientIDMutationMeta(MutationMeta):

    def __new__(cls, name, bases, attrs):
        super_new = type.__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, ClientIDMutationMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
        )

        input_class = attrs.pop('Input', None)

        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        input_fields = props(input_class) if input_class else {}
        input_local_fields = copy_fields(InputField, get_fields(InputObjectType, input_fields, ()))
        output_fields = copy_fields(Field, get_fields(ObjectType, attrs, bases))

        mutate_and_get_payload = getattr(cls, 'mutate_and_get_payload', None)
        assert mutate_and_get_payload, (
            "{}.mutate_and_get_payload method is required"
            " in a ClientIDMutation ObjectType.".format(cls.__name__)
        )

        field = mutation_with_client_mutation_id(
            name=options.name or cls.__name__,
            input_fields=input_local_fields,
            output_fields=output_fields,
            mutate_and_get_payload=cls.mutate_and_get_payload,
        )
        options.graphql_type = field.type
        options.get_fields = lambda: output_fields

        cls.Field = partial(Field.copy_and_extend, field, type=field.type, _creation_counter=None)
        return cls


class ClientIDMutation(six.with_metaclass(ClientIDMutationMeta, Mutation)):
    pass
