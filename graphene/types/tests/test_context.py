from ..context import Context
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema


class Query(ObjectType):
    hello = String()

    def resolve_hello(self, info):
        assert isinstance(info.context, Context)
        assert hasattr(info.context, "loaders")
        assert hasattr(info.context, "request")
        return "World"


test_schema = Schema(query=Query)


def test_context_with_kwargs():
    class Request:
        pass

    class Loader:
        pass

    context = Context(loaders=Loader, request=Request)
    test_schema.execute("{hello}", context)


def text_context_with_dict():
    class Request:
        pass

    class Loader:
        pass

    context_dict = {"loader": Loader, "request": Request}
    context = Context(**context_dict)
    test_schema.execute("{hello}", context)
