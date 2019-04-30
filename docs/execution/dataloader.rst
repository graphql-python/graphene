Dataloader
==========

DataLoader is a generic utility to be used as part of your application's
data fetching layer to provide a simplified and consistent API over
various remote data sources such as databases or web services via batching
and caching.


Batching
--------

Batching is not an advanced feature, it's DataLoader's primary feature.
Create loaders by providing a batch loading function.

.. code:: python

    from promise import Promise
    from promise.dataloader import DataLoader

    class UserLoader(DataLoader):
        def batch_load_fn(self, keys):
            # Here we return a promise that will result on the
            # corresponding user for each key in keys
            return Promise.resolve([get_user(id=key) for key in keys])


A batch loading function accepts a list of keys, and returns a ``Promise``
which resolves to a list of ``values``.

Then load individual values from the loader. ``DataLoader`` will coalesce all
individual loads which occur within a single frame of execution (executed once
the wrapping promise is resolved) and then call your batch function with all
requested keys.


.. code:: python

    user_loader = UserLoader()

    user_loader.load(1).then(lambda user: user_loader.load(user.best_friend_id))

    user_loader.load(2).then(lambda user: user_loader.load(user.best_friend_id))


A naive application may have issued *four* round-trips to a backend for the
required information, but with ``DataLoader`` this application will make at most *two*.

Note that loaded values are one-to-one with the keys and must have the same
order. This means that if you load all values from a single query, you must
make sure that you then order the query result for the results to match the keys:


.. code:: python

   class UserLoader(DataLoader):
       def batch_load_fn(self, keys):
           users = {user.id: user for user in User.objects.filter(id__in=keys)}
           return Promise.resolve([users.get(user_id) for user_id in keys])


``DataLoader`` allows you to decouple unrelated parts of your application without
sacrificing the performance of batch data-loading. While the loader presents
an API that loads individual values, all concurrent requests will be coalesced
and presented to your batch loading function. This allows your application to
safely distribute data fetching requirements throughout your application and
maintain minimal outgoing data requests.



Using with Graphene
-------------------

DataLoader pairs nicely well with Graphene/GraphQL. GraphQL fields are designed
to be stand-alone functions. Without a caching or batching mechanism, it's easy
for a naive GraphQL server to issue new database requests each time a field is resolved.

Consider the following GraphQL request:


.. code::

    {
      me {
        name
        bestFriend {
          name
        }
        friends(first: 5) {
          name
          bestFriend {
            name
          }
        }
      }
    }


Naively, if ``me``, ``bestFriend`` and ``friends`` each need to request the backend,
there could be at most 13 database requests!


When using DataLoader, we could define the User type using our previous example with
leaner code and at most 4 database requests, and possibly fewer if there are cache hits.


.. code:: python

    class User(graphene.ObjectType):
        name = graphene.String()
        best_friend = graphene.Field(lambda: User)
        friends = graphene.List(lambda: User)

        @staticmethod
        def resolve_best_friend(user, info):
            return user_loader.load(root.best_friend_id)

        @staticmethod
        def resolve_friends(user, info):
            return user_loader.load_many(root.friend_ids)
