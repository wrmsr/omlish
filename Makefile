# TODO:
# - build-deps:
#  - --force-reinstall --ignore-installed ?
#  - PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig" ./python -muv pip install mysqlclient
#  - BERKELEYDB_DIR=$(brew --prefix "berkeley-db@4") ./python -muv pip install bsddb

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

PYPROJECT_SRC=omdev/scripts/pyproject.py
PYPROJECT_PYTHON=python3
PYPROJECT=${PYPROJECT_PYTHON} ${PYPROJECT_SRC}

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
	@${PYTHON} --version

	@if [ "${VENV}" == "default" ] ; then \
		${MAKE} _default_venv ; \
	fi

.PHONY: _default_venv
_default_venv:
	@if [ ! -d .venv ] ; then \
		ln -s .venvs/default .venv ; \
	fi

	@.venv/bin/python3 -m omlish.diag._pycharm.runhack install -e || true

	@if ! ${PYTHON} -c 'import importlib.util; exit(importlib.util.find_spec("llama_cpp") is None)' ; then \
		if [ $$(uname) == "Linux" ] && [ $$(uname -m) == "x86_64" ] ; then \
			LCW=$$(ls -1 ../llama_cpp_python-*-linux_x86_64.whl 2>/dev/null | tail -n1) && \
			if [ ! -z "$$LCW" ] ; then \
				${PYTHON} -m pip install "$$LCW" ; \
			fi ; \
		fi ; \
	fi

	@if ! ${PYTHON} -c 'import importlib.util; exit(importlib.util.find_spec("tinygrad.tensor") is None)' ; then \
		${MAKE} tg ; \
	fi

.PHONY: fresh-venv
fresh-venv:
	rm -rf .venvs/default
	${MAKE} venv

.PHONY: tg
tg:
	git submodule update --init tinygrad

	# FIXME: ${PYTHON} -m pip install -e tinygrad --use-pep517
	ABS_PYTHON=$$(${PYTHON} -c 'import sys; print(sys.executable)') && \
	(cd tinygrad && "$$ABS_PYTHON" -m pip install -e .)

.PHONY: tg-update
tg-update:
	(cd tinygrad && git pull origin master)


### Deps

.PHONY: dep-list
dep-list:
	@${PYTHON} -m pip freeze

.PHONY: dep-freeze
dep-freeze: venv
	${PYTHON} -m pip freeze > requirements-frz.txt
	${PYTHON} -m omdev.tools.pip filter-dev-deps -wq requirements-frz.txt

.PHONY: dep-unfreeze
dep-unfreeze: venv
	${PYTHON} -m pip install -r requirements-frz.txt

.PHONY: dep-tree
dep-tree:
	@${PYTHON} -m pipdeptree

.PHONY: dep-updates
dep-updates: venv
	${PYTHON} -m pip list -o --format=columns

.PHONY: dep-refresh
dep-refresh: venv
	${PYTHON} -m pip install --upgrade pip setuptools wheel
	${PYTHON} -m pip install -r requirements-ext.txt


### Gen

.PHONY: gen
gen: gen-amalg gen-cmake gen-aws gen-manifest gen-pkg

.PHONY: gen-amalg
gen-amalg: venv
	${PYTHON} -m omdev.amalg gen \
		-m omdev \
		-m ominfra \
		-m omlish \
		-m omserv \
		${SRCS}

.PHONY: gen-cmake
gen-cmake:
	${PYTHON} -m omdev.cexts.cmake gen ${SRCS}

.PHONY: gen-aws
gen-aws:
	${PYTHON} -m ominfra.clouds.aws.models.gen gen-services

.PHONY: gen-manifest
gen-manifest:
	${PYTHON} -m omdev.manifests gen -wq ${SRCS} x

.PHONY: gen-pkg
gen-pkg:
	PYTHONPATH=. ${PYPROJECT} pkg gen


### Check

.PHONY: check
check: flake8 ruff mypy precheck

.PHONY: flake8
flake8: venv
	${PYTHON} -m flake8 ${SRCS}

.PHONY: ruff
ruff: venv
	${PYTHON} -m ruff check ${SRCS}

.PHONY: ruff-stats
ruff-stats: venv
	${PYTHON} -m ruff check --statistics ${SRCS}

.PHONY: ruff-fix
ruff-fix: venv
	if ! $$(git diff-files --quiet --ignore-submodules) ; then \
		echo 'there are unstaged changes - refusing to run' ; \
		exit 1 ; \
	fi
	${PYTHON} -m ruff check --fix ${SRCS}

.PHONY: fix-imports
fix-imports: venv
	${PYTHON} -m ruff check --select I001 --fix ${SRCS}

.PHONY: mypy
mypy: venv
	${PYTHON} -m mypy --check-untyped-defs ${SRCS}

.PHONY: precheck
precheck: venv
	${PYTHON} -m omdev.precheck check ${SRCS}


## pre-commit

# FIXME: update .git/hooks/pre-commit to use *just* git-ish omdev.precheck's

GIT_BLACKLIST_FILES=\
	.env \
	secrets.yml \

.PHONY: pre-commit
pre-commit:
	for F in ${GIT_BLACKLIST_FILES} ; do \
		ST=$$(git status -s "$$F") ; \
		if [ ! -z "$$ST" ] ; then \
			echo "must not checkin $$F" ; \
			exit 1 ; \
		fi ; \
	done


### Test

PYTEST_OPTS=

.PHONY: test-all
test-all: test test-docker test-13 test-13t test-lite

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
venv-all: venv venv-13 venv-13t venv-lite

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

# 14

.PHONY: venv-14
venv-14:
	${PYPROJECT} venv 14 exe

.PHONY: test-14
test-14:
	${PYPROJECT} venv 14 test -- ${PYTEST_OPTS} --ignore=omlish/sql

# 14t

.PHONY: venv-14t
venv-14t:
	${PYPROJECT} venv 14t exe

.PHONY: test-14t
test-14t:
	${PYPROJECT} venv 14t test -- ${PYTEST_OPTS} --ignore=omlish/sql

# lite

LITE_VENVS=\
	8 \
	9 \
	10 \
	11 \

.PHONY: venv-lite
venv-lite:
	for V in ${LITE_VENVS} ; do \
		${PYPROJECT} venv $$V exe ; \
	done

.PHONY: test-lite
test-lite:
	LITE_PATHS=$$(${PYTHON} -m omdev.magic find --modules -k '@omlish-lite' ${SRCS}) ; \
	for V in ${LITE_VENVS} ; do \
  		for T in $$LITE_PATHS ; do \
			if [ -d $$(echo "$$T" | tr '.' '/') ] ; then \
				$$(${PYPROJECT} venv $$V exe) -m unittest discover -vb $$T ; \
			else \
				$$(${PYPROJECT} venv $$V exe) -m unittest -vb $$T ; \
			fi ; \
		done ; \
	done

# docker

.PHONY: venv-docker
venv-docker:
	# FIXME: do this everywhere, even on darwin:
	# BERKELEYDB_DIR=$(brew --prefix 'berkeley-db@4') .venv/bin/pip install bsddb3
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

DOCKER_COMPOSE=docker compose -f docker/compose.yml

.PHONY: docker-stop
docker-stop:
	${DOCKER_COMPOSE} stop

DOCKER_DEV_CONTAINERS=\
	omlish-dev \
	# omlish-dev-amd64 \

DOCKER_LITE_CONTAINERS=\
	omlish-mysql \
	omlish-postgres \

.PHONY: docker-rebuild
docker-rebuild: docker-stop
	${DOCKER_COMPOSE} rm -f
	${DOCKER_COMPOSE} build ${DOCKER_DEV_CONTAINERS}

.PHONY: docker-reup
docker-reup: docker-rebuild
	${DOCKER_COMPOSE} up --attach-dependencies ${DOCKER_DEV_CONTAINERS}

.PHONY: docker-reup-lite
docker-reup-lite: docker-rebuild
	${DOCKER_COMPOSE} up --attach-dependencies ${DOCKER_LITE_CONTAINERS}

.PHONY: docker-invalidate
docker-invalidate:
	date +%s > docker/.timestamp

DOCKER_BASE_PORT=35220

.PHONY: docker-ports
docker-ports: venv
	${PYTHON} -m omdev.tools.docker reset-compose-ports -wq ${DOCKER_BASE_PORT}

.PHONY: docker-updates
docker-updates: venv
	${PYTHON} -m omdev.tools.docker compose-image-updates


### CI

CI_BASE_FILES=\
	docker \

.PHONY: ci-image
ci-image:
	tar ch \
		${CI_BASE_FILES} \
	| \
		docker build \
			--platform linux/x86_64 \
			--tag "${DOCKER_USER}/omlish-ci-base" \
			-f "docker/ci/Dockerfile" \
			--target omlish-ci-base \
			-

	tar ch \
		--exclude "__pycache__" \
		${CI_BASE_FILES} \
		${SRCS} \
		.versions \
		LICENSE \
		Makefile \
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
ci: ci-image
	${DOCKER_COMPOSE} run --quiet-pull --rm $$CI_DOCKER_OPTS -e CI=1 omlish-ci

.PHONY: _ci
_ci:
	if [ ! -z "${PYTEST_JUNIT_XML_PATH}" ] && [ -f "${PYTEST_JUNIT_XML_PATH}" ] ; then \
		rm "${PYTEST_JUNIT_XML_PATH}" ; \
	fi

	python \
		-m pytest \
		${PYTEST_OPTS} \
		--junitxml="${PYTEST_JUNIT_XML_PATH}" \
		${SRCS}

.PHONY: ci-bash
ci-bash: ci-image
	${DOCKER_COMPOSE} run --rm -e CI=1 omlish-ci bash


### CI2


.PHONY: ci2
ci2:
	${PYTHON} omdev/scripts/ci.py run \
		--cache-dir ~/.cache/omlish/ci \
		. \
		omlish-ci \
		-- \
	\
	python3 \
		-m pytest \
		${PYTEST_OPTS} \
		--junitxml="${PYTEST_JUNIT_XML_PATH}" \
		${SRCS}


### Package

.PHONY: package
package: gen check clean-package
	PYTHONPATH=. ${PYTHON} ${PYPROJECT_SRC} pkg -b -r gen

.PHONY: test-install
test-install: venv
	for EXT in '.tar.gz' '.whl' ; do \
		D=$$(mktemp -d) ; \
		echo "$$D" ; \
		${PYTHON} -m venv "$$D/venv" ; \
		find dist -name "*$$EXT" | xargs "$$D/venv/bin/python3" -m pip install --no-cache-dir || exit 1 ; \
		rm -rf "$$D" ; \
	done


### Publish

LOCAL_VERSION:=$$(${PYTHON} -c 'from omlish import __about__; print(__about__.__version__)')
PYPI_VERSION:=$$(${PYTHON} -m omdev.tools.pip lookup-latest-version omlish)

.PHONY: versions
versions: venv
	echo "PyPI version: ${PYPI_VERSION}"
	echo "Local version: ${LOCAL_VERSION}"

.PHONY: publish
publish: package test-install
	ls -al dist/*

	if [[ $$(git status --porcelain=v1 2>/dev/null) ]] ; then \
		echo 'Uncommitted changes' ; \
		exit 1 ; \
	fi

	${MAKE} versions
	read -p "Press enter to publish"

	${PYTHON} -m twine upload dist/*

	# FIXME: enable *after* nuking big files from history
	# git tag -a "v${LOCAL_VERSION}" -m "v${LOCAL_VERSION}"

	${PYTHON} -m omdev.scripts.bumpversion -w omlish/__about__.py
	${MAKE} gen


### Utils

.PHONY: my-repl
my-repl: venv
	${PYTHON} -m omdev.tools.sqlrepl repl mysql docker/compose.yml:omlish-mysql

.PHONY: pg-repl
pg-repl: venv
	${PYTHON} -m omdev.tools.sqlrepl repl postgres docker/compose.yml:omlish-postgres

.PHONY: secret-pg-repl
secret-pg-repl: venv
	${PYTHON} -m omdev.tools.sqlrepl repl postgres ~/Dropbox/.dotfiles/secrets.yml:postgres
