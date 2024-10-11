SHELL:=/bin/bash

.PHONY: clean
clean:
	-rm -rf \
		.venvs*

pyproject.py:
	curl https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/scripts/pyproject.py > pyproject.py
	chmod a+x pyproject.py

VENV?=default
PYPROJECT_VENV:=./pyproject.py venv ${VENV}

PYTHON:=$$(${PYPROJECT_VENV} exe)
SOURCES:=$$(${PYPROJECT_VENV} srcs)

.PHONY: venv
venv: pyproject.py
	${PYTHON} --version

.PHONY: test
test: venv
	${PYPROJECT_VENV} test
