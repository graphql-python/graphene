.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@grep -E '^\.PHONY: [a-zA-Z_-]+ .*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: docs ## Generate docs
docs:
	@cd docs &&\
	pip install -r requirements.txt &&\
	make html &&\
	cd -

dev-setup:
	pip install -e ".[test]"

tests:
	py.test graphene

test-benchmarks:
	py.test graphene --benchmark-only