Writing your first Graphene Schema
==================================

This tutorial is roughly based on Django's poll tutorial.
It will be divided in multiple steps.

We will assume that you already have Graphene installed.
The tutorial will be based on Graphene 2.0 and Python 3.6.

TODO: link to installation documentation.

In this tutorial we are going to build a super simple polls application,
the user will be able to query all the questions and the will be able to
answer each question by id.

We won't be using a database for now, since we'd like to keep this
tutorial simple and not force you to use a specific framework.

Creating your project
---------------------

Each graphene project is composed of a single Schema (
    TODO: link to what a schema is in the GraphQL documentation
), the suggested convention is to create a main ``schema.py`` file which
will contain your schema and ``schema.py`` files for each of your module.

Let's starts by creating your first GraphQL schema, go to :ref:`tutorial-part-1`.
