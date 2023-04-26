SHELL:=/bin/bash

PROJECT:=omlish

PYTHON_VERSION:=3.9.9

PYENV_ROOT:=$$(sh -c "if [ -z '$${PYENV_ROOT}' ] ; then echo '$${HOME}/.pyenv' ; else echo '$${PYENV_ROOT%/}' ; fi")
PYENV_BIN:=$$(sh -c "if [ -f '$${HOME}/.pyenv/bin/pyenv' ] ; then echo '$${HOME}/.pyenv/bin/pyenv' ; else echo pyenv ; fi")

REQUIREMENTS_TXT=requirements-dev.txt


### Clean

.PHONY: clean
clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf ${PROJECT}.egg-info


### Venv

PYTHON=.venv/bin/python

.PHONY: venv
venv:
	if [ ! -d .venv ] ; then \
		$(PYENV_BIN) install -s ${PYTHON_VERSION} && \
		"$(PYENV_ROOT)/versions/${PYTHON_VERSION}/bin/python" -mvenv .venv && \
		${PYTHON} -mpip install --upgrade pip setuptools wheel && \
		${PYTHON} -mpip install -r ${REQUIREMENTS_TXT} ; \
	fi


### Deps

.PHONY: dep-freze
dep-freeze: venv
	.venv/bin/pip freeze > requirements-frz.txt

.PHONY: dep-unfreeze
dep-unfreeze: venv
	.venv/bin/pip install -r requirements-frz.txt

.PHONY: dep-tree
dep-tree: venv
	.venv/bin/pipdeptree

.PHONY: dep-updates
dep-updates: venv
	.venv/bin/pip list -o --format=columns


### Check

.PHONY: check
check: flake8 mypy test

.PHONY: flake8
flake8:
	${PYTHON} -mflake8 ${PROJECT}

.PHONY: mypy
mypy:
	${PYTHON} -mmypy ${PROJECT}

.PHONY: test
test: venv
	${PYTHON} -mpytest ${PROJECT}
