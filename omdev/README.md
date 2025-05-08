# Overview

Development utilities and support code.

# Notable packages

- **[cli](cli)** - The codebase's all-in-one CLI. This is not installed as an entrypoint / command when this package is
  itself installed - that is separated into the `omdev-cli` installable package so as to not pollute users' bin/
  directories when depping this lib for its utility code.

- **[amalg](amalg)** - The [amalgamator](#amalgamation).

- **[pyproject](pyproject)** ([amalg](scripts/pyproject.py)) - python project management tool. wrangles but does not
  replace tools like venv, pip, setuptools, and uv. this should grow to eat more and more of the Makefile.

- **[ci](ci)** ([amalg](scripts/ci.py)) - ci runner. given a [compose.yml](https://github.com/wrmsr/omlish/blob/master/docker/compose.yml)
  and requirements.txt files, takes care of building and caching of containers and venvs and execution of required ci
  commands. detects and [natively uses](ci/github/api/v2) github-action's caching system.

# Amalgamation

Amalgamation is the process of stitching together multiple python source files into a single self-contained python
script. ['lite'](https://github.com/wrmsr/omlish/blob/master/omlish#lite-code) code is written in a style conducive to
this.
