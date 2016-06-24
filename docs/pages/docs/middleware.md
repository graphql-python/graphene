---
title: Middleware
description: Walkthrough Middleware
---

# Middleware

You can use _middleware_ to affect the evaluation of fields in your schema.

A middleware is any object that responds to `resolve(*args, next_middleware)`. Inside that method, it should either:

* Send `resolve` to the next middleware to continue the evaluation; or
* Return a value to end the evaluation early.

Middlewares' `resolve` is invoked with several arguments:

* `next` represents the execution chain. Call `next` to continue evalution.
* `root` is the root value object passed throughout the query
* `args` is the hash of arguments passed to the field
* `context` is the context object passed throughout the query
* `info` is the resolver info

Add a middleware to a schema by adding to the `middlewares` list.


### Example: Authorization

This middleware only continues evaluation if the `field_name` is not `'user'`:

```python
class AuthorizationMiddleware(object):

    def resolve(self, next, root, args, context, info):
        if info.field_name == 'user':
            return None
        return next(root, args, context, info)
```

Then, add the middleware to your schema:

```python
schema = Schema(middlewares=[AuthorizationMiddleware()])
```
