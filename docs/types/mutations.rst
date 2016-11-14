Mutations
=========

A Mutation is a special ObjectType that also defines an Input.

Quick example
-------------

This example defines a Mutation:

.. code:: python

    import graphene

    class CreatePerson(graphene.Mutation):
        class Input:
            name = graphene.String()

        ok = graphene.Boolean()
        person = graphene.Field(lambda: Person)

        def mutate(self, args, context, info):
            person = Person(name=args.get('name'))
            ok = True
            return CreatePerson(person=person, ok=ok)

**person** and **ok** are the output fields of the Mutation when is
resolved.

**Input** attributes are the arguments that the Mutation
``CreatePerson`` needs for resolving, in this case **name** will be the
only argument for the mutation.

**mutate** is the function that will be applied once the mutation is
called.

So, we can finish our schema like this:

.. code:: python

    # ... the Mutation Class

    class Person(graphene.ObjectType):
        name = graphene.String()

    class MyMutations(graphene.ObjectType):
        create_person = CreatePerson.Field()

    schema = graphene.Schema(mutation=MyMutations)

Executing the Mutation
----------------------

Then, if we query (``schema.execute(query_str)``) the following:

.. code:: graphql

    mutation myFirstMutation {
        createPerson(name:"Peter") {
            person {
                name
            }
            ok
        }
    }

We should receive:

.. code:: json

    {
        "createPerson": {
            "person" : {
                name: "Peter"
            },
            "ok": true
        }
    }

InputFields and InputObjectTypes
----------------------
InputFields are used in mutations to allow nested input data for mutations

To use an InputField you define an InputObjectType that specifies the structure of your input data




.. code:: python

    import graphene

    class PersonInput(graphene.InputObjectType):
        name = graphene.String()
        age = graphene.Int()

    class CreatePerson(graphene.Mutation):
        class Input:
            person_data = graphene.InputField(PersonInput)

        person = graphene.Field(lambda: Person)

        def mutate(self, args, context, info):
            p_data = args.get('person_data')

            name = p_data.get('name')
            age = p_data.get('age')

            person = Person(name=name, age=age)
            return CreatePerson(person=person)


Note that  **name** and **age** are part of **person_data** now

Using the above mutation your new query would look like this:

.. code:: graphql

    mutation myFirstMutation {
        createPerson(personData: {name:"Peter", age: 24}) {
            person {
                name
            }
            ok
        }
    }

InputObjectTypes can also be fields of InputObjectTypes allowing you to have
as complex of input data as you need

.. code:: python

    import graphene

    class LatLngInput(graphene.InputObjectType):
        lat = graphene.Float()
        lng = graphene.Float()

    #A location has a latlng associated to it
    class LocationInput(graphene.InputObjectType):
        name = graphene.String()
        latlng = graphene.InputField(LatLngInputType)


