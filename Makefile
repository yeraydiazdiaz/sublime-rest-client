.PHONY: deps install-dev tests

install-dev:
	python -m pip install -U pip wheel setuptools
	python -m pip install -r requirements/dev.txt

upgrade-deps:
	rm -fr ./deps/**
	python -m pip install --upgrade --target "./deps" -r requirements/main.txt
