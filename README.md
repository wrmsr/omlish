# Overview

My python monorepo, the successor to my previous one `omnibus`(... 'ish').

The core libraries have no required dependencies besides each other, but there are numerous optional ones - see their
respective `pyproject.toml` files for details.

General code is written for python 3.13+, '[lite](omlish#lite-code)' code for 3.8+.

# Core libraries

- **[omlish](omlish#readme)** - Core foundational code
- **[omdev](omdev#readme)** - Development utilities
- **[ominfra](ominfra)** - Infrastructure and cloud code
- **[ommlds](ommlds)** - ML / data science code
- **[omserv](omserv)** - Request serving code

# Installation

Core libraries installable by name from pypi:

```bash
pip install omlish
```

Or directly from git via:

```bash
pip install 'git+https://github.com/wrmsr/omlish@master#subdirectory=.pkg/<pkg>'
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

The structure of the repo is managed by the internal [pyproject](omdev/pyproject) tool, which generates [`.pkg`](.pkg)
directories (which map to published packages) from each library's [`__about__.py`](omlish/__about__.py). The root-level
[`pyproject.toml`](pyproject.toml) does not actually contain a PEP-621 project.

