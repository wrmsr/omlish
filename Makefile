SHELL:=/bin/bash

PROJECT:=omlish

MAIN_SOURCES:=\
	${PROJECT} \
	omdev \
	omml \

ALL_SOURCES:=\
	${MAIN_SOURCES} \
	omserv \
	x \


### Versions

define get-version
$$(grep '^$(1)=' .versions | cut -d= -f2)
endef

PYTHON_VERSION_11:=$(call get-version,'PYTHON_11')
PYTHON_VERSION_12:=$(call get-version,'PYTHON_12')
PYTHON_VERSION_13:=$(call get-version,'PYTHON_13')
PYTHON_VERSION_DEV:=$(call get-version,'PYTHON_DEV')


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

DEFAULT_PYTHON_VERSION:=${PYTHON_VERSION_11}
DEFAULT_PYENV_INSTALL_OPTS:=
DEFAULT_PYENV_VERSION_SUFFIX:=
DEFAULT_VENV_OPTS:=  # --copies
DEFAULT_VENV_ROOT:=.venv
DEFAULT_REQUIREMENTS_TXT:=requirements-ext.txt

PYTHON_VERSION:=$$(echo "$${_PYTHON_VERSION:-${DEFAULT_PYTHON_VERSION}}")
VENV_OPTS:=$$(echo "$${_VENV_OPTS:-${DEFAULT_VENV_OPTS}}")
VENV_ROOT:=$$(echo "$${_VENV_ROOT:-${DEFAULT_VENV_ROOT}}")
REQUIREMENTS_TXT:=$$(echo "$${_REQUIREMENTS_TXT:-${DEFAULT_REQUIREMENTS_TXT}}")

_PYTHONPATH=${PYTHONPATH}:.:external:tinygrad
DEFAULT_PYTHON_BIN:=$$(echo "$(VENV_ROOT)/bin/python")
PYTHON_BIN:=$$(echo "$${_PYTHON_BIN:-${DEFAULT_PYTHON_BIN}}")
PYTHON:=PYTHONPATH="$(_PYTHONPATH)" $(PYTHON_BIN)

PYENV_ROOT:=$$(sh -c "if [ -z '$${PYENV_ROOT}' ] ; then echo '$${HOME}/.pyenv' ; else echo '$${PYENV_ROOT%/}' ; fi")
PYENV_BIN:=$$(sh -c "if [ -f '$${HOME}/.pyenv/bin/pyenv' ] ; then echo '$${HOME}/.pyenv/bin/pyenv' ; else echo pyenv ; fi")
PYENV_INSTALL_OPTS:=$$(echo "$${_PYENV_INSTALL_OPTS:-${DEFAULT_PYENV_INSTALL_OPTS}}")
PYENV_VERSION_SUFFIX:=$$(echo "$${_PYENV_VERSION_SUFFIX:-${DEFAULT_PYENV_VERSION_SUFFIX}}")

.PHONY: _venv_
_venv_:
	$(PYENV_BIN) install -s $(PYENV_INSTALL_OPTS) $(PYTHON_VERSION)
	"$(PYENV_ROOT)/versions/$(PYTHON_VERSION)$(PYENV_VERSION_SUFFIX)/bin/python" -mvenv $(VENV_OPTS) $(VENV_ROOT)
	$(PYTHON) -mpip install --upgrade pip setuptools wheel
	$(PYTHON) -mpip install -r ${REQUIREMENTS_TXT}

.PHONY: _venv
_venv:
	if [ ! -d $(VENV_ROOT) ] ; then \
		${MAKE} _venv_ ; \
	fi

.PHONY: venv
venv:
	if [ ! -d $(VENV_ROOT) ] ; then \
		${MAKE} _venv_ tg ; \
	fi

.PHONY: tg
tg:
	export ABS_PYTHON=$$($(PYTHON) -c 'import sys; print(sys.executable)') && \
	(cd tinygrad && "$$ABS_PYTHON" -mpip install -e .)

.PHONY: tg-update
tg-update:
	(cd tinygrad && git pull origin master)

### Deps

.PHONY: dep-freze
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

DEFAULT_TEST_SOURCES:=${MAIN_SOURCES}

TEST_SOURCES:=$$(echo "$${_TEST_SOURCES:-${DEFAULT_TEST_SOURCES}}")

PYTEST_OPTS=
PYTEST_JUNIT_XML_PATH:=$$(echo "$${OMLISH_JUNIT_XML_PATH}")

.PHONY: _test
_test:
	if [ ! -z "$(PYTEST_JUNIT_XML_PATH)" ] && [ -f "$(PYTEST_JUNIT_XML_PATH)" ] ; then \
		rm "$(PYTEST_JUNIT_XML_PATH)" ; \
	fi

	$(PYTHON) -mpytest \
		$(PYTEST_OPTS) \
		--junitxml="$(PYTEST_JUNIT_XML_PATH)" \
		$(TEST_SOURCES) \
		--durations=5 --durations-min=1 \
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
	_TEST_SOURCES="${PROJECT}" \
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
	_TEST_SOURCES="${PROJECT}" \
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

.PHONY: docker-reup
docker-reup: docker-stop
	${DOCKER_COMPOSE} rm -f
	${DOCKER_COMPOSE} build omlish-dev
	${DOCKER_COMPOSE} up

.PHONY: docker-invalidate
docker-invalidate:
	date +%s > docker/.dockertimestamp

.PHONY: docker-enable-ptrace
docker-enable-ptrace:
	docker run --platform linux/x86_64 --privileged -it ubuntu sh -c 'echo 0 > /proc/sys/kernel/yama/ptrace_scope'


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
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} _test


### Utils

.PHONY: my-repl
my-repl: venv
	F=$$(mktemp) ; \
	echo -e "\n\
import yaml \n\
with open('docker/docker-compose.yml', 'r') as f: \n\
    dct = yaml.safe_load(f.read()) \n\
cfg = dct['services']['$(PROJECT)-mysql'] \n\
print('MY_USER=' + cfg['environment']['MYSQL_USER']) \n\
print('MY_PASSWORD=' + cfg['environment']['MYSQL_PASSWORD']) \n\
print('MY_PORT=' + cfg['ports'][0].split(':')[0]) \n\
" >> $$F ; \
	export $$(.venv/bin/python "$$F" | xargs) && \
	MYSQL_PWD="$$MY_PASSWORD" .venv/bin/mycli --user "$$MY_USER" --host localhost --port "$$MY_PORT"

.PHONY: pg-repl
pg-repl: venv
	F=$$(mktemp) ; \
	echo -e "\n\
import yaml \n\
with open('docker/docker-compose.yml', 'r') as f: \n\
    dct = yaml.safe_load(f.read()) \n\
cfg = dct['services']['$(PROJECT)-postgres'] \n\
print('PG_USER=' + cfg['environment']['POSTGRES_USER']) \n\
print('PG_PASSWORD=' + cfg['environment']['POSTGRES_PASSWORD']) \n\
print('PG_PORT=' + cfg['ports'][0].split(':')[0]) \n\
" >> $$F ; \
	export $$(.venv/bin/python "$$F" | xargs) && \
	PGPASSWORD="$$PG_PASSWORD" .venv/bin/pgcli --user "$$PG_USER" --host localhost --port "$$PG_PORT"

.PHONY: secret-pg-repl
secret-pg-repl: venv
	F=$$(mktemp) ; \
	echo -e "\n\
import yaml \n\
with open('secrets.yml', 'r') as f: \n\
    dct = yaml.safe_load(f.read()) \n\
print('PG_HOST=' + dct['postgres_host']) \n\
print('PG_USER=' + dct['postgres_user']) \n\
print('PG_PASSWORD=' + dct['postgres_pass']) \n\
" >> $$F ; \
	export $$(.venv/bin/python "$$F" | xargs) && \
	PGPASSWORD="$$PG_PASSWORD" .venv/bin/pgcli --user "$$PG_USER" --host "$$PG_HOST"
