# Overview

Utilities for working with async frameworks (asyncio, trio, anyio) and abstracting over their differences. Enables
writing framework-agnostic async code that works across all three backends without modification.

# Core Concepts

- **Flavor** - Enum representing async framework types: `ASYNCIO`, `TRIO`, `ANYIO`.
- **Flavor Detection** - Runtime detection of which async framework is active via `sniffio` integration.
- **Flavor Marking** - Decorators (`@mark_asyncio`, `@mark_trio`, `@mark_anyio`) to mark functions/classes with their
  required async framework.
- **Adapters** - Convert async primitives (tasks, events, locks) between frameworks.

# Key Features

- **Framework detection** - Automatically detect the current async framework via `get_flavor()`.
- **Framework marking** - Mark code with required frameworks to prevent runtime mismatches.
- **Context managers** - `adapt_context()` wraps context managers from one framework for use in another.
- **Trio-asyncio bridge** - `with_trio_asyncio_loop()` runs asyncio code within trio contexts.
- **Module-level flavor tracking** - Track which async framework modules belong to (e.g., `sqlalchemy.ext.asyncio` is
  asyncio-flavored).
- **Adapter loops** - `with_adapter_loop()` provides framework-specific event loop access.

# Notable Modules

- **[flavors](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/flavors.py)** - Core flavor detection and
  marking system.
- **[anyio](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/anyio)** - anyio-specific utilities.
- **[asyncio](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/asyncio)** - asyncio-specific utilities.
- **[trio](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/trio)** - trio-specific utilities.
- **[trio_asyncio](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/trio_asyncio.py)** - trio-asyncio
  integration for running asyncio code in trio.
- **[bluelet](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/bluelet)** - Bluelet-style coroutine utilities.
- **[ioproxy](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/ioproxy)** - IO proxy utilities for async
  contexts.
- **[buffers](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/buffers.py)** - Async buffer implementations.
- **[sync](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/sync.py)** - Sync/async bridge utilities.

# Example Usage

```python
from omlish.asyncs import flavors

# Mark function as requiring specific framework
@flavors.mark_anyio
async def my_function():
    await anyio.sleep(1)

# Detect current framework
flavor = flavors.get_flavor()  # Returns Flavor.ASYNCIO, Flavor.TRIO, or Flavor.ANYIO

# Adapt context manager from one framework to another
@flavors.mark_asyncio
async def use_trio_lock_in_asyncio():
    trio_lock = trio.Lock()
    async with flavors.adapt_context(trio_lock):
        # Can use trio lock in asyncio context
        pass

# Run asyncio code in trio
import trio
async def main():
    async with flavors.with_trio_asyncio_loop():
        # Can use asyncio APIs here
        await asyncio.sleep(1)

trio.run(main)
```

# Design Philosophy

This package exists because many async libraries are framework-specific (e.g., libraries using asyncio directly).
Writing framework-agnostic code allows libraries to work with any async backend, and allows users to choose their
preferred framework without being locked in by dependencies.

Standard code should prefer anyio unless specifically targeting a particular framework. Lite code must use asyncio
only.

# Testing Integration

See `omlish.testing.pytest.plugins.asyncs` for pytest plugin that enables running async tests across all three
frameworks without multiple conflicting plugins.
