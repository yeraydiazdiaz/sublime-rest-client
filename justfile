install-dev:
	python -m pip install -U pip wheel setuptools
	python -m pip install -r requirements/dev.txt
	pre-commit install

upgrade-deps:
	rm -fr ./deps/**
	python -m pip install --upgrade --target "./deps" -r requirements/main.txt

lint:
	black --check plugin.py rest_client tests
	flake8 plugin.py rest_client tests
	mypy .

test:
	coverage run -m pytest
	coverage report -m
