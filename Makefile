SHELL:=/bin/bash

PROJECT:=omlish

PYTHON_VERSION_10:=3.10.12
PYTHON_VERSION_11:=3.11.4
PYTHON_VERSION_12:=3.12-dev
PYTHON_VERSION_NOGIL:=nogil-3.12

MAIN_SOURCES:=\
	${PROJECT} \
	nn \

ALL_SOURCES:=\
	${MAIN_SOURCES} \
	hn \
	x \


### Clean

.PHONY: clean
clean:
	-rm -rf ${PROJECT}.egg-info
	-rm -rf *.sock
	-rm -rf .mypy_cache
	-rm -rf .pytest_cache
	-rm -rf build
	-rm -rf dist

	-rm -rf .venv*


### Venv

DEFAULT_PYTHON_VERSION:=${PYTHON_VERSION_10}
DEFAULT_PYENV_INSTALL_OPTS:=
DEFAULT_PYENV_VERSION_SUFFIX:=
DEFAULT_VENV_OPTS:=  # --copies
DEFAULT_VENV_ROOT:=.venv
DEFAULT_REQUIREMENTS_TXT:=requirements-ext.txt

PYTHON_VERSION:=$$(echo "$${_PYTHON_VERSION:-${DEFAULT_PYTHON_VERSION}}")
VENV_OPTS:=$$(echo "$${_VENV_OPTS:-${DEFAULT_VENV_OPTS}}")
VENV_ROOT:=$$(echo "$${_VENV_ROOT:-${DEFAULT_VENV_ROOT}}")
REQUIREMENTS_TXT:=$$(echo "$${_REQUIREMENTS_TXT:-${DEFAULT_REQUIREMENTS_TXT}}")

PYTHON:=$$(echo "$(VENV_ROOT)/bin/python")

PYENV_ROOT:=$$(sh -c "if [ -z '$${PYENV_ROOT}' ] ; then echo '$${HOME}/.pyenv' ; else echo '$${PYENV_ROOT%/}' ; fi")
PYENV_BIN:=$$(sh -c "if [ -f '$${HOME}/.pyenv/bin/pyenv' ] ; then echo '$${HOME}/.pyenv/bin/pyenv' ; else echo pyenv ; fi")
PYENV_INSTALL_OPTS:=$$(echo "$${_PYENV_INSTALL_OPTS:-${DEFAULT_PYENV_INSTALL_OPTS}}")
PYENV_VERSION_SUFFIX:=$$(echo "$${_PYENV_VERSION_SUFFIX:-${DEFAULT_PYENV_VERSION_SUFFIX}}")

.PHONY: venv
venv:
	if [ ! -d $(VENV_ROOT) ] ; then \
		$(PYENV_BIN) install -s $(PYENV_INSTALL_OPTS) $(PYTHON_VERSION) && \
		"$(PYENV_ROOT)/versions/$(PYTHON_VERSION)$(PYENV_VERSION_SUFFIX)/bin/python" -mvenv $(VENV_OPTS) $(VENV_ROOT) && \
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
	$(PYTHON) -mflake8 ${MAIN_SOURCES}

.PHONY: mypy
mypy: venv
	$(PYTHON) -mmypy --check-untyped-defs ${MAIN_SOURCES}


### Test

DEFAULT_TEST_SOURCES:=${ALL_SOURCES}

TEST_SOURCES:=$$(echo "$${_TEST_SOURCES:-${DEFAULT_TEST_SOURCES}}")

.PHONY: test
test: venv
	$(PYTHON) -mpytest $(TEST_SOURCES)

.PHONY: test-11
test-11:
	_PYTHON_VERSION=${PYTHON_VERSION_11} _VENV_ROOT=.venv-11 \
	${MAKE} test

.PHONY: test-all
test-all: test test-11

#

.PHONY: test-debug
test-debug:
	_PYTHON_VERSION=${DEFAULT_PYTHON_VERSION} _VENV_ROOT=.venv-debug \
	_PYENV_INSTALL_OPTS=-g \
	_PYENV_VERSION_SUFFIX=-debug \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} test

.PHONY: test-12
test-12:
	_PYTHON_VERSION=${PYTHON_VERSION_12} _VENV_ROOT=.venv-12 \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} test

.PHONY: test-nogil
test-nogil:
	_PYTHON_VERSION=${PYTHON_VERSION_NOGIL} _VENV_ROOT=.venv-nogil \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} test
