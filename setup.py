from pathlib import Path

from setuptools import find_packages, setup

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
]

dev_requires = ["black==20.8b1", "flake8>=3.7,<4"] + tests_require

setup(
    name="graphene",
    description="GraphQL Framework for Python",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/graphql-python/graphene",
    author="Syrus Akbary",
    author_email="me@syrusakbary.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python ",
        "Programming Language :: Python :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="api graphql protocol rest relay graphene",
    packages=find_packages(exclude=["examples"]),
    install_requires=[
        "graphql-core>=3.1.2,<4",
        "graphql-relay>=3.0,<4",
        "aniso8601>=8,<9",
        "dataclasses>=0.8;python_version<'3.7'",
    ],
    use_scm_version={
        "write_to": "graphene/_version.py",
        "write_to_template": "__version__ = '{version}'\n",
    },
    setup_requires=["setuptools_scm", "wheel"],
    tests_require=tests_require,
    extras_require={"test": tests_require, "dev": dev_requires},
)
