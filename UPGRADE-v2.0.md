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
