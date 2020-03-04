import ast
import codecs
import re
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

_version_re = re.compile(r"VERSION\s+=\s+(.*)")

with open("graphene/__init__.py", "rb") as f:
    version = ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))

path_copy = sys.path[:]

sys.path.append("graphene")
try:
    from pyutils.version import get_version

    version = get_version(version)
except Exception:
    version = ".".join([str(v) for v in version])

sys.path[:] = path_copy


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

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


tests_require = [
    "pytest>=5.3,<6",
    "pytest-benchmark>=3.2,<4",
    "pytest-cov>=2.8,<3",
    "pytest-mock>=2,<3",
    "pytest-asyncio>=0.10,<2",
    "snapshottest>=0.5,<1",
    "coveralls>=1.11,<2",
    "promise>=2.3,<3",
    "mock>=4.0,<5",
    "pytz==2019.3",
    "iso8601>=0.1,<2",
]

dev_requires = ["black==19.10b0", "flake8>=3.7,<4"] + tests_require

setup(
    name="graphene",
    version=version,
    description="GraphQL Framework for Python",
    long_description=codecs.open(
        "README.rst", "r", encoding="ascii", errors="replace"
    ).read(),
    url="https://github.com/graphql-python/graphene",
    author="Syrus Akbary",
    author_email="me@syrusakbary.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="api graphql protocol rest relay graphene",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    install_requires=[
        "graphql-core>=3.1.0b1,<4",
        "graphql-relay>=3.0,<4",
        "aniso8601>=8,<9",
        "unidecode>=1.1.1,<2",
    ],
    tests_require=tests_require,
    extras_require={"test": tests_require, "dev": dev_requires},
    cmdclass={"test": PyTest},
)
