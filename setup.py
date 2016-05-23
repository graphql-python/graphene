import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='graphene',
    version='0.10.1',

    description='GraphQL Framework for Python',
    long_description=open('README.rst').read(),

    url='https://github.com/graphql-python/graphene',

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
        'graphql-core>=0.5.1',
        'graphql-relay>=0.4.2',
        'iso8601',
    ],
    tests_require=[
        'django-filter>=0.10.0',
        'pytest>=2.7.2',
        'pytest-django',
        'sqlalchemy',
        'sqlalchemy_utils',
        'mock',
        # Required for Django postgres fields testing
        'psycopg2',
    ],
    extras_require={
        'django': [
            'Django>=1.6.0',
            'singledispatch>=3.4.0.3',
            'graphql-django-view>=1.3',
        ],
        'sqlalchemy': [
            'sqlalchemy',
            'singledispatch>=3.4.0.3',
        ]
    },

    cmdclass={'test': PyTest},
)
