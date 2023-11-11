# Linters (check, style, and type in the future)
.PHONY: lint-check lint-style

lint-check:
	isort sopel_help
	flake8

lint-style:
	pylint sopel_help
	pyroma .

lint: lint-check lint-style

# Tests (tests and coverage reports)
.PHONY: test coverage_report coverage_html coverages

test:
	coverage run -m pytest -v .

coverage_report:
	coverage report

coverage_html:
	coverage html

coverages: coverage_report coverage_html

# Development cycle (local install, qa, build, and release on PyPI)
.PHONY: develop qa build

develop:
	pip install -U -r requirements.txt
	pip install -e .

qa: lint-check test coverages lint-style

build:
	rm -rf build/ dist/
	python -m build .

release:
	twine upload -r sopel-help dist/*
