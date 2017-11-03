Middleware
==========

You can use ``middleware`` to affect the evaluation of fields in your schema.

A middleware is any object that responds to ``resolve(*args, next_middleware)``.

Inside that method, it should either:

- Send ``resolve`` to the next middleware to continue the evaluation; or
- Return a value to end the evaluation early.


Resolve arguments
-----------------

Middlewares ``resolve`` is invoked with several arguments:

- ``next`` represents the execution chain. Call ``next`` to continue evalution.
- ``root`` is the root value object passed throughout the query.
- ``info`` is the resolver info.
- ``args`` is the hash of arguments passed to the field.

Example
-------

This middleware only continues evaluation if the ``field_name`` is not ``'user'``

.. code:: python

    class AuthorizationMiddleware(object):
        def resolve(self, next, root, info, **args):
            if info.field_name == 'user':
                return None
            return next(root, info, **args)


And then execute it with:

.. code:: python

    result = schema.execute('THE QUERY', middleware=[AuthorizationMiddleware()])
