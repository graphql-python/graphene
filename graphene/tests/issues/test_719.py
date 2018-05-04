# https://github.com/graphql-python/graphene/issues/719

import graphene


class InvitationType(graphene.ObjectType):
    creation_date = graphene.String()


class CreateInvitation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    invitation = graphene.Field(InvitationType)

    def mutate(self, info, email):
        return InvitationType(creation_date='2018-05-04T14:45:36')


class Mutations(graphene.ObjectType):
    create_invitation = CreateInvitation.Field()


class Query(graphene.ObjectType):
    name = graphene.String(default_value="Dave")


def test_issue():
    query_string = '''
        mutation ($email: String!) {
           createInvitation(email: $email) {
               invitation {
                   creationDate
              }
           }
        }
    '''

    schema = graphene.Schema(query=Query, mutation=Mutations)
    result = schema.execute(query_string, variable_values={
        'email': 'foo@bar.com',
    })

    assert not result.errors
    # assert result.data['someField'] == 'Oh'
