# v2.0 Upgrade Guide

`ObjectType`, `Interface`, `InputObjectType`, `Scalar` and `Enum` implementations
have been quite simplified, without the need to define a explicit Metaclass for each subtype.

It also improves the field resolvers, [simplifying the code](#simpler-resolvers) the
developer have to write to use them.

Deprecations:
* [`AbstractType`](#abstracttype-deprecated)
* [`resolve_only_args`](#resolve_only_args)
* [`Mutation.Input`](#mutationinput)

Breaking changes:
* [`Node Connections`](#node-connections)

New Features!
* [`InputObjectType`](#inputobjecttype)
* [`Meta as Class arguments`](#meta-ass-class-arguments) (_only available for Python 3_)


> The type metaclases are now deleted as are no longer necessary, if your code was depending
> on this strategy for creating custom attrs, see an [example on how to do it in 2.0](https://github.com/graphql-python/graphene/blob/2.0/graphene/tests/issues/test_425.py).

## Deprecations

### Simpler resolvers

All the resolvers in graphene have been simplified. If before resolvers must had received
four arguments `root`, `args`, `context` and `info`, now the `args` are passed as keyword arguments
and `context` and `info` will only be passed if the function is annotated with it.

Before:

```python
my_field = graphene.String(my_arg=graphene.String())

def resolve_my_field(self, args, context, info):
    my_arg = args.get('my_arg')
    return ...
```

With 2.0:

```python
my_field = graphene.String(my_arg=graphene.String())

def resolve_my_field(self, info, my_arg):
    return ...
```

And, if the resolver want to get the context:

```python
my_field = graphene.String(my_arg=graphene.String())

def resolve_my_field(self, info, my_arg):
    context = info.context
    return ...
```


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

### resolve\_only\_args

`resolve_only_args` is now deprecated as the resolver API has been simplified.

Before:

```python
class User(ObjectType):
    name = String()

    @resolve_only_args
    def resolve_name(self):
        return self.name
```

With 2.0:

```python
class User(ObjectType):
    name = String()

    def resolve_name(self, info):
        return self.name
```

### Mutation.Input

`Mutation.Input` is now deprecated in favor using `Mutation.Arguments` (`ClientIDMutation` still uses `Input`).

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


## Mutation.mutate

Now only receive (`root`, `info`, `**args`)


## ClientIDMutation.mutate_and_get_payload

Now only receive (`root`, `info`, `**input`)


## New Features

### InputObjectType

If you are using `InputObjectType`, you now can access
it's fields via `getattr` (`my_input.myattr`) when resolving, instead of
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
    def resolve_user(self, input):
        user_id = input.get('id')
        if is_valid_input(user_id):
            return get_user(user_id)
```

With 2.0:

```python
class UserInput(InputObjectType):
    id = ID(required=True)

    @property
    def is_valid(self):
        return self.id.startswith('userid_')

class Query(ObjectType):
    user = graphene.Field(User, input=UserInput())

    def resolve_user(self, info, id):
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

    def resolve_id(self, info):
        return "{type}_{id}".format(
            type=self.__class__.__name__,
            id=self.id
        )
```

### UUID Scalar

In Graphene 2.0 there is a new dedicated scalar for UUIDs, `UUID`.
