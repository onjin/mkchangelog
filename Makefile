VERSION := $(shell curl -s https://pypi.org/simple/mkchangelog/ -H Accept:application/vnd.pypi.simple.v1+json|jq -r '.versions[-1]')
help:
	@echo ""
	@echo "  clean      to clear build and distribution directories"
	@echo "  package    to build a wheel and sdist"
	@echo "  release    to perform a release build, including deps, test, and package targets"
	@echo ""
	@echo "  test       to run all tests on the current python version"
	@echo "  test-all   to run all tests on all supported python versions"
	@echo "  lint       to run the lints"
	@echo "  ci         to run test and lints"
	@echo ""
	@echo "  help       to show this help message"
	@echo ""
	@echo "Most of these targets are just wrappers around hatch commands."
	@echo "See https://hatch.pypa.org for information to install hatch."


.PHONY: release
release: clean test package


.PHONY: clean
clean:
	hatch clean


.PHONY: package
package:
	hatch build


.PHONY: test
test:
	hatch run test
	hatch run coverage report -m --fail-under=100


.PHONY: test-all
test-all:
	hatch run test:test


.PHONY: lint
lint:
	hatch run lint
	hatch run format
	hatch run typecheck

.PHONY: docs
docs:
	hatch run mkdocs build

.PHONY: ci
ci: test lint

.PHONY: docker
docker:
	docker build --build-arg MKCHANGELOG_VERSION=v${VERSION} -t onjin/mkchangelog:v$(VERSION) .
	docker tag onjin/mkchangelog:v$(VERSION) onjin/mkchangelog:latest

.PHONY: docker-push
docker-push: docker
	docker push onjin/mkchangelog:v$(VERSION)
	docker push onjin/mkchangelog:latest
