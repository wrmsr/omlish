SHELL:=/bin/bash


### Clean

.PHONY: clean-venv
clean-venv:
	-rm -rf \
		.venv*

.PHONY: clean-package
clean-package:
	-rm -rf \
		*.egg-info \
		build \
		dist \

.PHONY: _clean
_clean: clean-venv clean-package
	-rm -rf \
		*.sock \
		.benchmarks \
		.mypy_cache \
		.pytest_cache \


### Venv

PYPROJECT_PYTHON=python3
PYPROJECT=${PYPROJECT_PYTHON} omdev/scripts/pyproject.py

VENV?=default
PYPROJECT_VENV=${PYPROJECT} venv ${VENV}

PYTHON:=$$(${PYPROJECT_VENV} exe)
SRCS:=$$(${PYPROJECT_VENV} srcs)

.PHONY: python
python:
	@echo "${PYTHON}"

.PHONY: srcs
srcs:
	@echo ${SRCS}

#

.PHONY: venv
venv:
	${PYTHON} --version

	if [ "${VENV}" == "default" ] && ! $$(${PYTHON} -c 'import tinygrad.tensor') ; then \
		${MAKE} tg ; \
	fi

.PHONY: tg
tg:
	ABS_PYTHON=$$(${PYTHON} -c 'import sys; print(sys.executable)') && \
	(cd tinygrad && "$$ABS_PYTHON" -mpip install -e .)

.PHONY: tg-update
tg-update:
	(cd tinygrad && git pull origin master)


### Deps

.PHONY: dep-list
dep-list:
	@${PYTHON} -mpip freeze

.PHONY: dep-freeze
dep-freeze: venv
	${PYTHON} -mpip freeze > requirements-frz.txt
	sed -i '' '/^-e git\+https:\/\/github.com\/tinygrad\/tinygrad/d' requirements-frz.txt

.PHONY: dep-unfreeze
dep-unfreeze: venv
	${PYTHON} -mpip install -r requirements-frz.txt

.PHONY: dep-tree
dep-tree:
	@${PYTHON} -mpipdeptree

.PHONY: dep-updates
dep-updates: venv
	${PYTHON} -mpip list -o --format=columns


### Check

.PHONY: check
check: flake8 mypy check-scripts

.PHONY: flake8
flake8: venv
	${PYTHON} -mflake8 ${SRCS}

.PHONY: ruff
ruff: venv
	${PYTHON} -mruff check ${SRCS}

.PHONY: ruff-stats
ruff-stats: venv
	${PYTHON} -mruff check --statistics ${SRCS}

.PHONY: ruff-fix
ruff-fix: venv
	if ! $$(git diff-index --quiet HEAD --) ; then \
		echo 'there are uncommitted changes - refusing to run' ; \
		exit 1 ; \
	fi
	${PYTHON} -mruff check --fix ${SRCS}

.PHONY: mypy
mypy: venv
	${PYTHON} -mmypy --check-untyped-defs ${SRCS}

.PHONY: check-scripts
check-scripts: venv
	SCRIPT_IMPORTS=$$(find omdev/scripts -maxdepth 1 -name '*.py' -print0 | xargs -0 ${PYTHON} -m omdev.scripts.findimports) ; \
	if [ ! -z "$$SCRIPT_IMPORTS" ] ; then \
		echo "script imports found: $$SCRIPT_IMPORTS" ; \
		exit 1 ; \
	fi


### Test

PYTEST_OPTS=
PYTEST_JUNIT_XML_PATH:=$$(echo "$${OMLISH_JUNIT_XML_PATH}")

.PHONY: test
test:
	if [ ! -z "${PYTEST_JUNIT_XML_PATH}" ] && [ -f "${PYTEST_JUNIT_XML_PATH}" ] ; then \
		rm "${PYTEST_JUNIT_XML_PATH}" ; \
	fi

	${PYPROJECT_VENV} \
		test \
		-- \
		${PYTEST_OPTS} \
		--junitxml="${PYTEST_JUNIT_XML_PATH}" \
		--no-slow \


### Alts

# all
.PHONY: venv-all
venv-all: venv venv-13 venv-13t venv-8 venv-docker

# 13

.PHONY: venv-13
venv-13:
	${PYPROJECT} venv 13 exe

.PHONY: test-13
test-13:
	${PYPROJECT} venv 13 test -- ${PYTEST_OPTS} --ignore=omlish/sql

# 13t

.PHONY: venv-13t
venv-13t:
	${PYPROJECT} venv 13t exe

.PHONY: test-13t
test-13t:
	${PYPROJECT} venv 13t test -- ${PYTEST_OPTS} --ignore=omlish/sql

# 8

.PHONY: venv-8
venv-8:
	${PYPROJECT} venv 8 exe

# docker

.PHONY: venv-docker
venv-docker:
	if [ $$(arch) == "aarch64" ] || [ $$(arch) == "arm64" ]; then \
		export BERKELEYDB_LIBDIR=/usr/lib/aarch64-linux-gnu ; \
		export BERKELEYDB_INCDIR=/usr/include ; \
		PYPROJECT_DOCKER_ENVS="-e BERKELEYDB_LIBDIR -e BERKELEYDB_INCDIR" ; \
	fi ; \
	\
	${PYPROJECT} venv $$PYPROJECT_DOCKER_ENVS docker

.PHONY: test-docker
test-docker:
	VENV=docker ${MAKE} test

# docker-amd64

.PHONY: venv-docker-amd64
venv-docker-amd64:
	# VENV=docker-amd64 ${MAKE} venv  # FIXME
	${PYPROJECT} venv docker-amd64

.PHONY: test-docker-amd64
test-docker-amd64:
	VENV=docker-amd64 ${MAKE} test

# deploy

.PHONY: venv-deploy
venv-deploy:
	VENV=deploy ${MAKE} venv

# debug

.PHONY: venv-debug
venv-debug:
	VENV=debug ${MAKE} venv

.PHONY: test-debug
test-debug:
	VENV=debug ${MAKE} test


### Docker

DOCKER_USER=wrmsr

DOCKER_COMPOSE=docker-compose -f docker/docker-compose.yml

.PHONY: docker-stop
docker-stop:
	${DOCKER_COMPOSE} stop

DOCKER_DEV_CONTAINERS=\
	omlish-dev \
	omlish-dev-amd64

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
		${SRCS} \
		LICENSE \
		Makefile \
		docker \
		pyproject.toml \
		requirements-dev.txt \
		requirements.txt \
	| \
		docker build \
			--platform linux/x86_64 \
			--tag "${DOCKER_USER}/omlish-ci" \
			-f "docker/ci/Dockerfile" \
			-

.PHONY: ci
ci: ci-images
	${DOCKER_COMPOSE} run --rm $$OMLISH_CI_DOCKER_OPTS omlish-ci

.PHONY: _ci
_ci:
	python -mpytest omlish omdev omserv


### Package

.PYTHON: package
package: clean-package
	${PYTHON} -mbuild


### Publish

.PHONY: publish
publish: package
	read -p "Press enter to publish"
	.venv/bin/twine upload dist/*


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
