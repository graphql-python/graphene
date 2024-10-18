Dynamic Application Security Testing
====================================

Continuous security testing
---------------------------

One of the best way to stop wondering about security for your API is to be able to scan it each time you deploy it into
staging or production environments. As you run your unit tests in your CI/CD pipeline, you can bullet-proof your GraphQL
application before it even reaches a production environment.

Security testing tools
----------------------

graphql.security
________________

`graphql.security`_ is a free, quick graphql security testing tool, allowing you to quickly assess the most common
vulnerabilities in your application.

Escape
______

`Escape`_ is a GraphQL security SaaS platform running an automated pentest tool.

You can effortlessly incorporate this platform into your current CI/CD pipeline such as Github Actions or Gitlab CIs
which makes it convenient to set up.

The security notifications will be automatically communicated to your CI/CD platform, enabling you to promptly attend to
them.

.. _graphql.security: https://graphql.security/
.. _Escape: https://escape.tech/
