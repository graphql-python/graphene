from setuptools import find_packages, setup

setup(
    name='graphene-django',
    version='1.0.dev20160910000001',

    description='Graphene Django integration',
    # long_description=open('README.rst').read(),

    url='https://github.com/graphql-python/graphene-django',

    author='Syrus Akbary',
    author_email='me@syrusakbary.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords='api graphql protocol rest relay graphene',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        'six>=1.10.0',
        'graphene>=1.0.dev',
        'Django>=1.6.0',
        'iso8601',
        'singledispatch>=3.4.0.3',
        'graphql-django-view>=1.3',
    ],
    tests_require=[
        'django-filter>=0.10.0',
        'pytest>=2.7.2',
        'pytest-django',
        'mock',
        # Required for Django postgres fields testing
        'psycopg2',
    ],
)
