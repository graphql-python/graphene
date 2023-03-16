======================
Security consideration
======================

As GraphQL is a query language, it allows users to use a wider pannel of inputs than traditional REST APIs.
Due to this feature, GraphQL APIs are inherently prone to various security risks, but they can be reduced by taking
appropriate precautions. Neglecting them can expose the API to vulnerabilities like credential leakage or denial of
service attacks.

In this section, we will discuss the most common security risks and how to mitigate them.

.. toctree::
   :maxdepth: 2

   queryvalidation
