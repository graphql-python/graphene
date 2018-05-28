Mutations
=========

Most APIs don’t just allow you to read data, they also allow you to
write.

In GraphQL, this is done using mutations. Just like queries,
Relay puts some additional requirements on mutations, but Graphene
nicely manages that for you. All you need to do is make your mutation a
subclass of ``relay.ClientIDMutation``.

.. code:: python

    class IntroduceShip(relay.ClientIDMutation):

        class Input:
            ship_name = graphene.String(required=True)
            faction_id = graphene.String(required=True)

        ship = graphene.Field(Ship)
        faction = graphene.Field(Faction)

        @classmethod
        def mutate_and_get_payload(cls, root, info, **input):
            ship_name = input.ship_name
            faction_id = input.faction_id
            ship = create_ship(ship_name, faction_id)
            faction = get_faction(faction_id)
            return IntroduceShip(ship=ship, faction=faction)



Accepting Files
---------------

Mutations can also accept files, that's how it will work with different integrations:

.. code:: python

    class UploadFile(graphene.ClientIDMutation):
         class Input:
             pass
             # nothing needed for uploading file

         # your return fields
         success = graphene.String()

        @classmethod
        def mutate_and_get_payload(cls, root, info, **input):
            # When using it in Django, context will be the request
            files = info.context.FILES
            # Or, if used in Flask, context will be the flask global request
            # files = context.files

            # do something with files

            return UploadFile(success=True)
