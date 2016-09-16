import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins

# This is a bit (!) hackish: we are setting a global variable so that the main
# graphql __init__ can detect if it is being loaded by the setup routine, to
# avoid attempting to load components that aren't built yet:
# the numpy distutils extensions that are used by scikit-learn to recursively
# build the compiled extensions in sub-packages is based on the Python import
# machinery.
builtins.__SETUP__ = True

version = __import__('graphene').get_version()


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
    version=version,

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
        'graphql-core>=1.0.dev',
        'graphql-relay>=0.4.4',
        'promise',
    ],
    tests_require=[
        'pytest>=2.7.2',
        'pytest-benchmark',
        'mock',
    ],
    extras_require={
        'django': [
            'graphene-django',
        ],
        'sqlalchemy': [
            'graphene-sqlalchemy',
        ]
    },
    cmdclass={'test': PyTest},
)
