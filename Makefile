.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@grep -E '^\.PHONY: [a-zA-Z_-]+ .*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: docs ## Generate docs
docs:
	cd docs && make install && make html

.PHONY: docs-live ## Generate docs with live reloading
docs-live:
	cd docs && make install && make livehtml
