Cookbook Example Django Project
===============================

This example project demos integration between Graphene, Flask and SQLAlchemy.
The project contains two models, one named `Department` and another
named `Employee`.

Getting started
---------------

First you'll need to get the source of the project. Do this by cloning the
whole Graphene repository:

```bash
# Get the example project code
git clone https://github.com/graphql-python/graphene.git
cd graphene/examples/cookbook
```

It is good idea (but not required) to create a virtual environment
for this project. We'll do this using
[virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
to keep things simple,
but you may also find something like
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)
to be useful:

```bash
# Create a virtualenv in which we can install the dependencies
virtualenv env
source env/bin/activate
```

Now we can install our dependencies:

```bash
pip install -r requirements.txt
```

Now the following command will setup the database, and start the server:

```bash
./app.py

```


Now head on over to
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)
and run some queries!
