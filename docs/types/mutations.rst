Mutations
=========

A Mutation is a special ObjectType that also defines an Input.

Quick example
-------------

This example defines a Mutation:

.. code:: python

    import graphene

    class CreatePerson(graphene.Mutation):
        class Arguments:
            name = graphene.String()

        ok = graphene.Boolean()
        person = graphene.Field(lambda: Person)

        def mutate(root, info, name):
            person = Person(name=name)
            ok = True
            return CreatePerson(person=person, ok=ok)

**person** and **ok** are the output fields of the Mutation when it is
resolved.

**Arguments** attributes are the arguments that the Mutation
``CreatePerson`` needs for resolving, in this case **name** will be the
only argument for the mutation.

**mutate** is the function that will be applied once the mutation is
called. This method is just a special resolver that we can change
data within. It takes the same arguments as the standard query :ref:`ResolverArguments`.

So, we can finish our schema like this:

.. code:: python

    # ... the Mutation Class

    class Person(graphene.ObjectType):
        name = graphene.String()
        age = graphene.Int()

    class MyMutations(graphene.ObjectType):
        create_person = CreatePerson.Field()

    # We must define a query for our schema
    class Query(graphene.ObjectType):
        person = graphene.Field(Person)

    schema = graphene.Schema(query=Query, mutation=MyMutations)

Executing the Mutation
----------------------

Then, if we query (``schema.execute(query_str)``) the following:

.. code::

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
                "name": "Peter"
            },
            "ok": true
        }
    }

InputFields and InputObjectTypes
----------------------------------
InputFields are used in mutations to allow nested input data for mutations

To use an InputField you define an InputObjectType that specifies the structure of your input data


.. code:: python

    import graphene

    class PersonInput(graphene.InputObjectType):
        name = graphene.String(required=True)
        age = graphene.Int(required=True)

    class CreatePerson(graphene.Mutation):
        class Arguments:
            person_data = PersonInput(required=True)

        person = graphene.Field(Person)

        def mutate(root, info, person_data=None):
            person = Person(
                name=person_data.name,
                age=person_data.age
            )
            return CreatePerson(person=person)


Note that  **name** and **age** are part of **person_data** now

Using the above mutation your new query would look like this:

.. code::

    mutation myFirstMutation {
        createPerson(personData: {name:"Peter", age: 24}) {
            person {
                name,
                age
            }
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
        latlng = graphene.InputField(LatLngInput)

Output type example
-------------------
To return an existing ObjectType instead of a mutation-specific type, set the **Output** attribute to the desired ObjectType:

.. code:: python

    import graphene

    class CreatePerson(graphene.Mutation):
        class Arguments:
            name = graphene.String()

        Output = Person

        def mutate(root, info, name):
            return Person(name=name)

Then, if we query (``schema.execute(query_str)``) the following:

.. code::

    mutation myFirstMutation {
        createPerson(name:"Peter") {
            name
            __typename
        }
    }

We should receive:

.. code:: json

    {
        "createPerson": {
            "name": "Peter",
            "__typename": "Person"
        }
    }
