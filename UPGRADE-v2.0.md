# v2.0 Upgrade Guide

`ObjectType`, `Interface`, `InputObjectType`, `Scalar` and `Enum` implementations
have been quite simplified, without the need to define a explicit Metaclass for each subtype.

It also improves the field resolvers, [simplifying the code](#simpler-resolvers) the
developer has to write to use them.

**Deprecations:**

- [`AbstractType`](#abstracttype-deprecated)
- [`resolve_only_args`](#resolve_only_args)
- [`Mutation.Input`](#mutationinput)

**Breaking changes:**

- [`Simpler Resolvers`](#simpler-resolvers)
- [`Node Connections`](#node-connections)

**New Features!**

- [`InputObjectType`](#inputobjecttype)
- [`Meta as Class arguments`](#meta-as-class-arguments) (_only available for Python 3_)

> The type metaclasses are now deleted as they are no longer necessary. If your code was depending
> on this strategy for creating custom attrs, see an [example on how to do it in 2.0](https://github.com/graphql-python/graphene/blob/v2.0.0/graphene/tests/issues/test_425.py).

## Deprecations

### AbstractType deprecated

AbstractType is deprecated in graphene 2.0, you can now use normal inheritance instead.

Before:

```python
class CommonFields(AbstractType):
    name = String()

class Pet(CommonFields, Interface):
    pass
```

With 2.0:

```python
class CommonFields(object):
    name = String()

class Pet(CommonFields, Interface):
    pass
```

### resolve_only_args

`resolve_only_args` is now deprecated as the resolver API has been simplified.

Before:

```python
class User(ObjectType):
    name = String()

    @resolve_only_args
    def resolve_name(root):
        return root.name
```

With 2.0:

```python
class User(ObjectType):
    name = String()

    def resolve_name(root, info):
        return root.name
```

### Mutation.Input

`Mutation.Input` is now deprecated in favor of using `Mutation.Arguments` (`ClientIDMutation` still uses `Input`).

Before:

```python
class User(Mutation):
    class Input:
        name = String()
```

With 2.0:

```python
class User(Mutation):
    class Arguments:
        name = String()
```

## Breaking Changes

### Simpler resolvers

All the resolvers in graphene have been simplified.
Prior to Graphene `2.0`, all resolvers required four arguments: `(root, args, context, info)`.
Now, resolver `args` are passed as keyword arguments to the function, and `context` argument dissapeared in favor of `info.context`.

Before:

```python
my_field = graphene.String(my_arg=graphene.String())

def resolve_my_field(root, args, context, info):
    my_arg = args.get('my_arg')
    return ...
```

With 2.0:

```python
my_field = graphene.String(my_arg=graphene.String())

def resolve_my_field(root, info, my_arg):
    return ...
```

**PS.: Take care with receiving args like `my_arg` as above. This doesn't work for optional (non-required) arguments as stantard `Connection`'s arguments (first, before, after, before).**
You may need something like this:

```python
def resolve_my_field(root, info, known_field1, known_field2, **args): ## get other args with: args.get('arg_key')
```

And, if you need the context in the resolver, you can use `info.context`:

```python
my_field = graphene.String(my_arg=graphene.String())

def resolve_my_field(root, info, my_arg):
    context = info.context
    return ...
```

### Node Connections

Node types no longer have a `Connection` by default.
In 2.0 and onwards `Connection`s should be defined explicitly.

Before:

```python
class User(ObjectType):
    class Meta:
        interfaces = [relay.Node]
    name = String()

class Query(ObjectType):
    user_connection = relay.ConnectionField(User)
```

With 2.0:

```python
class User(ObjectType):
    class Meta:
        interfaces = [relay.Node]
    name = String()

class UserConnection(relay.Connection):
    class Meta:
        node = User

class Query(ObjectType):
    user_connection = relay.ConnectionField(UserConnection)
```

## Node.get_node

The method `get_node` in `ObjectTypes` that have `Node` as interface, changes its API.
From `def get_node(cls, id, context, info)` to `def get_node(cls, info, id)`.

```python
class MyObject(ObjectType):
    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, id, context, info):
        return ...
```

To:

```python
class MyObject(ObjectType):
    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, id):
        return ...
```

## Node.get_node_from_global_id

The parameters' order of `get_node_from_global_id` method has changed. You may need to adjust your [Node Root Field](http://docs.graphene-python.org/en/latest/relay/nodes/#node-root-field) and maybe other places that uses this method to obtain an object.

Before:

```python
class RootQuery(object):
    ...
    node = Field(relay.Node, id=ID(required=True))

    def resolve_node(root, args, context, info):
        node = relay.Node.get_node_from_global_id(args['id'], context, info)
        return node
```

Now:

```python
class RootQuery(object):
    ...
    node = Field(relay.Node, id=ID(required=True))

    def resolve_node(root, info, id):
        node = relay.Node.get_node_from_global_id(info, id)
        return node
```

## Mutation.mutate

Now only receives (`root`, `info`, `**kwargs`) and is not a @classmethod

Before:

```python
class SomeMutation(Mutation):
    ...

    @classmethod
    def mutate(cls, instance, args, context, info):
        ...
```

With 2.0:

```python
class SomeMutation(Mutation):
    ...

    def mutate(root, info, **args):
        ...
```

With 2.0 you can also get your declared (as above) `args` this way:

```python
class SomeMutation(Mutation):
    class Arguments:
        first_name = String(required=True)
        last_name = String(required=True)
    ...

    def mutate(root, info, first_name, last_name):
        ...
```

## ClientIDMutation.mutate_and_get_payload

Now only receives (`root`, `info`, `**input`)

### Middlewares

If you are using Middelwares, you need to some adjustments:

Before:

```python
class MyGrapheneMiddleware(object):
    def resolve(self, next_mw, root, args, context, info):

        ## Middleware code

        return next_mw(root, args, context, info)
```

With 2.0:

```python
class MyGrapheneMiddleware(object):
    def resolve(self, next_mw, root, info, **args):
        context = info.context

        ## Middleware code

        info.context = context
        return next_mw(root, info, **args)
```

## New Features

### InputObjectType

If you are using `InputObjectType`, you now can access
its fields via `getattr` (`my_input.myattr`) when resolving, instead of
the classic way `my_input['myattr']`.

And also use custom defined properties on your input class.

Example. Before:

```python
class UserInput(InputObjectType):
    id = ID(required=True)

def is_valid_input(input):
    return input.get('id').startswith('userid_')

class Query(ObjectType):
    user = graphene.Field(User, input=UserInput())

    @resolve_only_args
    def resolve_user(root, input):
        user_id = input.get('id')
        if is_valid_input(user_id):
            return get_user(user_id)
```

With 2.0:

```python
class UserInput(InputObjectType):
    id = ID(required=True)

    @property
    def is_valid(root):
        return root.id.startswith('userid_')

class Query(ObjectType):
    user = graphene.Field(User, input=UserInput())

    def resolve_user(root, info, input):
        if input.is_valid:
            return get_user(input.id)
```

### Meta as Class arguments

Now you can use the meta options as class arguments (**ONLY PYTHON 3**).

Before:

```python
class Dog(ObjectType):
    class Meta:
        interfaces = [Pet]
    name = String()
```

With 2.0:

```python
class Dog(ObjectType, interfaces=[Pet]):
    name = String()
```

### Abstract types

Now you can create abstact types super easily, without the need of subclassing the meta.

```python
class Base(ObjectType):
    class Meta:
        abstract = True

    id = ID()

    def resolve_id(root, info):
        return "{type}_{id}".format(
            type=root.__class__.__name__,
            id=root.id
        )
```

### UUID Scalar

In Graphene 2.0 there is a new dedicated scalar for UUIDs, `UUID`.
