---
title: Tips
description: Tips when SQLAlchemy in Graphene
---

# Tips

## Querying

For make querying to the database work, there are two alternatives:

* Expose the db session when you create the `graphene.Schema`:

```python
schema = graphene.Schema(session=session)
```

* Create a query for the models.

```python
Base = declarative_base()
Base.query = db_session.query_property()

class MyModel(Base):
	# ...
```

If you don't specify any, the following error will be displayed:

`A query in the model Base or a session in the schema is required for querying.`
