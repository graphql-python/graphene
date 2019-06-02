Mutations
=========

A Mutation is a special ObjectType that also defines an Input.

Quick example
-------------

This example defines a Mutation:

.. code:: python

    from graphene import Mutation, String, Boolean, Field


    class CreatePerson(Mutation):
        class Arguments:
            name = String()

        ok = Boolean()
        person = Field(lambda: Person)

        def mutate(self, info, name):
            person = Person(name=name)
            ok = True
            return CreatePerson(person=person, ok=ok)

**person** and **ok** are the output fields of the Mutation when it is
resolved.

**Arguments** attributes are the arguments that the Mutation
``CreatePerson`` needs for resolving, in this case **name** will be the
only argument for the mutation.

**mutate** is the function that will be applied once the mutation is
called.

So, we can finish our schema like this:

.. code:: python

    from graphene import ObjectType, Mutation, String, Boolean, Field, Int, Schema


    class Person(ObjectType):
        name = String()
        age = Int()


    class CreatePerson(Mutation):
        class Arguments:
            name = String()

        ok = Boolean()
        person = Field(lambda: Person)

        def mutate(self, info, name):
            person = Person(name=name)
            ok = True
            return CreatePerson(person=person, ok=ok)


    class MyMutations(ObjectType):
        create_person = CreatePerson.Field()


    # We must define a query for our schema
    class Query(ObjectType):
        person = Field(Person)


    schema = Schema(query=Query, mutation=MyMutations)

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

    from graphene import InputObjectType, Mutation, String, Field, Int


    class PersonInput(InputObjectType):
        name = String(required=True)
        age = Int(required=True)


    class CreatePerson(Mutation):
        class Arguments:
            person_data = PersonInput(required=True)

        person = Field(Person)

        @staticmethod
        def mutate(root, info, person_data=None):
            person = Person(name=person_data.name, age=person_data.age)
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

    from graphene import InputObjectType, InputField, Float, String


    class LatLngInput(InputObjectType):
        lat = Float()
        lng = Float()


    # A location has a latlng associated to it
    class LocationInput(InputObjectType):
        name = String()
        latlng = InputField(LatLngInput)

Output type example
-------------------
To return an existing ObjectType instead of a mutation-specific type, set the **Output** attribute to the desired ObjectType:

.. code:: python

    from graphene import Mutation, String


    class CreatePerson(Mutation):
        class Arguments:
            name = String()

        Output = Person

        def mutate(self, info, name):
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
