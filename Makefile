.PHONY: qa quality test coverages coverage_report coverage_html pylint

quality:
	isort sopel_help
	flake8

test:
	coverage run -m pytest -v .

coverage_report:
	coverage report

coverage_html:
	coverage html

coverages: coverage_report coverage_html

pylint:
	pylint sopel_help

pyroma:
	pyroma .

qa: quality test coverages pylint pyroma

.PHONY: develop build

develop:
	pip install -U -r requirements.txt
	pip install -e .

build:
	rm -rf build/ dist/
	python -m build .
