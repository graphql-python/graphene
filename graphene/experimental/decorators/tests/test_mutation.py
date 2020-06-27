from textwrap import dedent

from graphene import String, ObjectType, Schema, Union, Field

from ..mutation import mutation


def test_mutation_basic():
    @mutation(String, required=True)
    def my_mutation(root, info):
        return "hi"

    class Query(ObjectType):
        a = String()

    schema = Schema(query=Query, mutations=[my_mutation])
    result = schema.execute(
        """
        mutation MyMutation {
            myMutation
        }
    """
    )

    assert not result.errors
    assert result.data == {"myMutation": "hi"}


def test_mutation_arguments():
    @mutation(String, required=True, arguments={"name": String(required=True)})
    def my_mutation(root, info, name):
        return f"hi {name}"

    class Query(ObjectType):
        a = String()

    schema = Schema(query=Query, mutations=[my_mutation])
    result = schema.execute(
        """
        mutation MyMutation {
            myMutation(name: "world")
        }
    """
    )

    assert not result.errors
    assert result.data == {"myMutation": "hi world"}


def test_mutation_field_options():
    @mutation(
        String,
        required=True,
        arguments={"name": String(required=True)},
        name="other_mutation",
        deprecation_reason="Don't use this mutation",
        description="Some description",
    )
    def my_mutation(root, info, name):
        return f"hi {name}"

    class Query(ObjectType):
        a = String()

    schema = Schema(query=Query, mutations=[my_mutation])
    result = schema.execute(
        """
        mutation MyMutation {
            otherMutation(name: "world")
        }
    """
    )

    assert not result.errors
    assert result.data == {"otherMutation": "hi world"}

    assert str(schema) == dedent(
        """\
        type Query {
          a: String
        }

        type Mutation {
          \"\"\"Some description\"\"\"
          otherMutation(name: String!): String! @deprecated(reason: \"Don't use this mutation\")
        }
    """
    )


def test_mutation_complex_return():
    class User(ObjectType):
        name = String(required=True)

    class CreateUserSuccess(ObjectType):
        user = Field(User, required=True)

    class CreateUserError(ObjectType):
        error_message = String(required=True)

    class CreateUserOutput(Union):
        class Meta:
            types = [
                CreateUserSuccess,
                CreateUserError,
            ]

    @mutation(
        CreateUserOutput, required=True, arguments={"name": String(required=True)}
    )
    def create_user(root, info, name):
        return CreateUserSuccess(user=User(name=name))

    class Query(ObjectType):
        a = String()

    schema = Schema(query=Query, mutations=[create_user])
    result = schema.execute(
        """
        mutation CreateUserMutation {
            createUser(name: "Kate") {
                __typename
                ... on CreateUserSuccess {
                    user {
                        name
                    }
                }
            }
        }
    """
    )

    assert not result.errors
    assert result.data == {
        "createUser": {"__typename": "CreateUserSuccess", "user": {"name": "Kate"}}
    }

    assert str(schema) == dedent(
        """\
        type Query {
          a: String
        }

        type Mutation {
          createUser(name: String!): CreateUserOutput!
        }

        union CreateUserOutput = CreateUserSuccess | CreateUserError

        type CreateUserSuccess {
          user: User!
        }

        type User {
          name: String!
        }

        type CreateUserError {
          errorMessage: String!
        }
    """
    )
