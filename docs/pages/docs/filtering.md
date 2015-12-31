---
title: Filtering (Django)
description: Details of how to perform filtering
---

# Filtering (Django)

Graphene integrates with [django-filter](https://django-filter.readthedocs.org)
to provide filtering of results. See the
[usage documentation](https://django-filter.readthedocs.org/en/latest/usage.html#the-filter)
for details on the format for `filter_fields`.

**Note 1:** This filtering is only available when using the Django integrations
(i.e. nodes which extend `DjangoNode`)

**Note 2:** `django-filter` is an optional dependency of Graphene. You will need to
install it manually, which can be done as follows:

```bash
pip install django-filter
```

## Filterable fields

The `filter_fields` parameter is used to specify the fields which can be filtered upon.
The value specified here is passed directly to `django-filter`, so see the
[filtering documentation](https://django-filter.readthedocs.org/en/latest/usage.html#the-filter)
for full details on the range of options available.

For example:

```python
class AnimalNode(DjangoNode):
    class Meta:
        # Assume you have an Animal model defined with the following fields
        model = Animal
        filter_fields = ['name', 'genus', 'is_domesticated']

class Query(ObjectType):
    animal = relay.NodeField(AnimalNode)
    all_animals = DjangoFilterConnectionField(AnimalNode)
```

You could then perform a query such as:

```graphql
query {
  # Note that fields names become camelcased
  allAnimals(genus: "cat", isDomesticated: true) {
    edges {
      node {
        id,
        name
}}}}
```

You can also make more complex lookup types available:

```python
class AnimalNode(DjangoNode):
    class Meta:
        model = Animal
        # Provide more complex lookup types
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'genus': ['exact'],
            'is_domesticated': ['exact'],
        }
```

Which you could query as follows:

```graphql
query {
  # Note that fields names become camelcased
  allAnimals(nameIcontains: "lion") {
    edges {
      node {
        id,
        name
}}}}
```

## Orderable fields

Ordering can also be specified using `filter_order_by`. Like `filter_fields`,
this value is also passed directly to `django-filter` as the `order_by` field.
For full details see the
[order_by documentation](https://django-filter.readthedocs.org/en/latest/usage.html#ordering-using-order-by).

For example:

```python
class AnimalNode(DjangoNode):
    class Meta:
        model = Animal
        filter_fields = ['name', 'genus', 'is_domesticated']
        # Either a tuple/list of fields upon which ordering is allowed, or
        # True to allow filtering on all fields specified in filter_fields
        order_by_fields = True
```

You can then control the ordering via the `orderBy` argument:

```graphql
query {
  allAnimals(orderBy: "name") {
    edges {
      node {
        id,
        name
}}}}
```

## Custom Filtersets

By default Graphene provides easy access to the most commonly used
features of `django-filter`. This is done by transparently creating a
`django_filters.FilterSet` class for you and passing in the values for
`filter_fields` and `order_by_fields`.

However, you may find this to be insufficient. In these cases you can
create your own `Filterset` as follows:

```python
class AnimalNode(DjangoNode):
    class Meta:
        # Assume you have an Animal model defined with the following fields
        model = Animal
        filter_fields = ['name', 'genus', 'is_domesticated']


class AnimalFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    name = django_filters.CharFilter(lookup_type='iexact')

    class Meta:
        model = Animal
        fields = ['name', 'genus', 'is_domesticated']


class Query(ObjectType):
    animal = relay.NodeField(AnimalNode)
    # We specify our custom AnimalFilter using the filterset_class param
    all_animals = DjangoFilterConnectionField(AnimalNode,
                                              filterset_class=AnimalFilter)
```
