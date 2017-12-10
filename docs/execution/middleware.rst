Middleware
==========

You can use ``middleware`` to affect the evaluation of fields in your schema.

A middleware is any object or function that responds to ``resolve(next_middleware, *args)``.

Inside that method, it should either:

- Send ``resolve`` to the next middleware to continue the evaluation; or
- Return a value to end the evaluation early.


Resolve arguments
-----------------

Middlewares ``resolve`` is invoked with several arguments:

- ``next`` represents the execution chain. Call ``next`` to continue evalution.
- ``root`` is the root value object passed throughout the query.
- ``info`` is the resolver info.
- ``args`` is the dict of arguments passed to the field.

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


Functional example
------------------

Middleware can also be defined as a function. Here we define a middleware that
logs the time it takes to resolve each field

.. code:: python

    from time import time as timer

    def timing_middleware(next, root, info, **args):
        start = timer()
        return_value = next(root, info, **args)
        duration = timer() - start
        logger.debug("{parent_type}.{field_name}: {duration} ms".format(
            parent_type=root._meta.name if root else '',
            field_name=info.field_name,
            duration=round(duration * 1000, 2)
        ))
        return return_value


And then execute it with:

.. code:: python

    result = schema.execute('THE QUERY', middleware=[timing_middleware])
