.PHONY: qa quality test coverages coverage_report coverage_html pylint

quality:
	isort -rc sopel_help
	flake8

test:
	coverage run -m py.test -v .

coverage_report:
	coverage report

coverage_html:
	coverage html

coverages: coverage_report coverage_html

pylint:
	pylint sopel_help

qa: quality test coverages pylint

.PHONY: develop

develop:
	pip install -r requirements.txt
	python setup.py develop
