from functools import partial

from ..inputfield import InputField
from ..inputobjecttype import InputObjectType
from ..scalars import String, Boolean
from ..objecttype import ObjectType
from ..structures import NonNull
from ..schema import Schema
from ..mutation import Mutation
from .utils import MyLazyType


def test_inputfield_required():
    MyType = object()
    field = InputField(MyType, required=True)
    assert isinstance(field.type, NonNull)
    assert field.type.of_type == MyType


def test_inputfield_with_lazy_type():
    MyType = object()
    field = InputField(lambda: MyType)
    assert field.type == MyType


def test_inputfield_with_lazy_partial_type():
    MyType = object()
    field = InputField(partial(lambda: MyType))
    assert field.type == MyType


def test_inputfield_with_string_type():
    field = InputField("graphene.types.tests.utils.MyLazyType")
    assert field.type == MyLazyType


def test_inputfield_with_default_value():
    class MyInput(InputObjectType):
        name = InputField(String, default_value="Emma", required=True)
        good_person = InputField(Boolean, default_value=True, required=True)

    class Query(ObjectType):
        a = String()

    class TestMutation(Mutation):
        class Arguments:
            my_field = MyInput(required=True)

        Output = Boolean

        def mutate(root, info, my_field):
            return my_field.good_person

    class MyMutation(ObjectType):
        test_mutation = TestMutation.Field(required=True)

    schema = Schema(query=Query, mutation=MyMutation)
    result = schema.execute(
        """
        mutation {
            testMutation(myField: {})
        }
        """
    )

    assert not result.errors
    assert result.data == {"testMutation": True}
