import graphene


class SecondChild(graphene.ObjectType):
    hello = graphene.String()


def resolve_second_child(self, info):
    return SecondChild(hello=self.second_child._test)


second_child_f = graphene.Field(SecondChild, resolver=resolve_second_child)


class FirstChild(graphene.ObjectType):
    hello = graphene.String()
    second_child = second_child_f


def resolve_first_child(self, info):
    message = self.first_child._test + " stranger"

    test_case = {"_test": message}

    return FirstChild(
        hello=self.first_child._test, second_child=SecondChild(**test_case)
    )


first_child_f = graphene.Field(FirstChild, resolver=resolve_first_child)


class ParentQuery(graphene.ObjectType):
    hello = graphene.String()
    first_child = first_child_f


def resolve_parent(self, info, **args):

    message = args.get("greeting") + " there"

    test_case = {"_test": message}

    return ParentQuery(hello=args.get("greeting"), first_child=FirstChild(**test_case))


parent = graphene.Field(
    ParentQuery, resolver=resolve_parent, greeting=graphene.Argument(graphene.String)
)


class Query(graphene.ObjectType):
    final = parent


def test_issue():
    query_string = """
    query {
        final (greeting: "hi") {
            hello
            firstChild {
                hello
                secondChild {
                    hello
                }
            }
        }
    }
    """

    schema = graphene.Schema(query=Query)
    result = schema.execute(query_string)

    assert not result.errors
    assert result.data["final"]["hello"] == "hi"
    assert result.data["final"]["firstChild"]["hello"] == "hi there"
    assert (
        result.data["final"]["firstChild"]["secondChild"]["hello"]
        == "hi there stranger"
    )
