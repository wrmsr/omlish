SHELL:=/bin/bash

PROJECT:=omlish

PYTHON_VERSION_9:=3.9.16
PYTHON_VERSION_10:=3.10.10
PYTHON_VERSION_11:=3.11.2
PYTHON_VERSION_12:=3.12-dev
PYTHON_VERSION_NOGIL:=nogil-3.9.10-1

REQUIREMENTS_TXT=requirements-dev.txt

SOURCES:=\
	${PROJECT} \
	nn \


### Clean

.PHONY: clean
clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf ${PROJECT}.egg-info

	-rm -rf .venv*


### Venv

DEFAULT_PYTHON_VERSION:=${PYTHON_VERSION_9}
DEFAULT_VENV_ROOT:=.venv

PYTHON_VERSION:=$$(echo "$${_PYTHON_VERSION:-${DEFAULT_PYTHON_VERSION}}")
VENV_ROOT:=$$(echo "$${_VENV_ROOT:-${DEFAULT_VENV_ROOT}}")

PYTHON:=$$(echo "$(VENV_ROOT)/bin/python")

PYENV_ROOT:=$$(sh -c "if [ -z '$${PYENV_ROOT}' ] ; then echo '$${HOME}/.pyenv' ; else echo '$${PYENV_ROOT%/}' ; fi")
PYENV_BIN:=$$(sh -c "if [ -f '$${HOME}/.pyenv/bin/pyenv' ] ; then echo '$${HOME}/.pyenv/bin/pyenv' ; else echo pyenv ; fi")

.PHONY: venv
venv:
	if [ ! -d $(VENV_ROOT) ] ; then \
		$(PYENV_BIN) install -s $(PYTHON_VERSION) && \
		"$(PYENV_ROOT)/versions/$(PYTHON_VERSION)/bin/python" -mvenv $(VENV_ROOT) && \
		$(PYTHON) -mpip install --upgrade pip setuptools wheel && \
		$(PYTHON) -mpip install -r ${REQUIREMENTS_TXT} ; \
	fi


### Deps

.PHONY: dep-freze
dep-freeze: venv
	$(PYTHON) -mpip freeze > requirements-frz.txt

.PHONY: dep-unfreeze
dep-unfreeze: venv
	$(PYTHON) -mpip install -r requirements-frz.txt

.PHONY: dep-tree
dep-tree: venv
	$(PYTHON) -mpipdeptree

.PHONY: dep-updates
dep-updates: venv
	$(PYTHON) -mpip list -o --format=columns


### Check

.PHONY: check
check: flake8 mypy

.PHONY: flake8
flake8: venv
	$(PYTHON) -mflake8 ${SOURCES}

.PHONY: mypy
mypy: venv
	$(PYTHON) -mmypy --check-untyped-defs ${SOURCES}

.PHONY: test
test: venv
	$(PYTHON) -mpytest ${SOURCES}

.PHONY: test-all
test-all: test test-10 test-11 test-nogil

.PHONY: test-10
test-10:
	_PYTHON_VERSION=${PYTHON_VERSION_10} _VENV_ROOT=.venv-10 ${MAKE} test

.PHONY: test-11
test-11:
	_PYTHON_VERSION=${PYTHON_VERSION_11} _VENV_ROOT=.venv-11 ${MAKE} test

.PHONY: test-12
test-12:
	_PYTHON_VERSION=${PYTHON_VERSION_12} _VENV_ROOT=.venv-12 ${MAKE} test

.PHONY: test-nogil
test-nogil:
	_PYTHON_VERSION=${PYTHON_VERSION_NOGIL} _VENV_ROOT=.venv-nogil ${MAKE} test


###

.PHONY: barf
barf: