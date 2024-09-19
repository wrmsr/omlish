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
	${PYTHON} --version

	if [ "${VENV}" == "default" ] ; then \
		if [ ! -d .venv ] ; then \
			ln -s .venvs/default .venv ; \
		fi ; \
		if ! $$(${PYTHON} -c 'import tinygrad.tensor' 2>/dev/null) ; then \
			${MAKE} tg ; \
		fi ; \
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
	sed -i '' '/^-e git\+https:\/\/github.com\/tinygrad\/tinygrad/d' requirements-frz.txt

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
gen: gen-amalg gen-cmake gen-manifest gen-pkg

.PHONY: gen-amalg
gen-amalg: venv
	${PYTHON} -m omdev.amalg gen \
		-m omlish \
		-m omdev \
		${SRCS}

.PHONY: gen-cmake
gen-cmake:
	${PYTHON} -m omdev.cexts.cmake gen ${SRCS} x/dev/c

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
	if git rev-parse --verify HEAD >/dev/null 2>&1 ; then \
		against=HEAD ; \
	else \
		against=$$(git hash-object -t tree /dev/null) ; \
	fi

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
test-all: test test-13 test-lite

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
	LITE_PATHS=$$(${PYTHON} -m omdev.findmagic --py -x py -m '# @omlish-lite' ${SRCS}) ; \
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
	omlish-dev
#	omlish-dev-amd64

.PHONY: docker-rebuild
docker-rebuild: docker-stop
	${DOCKER_COMPOSE} rm -f
	${DOCKER_COMPOSE} build ${DOCKER_DEV_CONTAINERS}

.PHONY: docker-reup
docker-reup: docker-rebuild
	${DOCKER_COMPOSE} up --attach-dependencies ${DOCKER_DEV_CONTAINERS}

.PHONY: docker-invalidate
docker-invalidate:
	date +%s > docker/.timestamp

DOCKER_BASE_PORT=35220

.PHONY: docker-ports
docker-ports: venv
	${PYTHON} -m omdev.tools.dockertools reset_compose_ports -wq ${DOCKER_BASE_PORT}


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


### Package

.PHONY: package
package: venv clean-package
	PYTHONPATH=. ${PYTHON} ${PYPROJECT_SRC} pkg -b -r gen

.PHONY: test-install
test-install: venv
	for f in $$(find dist -name 'omlish-*') ; do \
		echo "Test installing $$f" ; \
		${PYTHON} -mpip install --dry-run "$$f" ; \
	done


### Publish

LOCAL_VERSION:=$$(${PYTHON} -c 'from omlish import __about__; print(__about__.__version__)')
PYPI_VERSION:=$$(${PYTHON} -m omdev.tools.piptools lookup_latest_version omlish)

.PHONY: versions
versions: venv
	echo "PyPI version: ${PYPI_VERSION}"
	echo "Local version: ${LOCAL_VERSION}"

.PHONY: publish
publish: gen package test-install
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
