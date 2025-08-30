# Overview

Development utilities and support code.

# Notable packages

- **[cli](https://github.com/wrmsr/omlish/blob/master/omdev/cli)** - The codebase's all-in-one CLI. This is not
  installed as an entrypoint / command when this package is itself installed - that is separated into the `omdev-cli`
  installable package so as to not pollute users' bin/ directories when depping this lib for its utility code.

- **[amalg](https://github.com/wrmsr/omlish/blob/master/omdev/amalg)** - The [amalgamator](#amalgamation).

- **[pyproject](https://github.com/wrmsr/omlish/blob/master/omdev/pyproject)**
  ([amalg](https://github.com/wrmsr/omlish/blob/master/omdev/scripts/pyproject.py)) - python project management tool.
  wrangles but does not replace tools like venv, pip, setuptools, and uv. does things like sets up venvs, generates
  [`.pkg`](https://github.com/wrmsr/omlish/blob/master/.pkg) directories and their `pyproject.toml`'s (from their
  `__about__.py`'s), and packages them. this should grow to eat more and more of the Makefile. as it is amalgamated it
  requires no installation and can just be dropped into other projects / repos.

- **[ci](https://github.com/wrmsr/omlish/blob/master/omdev/ci)**
  ([amalg](https://github.com/wrmsr/omlish/blob/master/omdev/scripts/ci.py)) - ci runner. given a
  [`compose.yml`](https://github.com/wrmsr/omlish/blob/master/docker/compose.yml)
  and requirements.txt files, takes care of building and caching of containers and venvs and execution of required ci
  commands. detects and [natively uses](https://github.com/wrmsr/omlish/blob/master/omdev/ci/github/api/v2)
  github-action's caching system. unifies ci execution between local dev and github runners.

- **[tools.json](https://github.com/wrmsr/omlish/blob/master/omdev/tools/json)** (cli: `om j`) - a tool for json-like
  data, obviously in the vein of [jq](https://github.com/jqlang/jq) but using the internal
  [jmespath](https://github.com/wrmsr/omlish/blob/master/omlish/specs/jmespath) engine. supports
  [true streaming](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json/stream) json input and output, as
  well as [various other](https://github.com/wrmsr/omlish/blob/master/omdev/tools/json/formats.py) non-streaming input
  formats.

- **[tools.git](https://github.com/wrmsr/omlish/blob/master/omdev/tools/git)** (cli: `om git`) - a tool for various lazy
  git operations, including the one that (poorly) writes all of these commit messages.

# Amalgamation

Amalgamation is the process of stitching together multiple python source files into a single self-contained python
script. ['lite'](https://github.com/wrmsr/omlish/blob/master/omlish#lite-code) code is written in a style conducive to
this.

# Local storage

Some of this code, when asked, will store things on the local filesystem. The only directories used (outside of ones
explicitly specified as command or function arguments) are managed in
[home.paths](https://github.com/wrmsr/omlish/blob/master/omdev/home/paths.py), and are the following:

- `$OMLISH_HOME`, default of `~/.omlish` - persistent things like config and state.
- `$OMLISH_CACHE`, default of `~/.cache/omlish` - used for things like the local ci cache and
  [various other](https://github.com/search?q=repo%3Awrmsr%2Fomlish+%22dcache.%22&type=code) cached data.
