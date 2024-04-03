SHELL:=/bin/bash

PROJECT:=omlish

MAIN_SOURCES:=\
	${PROJECT} \

ALL_SOURCES:=\
	${MAIN_SOURCES} \
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

.PHONY: clean
clean: clean-venv
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
		$(PYTHON) -mpip install -r ${REQUIREMENTS_TXT} && \
		export ABS_PYTHON=$$($(PYTHON) -c 'import sys; print(sys.executable)') && \
		(cd tinygrad && "$$ABS_PYTHON" -mpip install -e .) ; \
	fi

.PHONY: vx
vx:
	export ABS_PYTHON=$$($(PYTHON) -c 'import sys; print(sys.executable)') && \
	(cd tinygrad && "$$ABS_PYTHON" -mpip install -e .) ; \


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

DEFAULT_TEST_SOURCES:=${MAIN_SOURCES}

TEST_SOURCES:=$$(echo "$${_TEST_SOURCES:-${DEFAULT_TEST_SOURCES}}")

.PHONY: test
test: venv
	$(PYTHON) -mpytest $(TEST_SOURCES)


### Alts

# debug

.PHONY: venv-debug
venv-debug:
	_VENV_ROOT=.venv-debug \
	_PYTHON_VERSION=${DEFAULT_PYTHON_VERSION} \
	_PYENV_INSTALL_OPTS=-g \
	_PYENV_VERSION_SUFFIX=-debug \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} venv

.PHONY: test-debug
test-debug: venv-debug
	_VENV_ROOT=.venv-debug \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} test

# 12

.PHONY: venv-12
venv-12:
	_VENV_ROOT=.venv-12 \
	_PYTHON_VERSION=${PYTHON_VERSION_12} \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} venv

.PHONY: test-12
test-12: venv-12
	_VENV_ROOT=.venv-12 \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} test

# 13

.PHONY: venv-13
venv-13:
	_VENV_ROOT=.venv-13 \
	_PYTHON_VERSION=${PYTHON_VERSION_13} \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} venv

.PHONY: test-13
test-13: venv-13
	_VENV_ROOT=.venv-13 \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} test

# dev

.PHONY: venv-dev
venv-dev:
	_VENV_ROOT=.venv-dev \
	_PYTHON_VERSION=${PYTHON_VERSION_DEV} \
	_REQUIREMENTS_TXT=requirements-dev.txt \
	${MAKE} venv

.PHONY: test-dev
test-dev: venv-dev
	_VENV_ROOT=.venv-dev \
	_TEST_SOURCES="${PROJECT}" \
	${MAKE} test


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
