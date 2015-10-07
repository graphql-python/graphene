Graphene: Pythonic GraphQL |Build Status| |Coverage Status|
===========================================================

This is a library to use GraphQL in a Pythonic and easy way. It maps the
models/fields to internal GraphQLlib objects without effort. Including
automatic `Django models`_ conversion.

Installation
------------

For instaling graphene, just run this command in your shell

.. code:: bash

    pip install graphene

Usage
-----

Example code of a GraphQL schema using Graphene:

Schema definition
~~~~~~~~~~~~~~~~~

.. code:: python

    class Character(graphene.Interface):
        id = graphene.IDField()
        name = graphene.StringField()
        friends = graphene.ListField('self')

        def resolve_friends(self, args, *_):
            return [Human(f) for f in self.instance.friends]

    class Human(Character):
        homePlanet = graphene.StringField()

    class Query(graphene.ObjectType):
        human = graphene.Field(Human)

    schema = graphene.Schema(query=Query)

Querying
~~~~~~~~

Querying ``graphene.Schema`` is as simple as:

.. code:: python

    query = '''
        query HeroNameQuery {
          hero {
            name
          }
        }
    '''
    result = schema.execute(query)

Relay Schema
~~~~~~~~~~~~

Graphene also supports Relay, check the `Starwars Relay example`_!

.. code:: python

    class Ship(relay.Node):
        '''A ship in the Star Wars saga'''
        name = graphene.StringField(description='The name of the ship.')

        @classmethod
        def get_node(cls, id):
            return Ship(getShip(id))


    class Query(graphene.ObjectType):
        ships = relay.ConnectionField(Ship, description='The ships used by the faction.')
        node = relay.NodeField()

        @resolve_only_args
        def resolve_ships(self):
            return [Ship(s) for s in getShips()]

Django+Relay Schema
~~~~~~~~~~~~~~~~~~~

If you want to use graphene with your Django Models check the `Starwars
Django example`_!

.. code:: python

    class Ship(DjangoNode):
        class Meta:
            model = YourDjangoModelHere
            # only_fields = ('id', 'name') # Only map this fields from the model
            # excluxe_fields ('field_to_excluxe', ) # Exclude mapping this fields from the model

    class Query(graphene.ObjectType):
        node = relay.NodeField()

Contributing
------------

After cloning this repo, ensure dependencies are installed by running:

.. code:: sh

    python setup.py install

After developing, the full test suite can be evaluated by running:

.. code:: sh

    python setup.py test # Use --pytest-args="-v -s" for verbose mode

.. _Django models: #djangorelay-schema
.. _Starwars Relay example: tests/starwars_relay
.. _Starwars Django example: tests/starwars_django

.. |Build Status| image:: https://travis-ci.org/graphql-python/graphene.svg?branch=master
   :target: https://travis-ci.org/graphql-python/graphene
.. |Coverage Status| image:: https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/graphql-python/graphene?branch=master
