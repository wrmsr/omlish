# Overview

My python monorepo, the successor to my previous one `omnibus`(... 'ish').

The core libraries have no required dependencies besides each other, but there are numerous optional ones - see their
respective `pyproject.toml` files for details.

Standard code is written for python 3.13+, '[lite](https://github.com/wrmsr/omlish/blob/master/omlish#lite-code)' code
for 3.8+.

# Core libraries

- **[omlish](https://github.com/wrmsr/omlish/blob/master/omlish#readme)** - Core foundational code
- **[omdev](https://github.com/wrmsr/omlish/blob/master/omdev#readme)** - Development utilities
- **[ominfra](https://github.com/wrmsr/omlish/blob/master/ominfra#readme)** - Infrastructure and cloud code
- **[ommlds](https://github.com/wrmsr/omlish/blob/master/ommlds#readme)** - ML / data science code
- **[omserv](https://github.com/wrmsr/omlish/blob/master/omserv#readme)** - Request serving code

# Installation

Core libraries installable by name from pypi:

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
