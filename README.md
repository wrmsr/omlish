# Overview

My python monorepo, the successor to my previous one `omnibus`(... 'ish').

Core packages begin with `om`, scratch app is in `app`, temp / dump code is in `x`.

The packages have no required dependencies besides each other, but there are numerous optional ones - see their
respective `pyproject.toml` files for details.

General code is written for python 3.12+, '[lite](omlish/README.md#lite-code' code for 3.8+.

# Core packages

- **[omlish](omlish#readme)** - Core foundational code
- **[omdev](omdev#readme)** - Development utilities
- **[omserv](omserv)** - Production web server
- **[ominfra](ominfra)** - Infrastructure and cloud code
- **[ommlx](ommlx)** - ML / AI code

# Installation

Core packages installable from pypi, or from git via:

```bash
pip install 'git+https://github.com/wrmsr/omlish@master#subdirectory=.pkg/<pkg>'
```

The CLI is installable through uvx or pipx via:

```bash
curl -LsSf 'https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/cli/install.py' | python3 -
```

Additional deps to be injected may be appended to the command.
