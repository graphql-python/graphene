======================
Security consideration
======================

This section will discuss the most common security risks and how to mitigate them.

As GraphQL is a query language, it allows users to use a wider pannel of inputs than traditional REST APIs.

Due to this feature, GraphQL APIs are inherently prone to various security risks, but they can be reduced by taking appropriate precautions. Neglecting them can expose the API to vulnerabilities like credential leakage or denial of service attacks.

As Graphene is only an engine to run GraphQL queries, it is not responsible for the HTTP layer, and this security must be handled by the web framework you are using. For example, if you are using Django-GraphQL, you may also want to check out the `Django documentation`_ on securing your API.

.. toctree::
   :maxdepth: 1

   maxdepth
   introspection
   customvalidation
   dast

.. _Django documentation: https://docs.djangoproject.com/en/4.1/topics/security/
