---
title: Authorization
description: Details on how to restrict data access
---

# Authorization in Django

There are two main ways you may want to limit access to data when working
with Graphene and Django: limiting which fields are accessible via GraphQL
and limiting which objects a user can access.

Let's use a simple example model.

```python
from django.db import models

class Post(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    published = models.BooleanField(default=False)
    owner = models.ForeignKey('auth.User')
```

## Limiting Field Access

This is easy, simply use the `only_fields` meta attribute.

```python
from graphene.contrib.django.types import DjangoNode
from .models import Post

class PostNode(DjangoNode):
    class Meta:
        model = Post
        only_fields = ('title', 'content')
```

## Queryset Filtering On Lists

In order to filter which objects are available in a queryset-based list,
define a resolve method for that field and return the desired queryset.

```python
from graphene import ObjectType
from graphene.contrib.django.filter import DjangoFilterConnectionField
from .models import Post

class Query(ObjectType):
    all_posts = DjangoFilterConnectionField(CategoryNode)

    class Meta:
        abstract = True

    def resolve_all_posts(self, args, info):
        return Post.objects.filter(published=True)
```

## User-based Queryset Filtering

If you are using `graphql-django-view` you can access Django's request object
via `info.request_context`.

```python
from graphene import ObjectType
from graphene.contrib.django.filter import DjangoFilterConnectionField
from .models import Post

class Query(ObjectType):
    my_posts = DjangoFilterConnectionField(CategoryNode)

    class Meta:
        abstract = True

    def resolve_my_posts(self, args, info):
        if not info.request_context.user.is_authenticated():
            return []
        else:
            return Post.objects.filter(owner=info.request_context.user)
```

If you're using your own view, passing the request context into the schema is
simple.

```python
result = schema.execute(query, request_context=request)
```

## Filtering ID-based node access

In order to add authorization to id-based node access, we need to add a method
to your `DjangoNode`.

```python
from graphene.contrib.django.types import DjangoNode
from .models import Post

class PostNode(DjangoNode):
    class Meta:
        model = Post
        only_fields = ('title', 'content')

    @classmethod
    def get_node(Cls, id, info):
        try:
            post = Cls._meta.model.objects.get(id=id)
        except Cls._meta.model.DoesNotExist:
            return None

        if post.published or info.request_context.user is post.owner:
            return Cls(instance)
        else:
            return None
```
