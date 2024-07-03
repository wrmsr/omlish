SHELL:=/bin/bash

PROJECT:=omlish

MAIN_SOURCES:=\
	${PROJECT} \
	omdev \
	omserv \

ML_SOURCES:=\
	${MAIN_SOURCES} \
	omml

ALL_SOURCES:=\
	${ML_SOURCES} \
	x \


### Clean

.PHONY: clean-venv
clean-venv:
	-rm -rf .venv*

.PHONY: _clean
_clean: clean-venv
	-rm -rf \
		${PROJECT}.egg-info \
		*.sock \
		.benchmarks \
		.mypy_cache \
		.pytest_cache \
		build \
		dist \


### Venv

PYPROJECT_PYTHON=python3
PYPROJECT=${PYPROJECT_PYTHON} omdev/scripts/pyproject.py

VENV?=default
PYPROJECT_VENV=${PYPROJECT} venv ${VENV}

PYTHON:=$$(${PYPROJECT_VENV} exe)

.PHONY: venv
venv:
	# FIXME: .venv-13/bin/python -c 'import tinygrad' -> ${MAKE} tg
	${PYTHON} --version

.PHONY: tg
tg:
	export ABS_PYTHON=$$($(PYTHON) -c 'import sys; print(sys.executable)') && \
	(cd tinygrad && "$$ABS_PYTHON" -mpip install -e .)

.PHONY: tg-update
tg-update:
	(cd tinygrad && git pull origin master)


### Deps

.PHONY: dep-freeze
dep-freeze: venv
	$(PYTHON) -mpip freeze > requirements-frz.txt
	sed -i '' '/^-e git\+https:\/\/github.com\/tinygrad\/tinygrad/d' requirements-frz.txt

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

.PHONY: new_test
new_test:
	if [ ! -z "${PYTEST_JUNIT_XML_PATH}" ] && [ -f "${PYTEST_JUNIT_XML_PATH}" ] ; then \
		rm "${PYTEST_JUNIT_XML_PATH}" ; \
	fi

	${PYPROJECT_VENV} \
		test \
		-- \
		${PYTEST_OPTS} \
		--junitxml="$(PYTEST_JUNIT_XML_PATH)" \
		--no-slow \

DEFAULT_TEST_SOURCES:=${MAIN_SOURCES}

TEST_SOURCES:=$$(echo "$${_TEST_SOURCES:-${DEFAULT_TEST_SOURCES}}")

PYTEST_OPTS=
PYTEST_JUNIT_XML_PATH:=$$(echo "$${OMLISH_JUNIT_XML_PATH}")

.PHONY: _test
_test:
	if [ ! -z "$(PYTEST_JUNIT_XML_PATH)" ] && [ -f "$(PYTEST_JUNIT_XML_PATH)" ] ; then \
		rm "$(PYTEST_JUNIT_XML_PATH)" ; \
	fi

	${PYTHON} -mpytest \
		$(PYTEST_OPTS) \
		--junitxml="$(PYTEST_JUNIT_XML_PATH)" \
		$(TEST_SOURCES) \
		--no-slow \

.PHONY: test
test: _venv _test


### Alts

# debug

.PHONY: venv-debug
venv-debug:
	_VENV_ROOT=.venv-debug \
	_PYTHON_VERSION=${DEFAULT_PYTHON_VERSION} \
	_PYENV_INSTALL_OPTS=-g \
	_PYENV_VERSION_SUFFIX=-debug \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} _venv

.PHONY: test-debug
test-debug: venv-debug
	_VENV_ROOT=.venv-debug \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} _venv _test

# 12

.PHONY: venv-12
venv-12:
	_VENV_ROOT=.venv-12 \
	_PYTHON_VERSION=${PYTHON_VERSION_12} \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} _venv

.PHONY: test-12
test-12: venv-12
	_VENV_ROOT=.venv-12 \
	_TEST_SOURCES="${MAIN_SOURCES}" \
	${MAKE} _venv _test

# 13

.PHONY: venv-13
venv-13:
	_VENV_ROOT=.venv-13 \
	_PYTHON_VERSION=${PYTHON_VERSION_13} \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} _venv

.PHONY: test-13
test-13: venv-13
	_VENV_ROOT=.venv-13 \
	_TEST_SOURCES="${MAIN_SOURCES}" \
	${MAKE} _venv _test

# dev

.PHONY: venv-dev
venv-dev:
	_VENV_ROOT=.venv-dev \
	_PYTHON_VERSION=${PYTHON_VERSION_DEV} \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} _venv

.PHONY: test-dev
test-dev: venv-dev
	_VENV_ROOT=.venv-dev \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} _venv _test

# docker

DOCKER_USER=wrmsr

.PHONY: venv-docker
venv-docker:
	./docker-dev make _venv-docker

.PHONY: _venv-docker
_venv-docker:
	if [ $$(arch) == "aarch64" ] ; then \
		export BERKELEYDB_LIBDIR=/usr/lib/aarch64-linux-gnu ; \
		export BERKELEYDB_INCDIR=/usr/include ; \
	fi && \
	\
	_VENV_ROOT=.venv-docker \
	${MAKE} _venv

.PHONY: test-docker
test-docker:
	./docker-dev make _test-docker

.PHONY: _test-docker
_test-docker: venv-docker
	_VENV_ROOT=.venv-docker \
	${MAKE} _venv _test


### Docker

DOCKER_COMPOSE=docker-compose -f docker/docker-compose.yml

.PHONY: docker-stop
docker-stop:
	${DOCKER_COMPOSE} stop

DOCKER_DEV_CONTAINERS=\
	omlish-dev

.PHONY: docker-reup
docker-reup: docker-stop
	${DOCKER_COMPOSE} rm -f
	${DOCKER_COMPOSE} build ${DOCKER_DEV_CONTAINERS}
	${DOCKER_COMPOSE} up --attach-dependencies ${DOCKER_DEV_CONTAINERS}

.PHONY: docker-invalidate
docker-invalidate:
	date +%s > docker/.dockertimestamp


### CI

.PHONY: ci-images
ci-images:
	tar cvh \
		--exclude "__pycache__" \
		${MAIN_SOURCES} \
		LICENSE \
		Makefile \
		docker \
		pyproject.toml \
		requirements-dev.txt \
		requirements.txt \
	| \
		docker build --platform linux/x86_64 --tag "$(DOCKER_USER)/omlish-ci" -f "docker/ci/Dockerfile" -

.PHONY: ci
ci: ci-images
	${DOCKER_COMPOSE} run --rm $$OMLISH_CI_DOCKER_OPTS omlish-ci

.PHONY: _ci
_ci:
	_PYTHON_BIN=python \
	_TEST_SOURCES="${MAIN_SOURCES}" \
	${MAKE} _test


### Utils

.PHONY: my-repl
my-repl: venv
	${PYTHON} -m omdev.tools.sqlrepl repl mysql docker/docker-compose.yml:omlish-mysql

.PHONY: pg-repl
pg-repl: venv
	${PYTHON} -m omdev.tools.sqlrepl repl postgres docker/docker-compose.yml:omlish-postgres

.PHONY: secret-pg-repl
secret-pg-repl: venv
	${PYTHON} -m omdev.tools.sqlrepl repl postgres secrets.yml:postgres
