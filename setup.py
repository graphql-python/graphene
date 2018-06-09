import ast
import re
import sys

from setuptools import find_packages, setup

_version_re = re.compile(r'VERSION\s+=\s+(.*)')

with open('graphene/__init__.py', 'rb') as f:
    version = ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))

path_copy = sys.path[:]

sys.path.append('graphene')
try:
    from pyutils.version import get_version
    version = get_version(version)
except Exception:
    version = ".".join([str(v) for v in version])

sys.path[:] = path_copy


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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords='api graphql protocol rest relay graphene',

    packages=find_packages(exclude=['tests', 'tests.*', 'examples']),

    install_requires=[
        'six>=1.10.0,<2',
        'graphql-core>=2.0,<3',
        'graphql-relay>=0.4.5,<1',
        'promise>=2.1,<3',
        'aniso8601>=3,<4',
    ],
    extras_require={
        'django': [
            'graphene-django',
        ],
        'sqlalchemy': [
            'graphene-sqlalchemy',
        ]
    },
)
