REBUILD_FLAG =

.PHONY: all
all: venv test

.PHONY: venv
venv: .venv.touch install-hooks
	tox -e venv $(REBUILD_FLAG)

.PHONY: tests test
tests: test
test: .venv.touch install-hooks
	tox $(REBUILD_FLAG)

.venv.touch: setup.py requirements-dev.txt
	$(eval REBUILD_FLAG := --recreate)
	touch .venv.touch

.PHONY: install-hooks
install-hooks:
	tox -e pre-commit -- install -f --install-hooks

.PHONY: clean
clean:
	find . -iname '*.pyc' -delete
	rm -rf .tox
	rm -rf ./venv-*
	rm -f .venv.touch
