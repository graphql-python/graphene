import sys

from setuptools import setup, find_packages
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
    version='0.1',

    description='Graphene: Python DSL for GraphQL',

    url='https://github.com/syrusakbary/graphene',

    author='Syrus Akbary',
    author_email='me@syrusakbary.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
    ],

    keywords='api graphql protocol rest relay graphene',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        'six',
        'blinker',
        'graphqllib',
        'graphql-relay'
    ],
    tests_require=['pytest>=2.7.2'],
    extras_require={
        'django': [
            'Django>=1.8.0,<1.9',
            'pytest-django',
            'singledispatch>=3.4.0.3',
        ],
    },

    cmdclass={'test': PyTest},
)
