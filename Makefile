.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@grep -E '^\.PHONY: [a-zA-Z_-]+ .*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: install-dev ## Install development dependencies
install-dev:
	pip install -e ".[dev]"

.PHONY: test ## Run tests
test:
	py.test graphene examples

.PHONY: docs ## Generate docs
docs: install-dev
	cd docs && make install && make html

.PHONY: docs-live ## Generate docs with live reloading
docs-live: install-dev
	cd docs && make install && make livehtml

.PHONY: format
format:
	black graphene examples setup.py

.PHONY: lint
lint:
	flake8 graphene examples setup.py
