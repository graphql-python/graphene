# Contributing

## Set up

After cloning this repo, create a [virtualenv](https://virtualenv.pypa.io/en/stable/) and ensure dependencies are installed by running:

```sh
virtualenv venv
source venv/bin/activate
make dev-setup
git checkout -B YOUR_BRANCH_NAME
```

You are not ready to start developing

## Testing

Well-written tests and maintaining good test coverage is important to this project. While developing, run new and existing tests with:

```sh
py.test graphene/relay/tests/test_node.py # Single file
make tests # All tests
```

Add the `-s` flag if you have introduced breakpoints into the code for debugging.
Add the `-v` ("verbose") flag to get more detailed test output. For even more detailed output, use `-vv`.
Check out the [pytest documentation](https://docs.pytest.org/en/latest/) for more options and test running controls.

You can also run the benchmarks with:

```sh
make test-benchmarks
```

Graphene supports several versions of Python. To make sure that changes do not break compatibility with any of those versions, we use `tox` to create virtualenvs for each python version and run tests with that version. To run against all python versions defined in the `tox.ini` config file, just run:

```sh
tox
```

If you wish to run against a specific version defined in the `tox.ini` file:

```sh
tox -e py36
```

Tox can only use whatever versions of python are installed on your system. When you create a pull request, Travis will also be running the same tests and report the results, so there is no need for potential contributors to try to install every single version of python on their own system ahead of time. We appreciate opening issues and pull requests to make graphene even more stable & useful!

## Building Documentation

The documentation is generated using the excellent [Sphinx](http://www.sphinx-doc.org/) and a custom theme.

An HTML version of the documentation is produced by running:

```sh
make docs
```
