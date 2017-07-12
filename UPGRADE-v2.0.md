# v1.0 Upgrade Guide

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
