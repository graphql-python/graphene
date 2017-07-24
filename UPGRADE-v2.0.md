# v2.0 Upgrade Guide

* `ObjectType`, `Interface`, `InputObjectType`, `Scalar` and `Enum` implementations
  have been quite simplified, without the need of define a explicit Metaclass.
  The metaclasses threfore are now deleted as are no longer necessary, if your code was depending
  on this internal metaclass for creating custom attrs, please see an [example of how to do it now in 2.0](https://github.com/graphql-python/graphene/blob/master/graphene/tests/issues/test_425_graphene2.py).

## Deprecations


*  AbstractType is deprecated, please use normal inheritance instead.

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

* Meta options as class arguments (**ONLY PYTHON 3**).
  
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

## Breaking Changes

* Node types no longer have a `Connection` by default.
  In 2.0 and onwoards `Connection`s should be defined explicitly.
  
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

## New Features

### InputObjectType

`InputObjectType`s are now a first class citizen in Graphene.
That means, if you are using a custom InputObjectType, you can access
it's fields via `getattr` (`my_input.myattr`) when resolving, instead of
the classic way `my_input['myattr']`.

And also use custom defined properties on your input class.

Example. Before:

```python
class User(ObjectType):
    name = String()

class UserInput(InputObjectType):
    id = ID()

def is_user_id(id):
    return id.startswith('userid_')

class Query(ObjectType):
    user = graphene.Field(User, id=UserInput())

    @resolve_only_args
    def resolve_user(self, input):
        user_id = input.get('id')
        if is_user_id(user_id):
            return get_user(user_id)
```

With 2.0:

```python
class User(ObjectType):
    id = ID()

class UserInput(InputObjectType):
    id = ID()

    @property
    def is_user_id(self):
        return id.startswith('userid_')

class Query(ObjectType):
    user = graphene.Field(User, id=UserInput())

    @annotate(input=UserInput)
    def resolve_user(self, input):
        if input.is_user_id:
            return get_user(input.id)

    # You can also do in Python 3:
    def resolve_user(self, input: UserInput):
        if input.is_user_id:
            return get_user(input.id)

```
