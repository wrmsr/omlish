# Overview

My python monorepo, the successor to my previous one `omnibus`(... 'ish').
 
This is my 'production' codebase - code which has graduated from and powers my various other little projects.

It's organized into a handful of toplevel libraries - the `om*` directories - which are each independently installable
and published to pypi.

The most substantial toplevel libraries are `omlish`, `omdev`, and (at the moment) `ommlds`, described below.

The toplevel libraries have no required dependencies besides each other - `omlish` in particular has none at all - but
there are a number of optional ones - see their respective `pyproject.toml` files for details.

Standard code is written for python 3.13+, '[lite](https://github.com/wrmsr/omlish/blob/master/omlish#lite-code)' code
for 3.8+.

# Toplevel libraries

- **[omlish](https://github.com/wrmsr/omlish/blob/master/omlish#readme)** - Core foundational code - the comprehensive
  standard library, including language helpers (like lazy imports), a `dataclasses` rebuild, a dependency injector, and
  a serde system. This is the most stable of the libraries, and the bottom of the dependency graph.
- **[omdev](https://github.com/wrmsr/omlish/blob/master/omdev#readme)** - Development utilities, including the
  all-in-one `om` CLI, the amalgamator, the `pyproject` tool, and the ci engine. This is intended to not generally be
  present in production environments.
- **[ommlds](https://github.com/wrmsr/omlish/blob/master/ommlds#readme)** - ML / data science code, including
  `minichain` (roughly like langchain) and its CLI.
- **[ominfra](https://github.com/wrmsr/omlish/blob/master/ominfra#readme)** - Infrastructure and cloud code, including
  a boto alternative, a remote management tool, and a [supervisor](https://github.com/Supervisor/supervisor) rebuild.
- **[omserv](https://github.com/wrmsr/omlish/blob/master/omserv#readme)** - Request serving code, including an internal
  fork of [hypercorn](https://github.com/pgjones/hypercorn).

# Installation

Toplevel libraries are installable by name from pypi:

```bash
pip install omlish
```

Or directly from git via:

```bash
pip install 'git+https://github.com/wrmsr/omlish@master#subdirectory=.pkg/omlish'
```

The CLI is installable through uvx or pipx via:

```bash
curl -LsSf 'https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/cli/install.py' | python3 -
```

Additional deps to be injected may be appended to the command.

Once installed the CLI can be updated via:

```bash
om cli reinstall
```

# Project structure

The structure of the repo is managed by the internal
[pyproject](https://github.com/wrmsr/omlish/blob/master/omdev/pyproject) tool, which generates
[`.pkg`](https://github.com/wrmsr/omlish/blob/master/.pkg) directories (which map to published packages) from each
library's [`__about__.py`](https://github.com/wrmsr/omlish/blob/master/omlish/__about__.py). The root-level
[`pyproject.toml`](https://github.com/wrmsr/omlish/blob/master/pyproject.toml) does not actually contain a PEP-621
project.
