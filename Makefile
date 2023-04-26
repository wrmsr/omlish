SHELL:=/bin/bash

PROJECT:=omlish

DEFAULT_PYTHON_VERSION:=3.9.16

REQUIREMENTS_TXT=requirements-dev.txt


### Clean

.PHONY: clean
clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf ${PROJECT}.egg-info

	-rm -rf .venv*


### Venv

VENV:=$$(if [ "$$_VENV" ] ; then echo "$$_VENV" ; else echo .venv ; fi)
PYTHON_VERSION:=$$(if [ "$$_PYTHON_VERSION" ] ; then echo "$$_PYTHON_VERSION" ; else echo ${DEFAULT_PYTHON_VERSION} ; fi)

PYTHON:=$$(echo "$(VENV)/bin/python")

PYENV_ROOT:=$$(sh -c "if [ -z '$${PYENV_ROOT}' ] ; then echo '$${HOME}/.pyenv' ; else echo '$${PYENV_ROOT%/}' ; fi")
PYENV_BIN:=$$(sh -c "if [ -f '$${HOME}/.pyenv/bin/pyenv' ] ; then echo '$${HOME}/.pyenv/bin/pyenv' ; else echo pyenv ; fi")

.PHONY: venv
venv:
	if [ ! -d $(VENV) ] ; then \
		$(PYENV_BIN) install -s $(PYTHON_VERSION) && \
		"$(PYENV_ROOT)/versions/$(PYTHON_VERSION)/bin/python" -mvenv $(VENV) && \
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
check: flake8 mypy test

.PHONY: flake8
flake8: venv
	$(PYTHON) -mflake8 ${PROJECT}

.PHONY: mypy
mypy: venv
	$(PYTHON) -mmypy ${PROJECT}

.PHONY: test
test: venv
	$(PYTHON) -mpytest ${PROJECT}


###

.PHONY: barf
barf: