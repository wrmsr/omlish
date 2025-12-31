# Overview

Enhanced function dispatch system extending `functools.singledispatch`. Supports MRO-honoring method dispatch, multiple
dispatch strategies, and improved type matching.

# Key Features

- **MRO-honoring method dispatch** - Unlike stdlib `singledispatch`, properly handles method dispatch respecting Method
  Resolution Order.
- **Multiple dispatch strategies** - Register implementations for different types and have the dispatcher select the
  best match.
- **Type-based routing** - Dispatch based on argument types, not just first argument.
- **Implementation registration** - Clean API for registering dispatch implementations.

# Core Concepts

- **Dispatcher** - Central registry mapping types to implementations.
- **Implementation** - Type-specific function/method implementations registered with a dispatcher.
- **Method dispatch** - Dispatch that works correctly with class hierarchies and method inheritance.

# Notable Modules

- **[dispatch](https://github.com/wrmsr/omlish/blob/master/omlish/dispatch/dispatch.py)** - Core dispatcher
  implementation.
- **[functions](https://github.com/wrmsr/omlish/blob/master/omlish/dispatch/functions.py)** - Function-based dispatch.
- **[methods](https://github.com/wrmsr/omlish/blob/master/omlish/dispatch/methods.py)** - Method-based dispatch with
  proper MRO handling.
- **[impls](https://github.com/wrmsr/omlish/blob/master/omlish/dispatch/impls.py)** - Implementation registration and
  lookup.

# Example Usage

```python
from omlish import dispatch

# Create a dispatcher
@dispatch.dispatch
def process(obj):
    raise NotImplementedError(f"No implementation for {type(obj)}")

# Register implementations
@process.register(str)
def _(obj):
    return f"String: {obj}"

@process.register(int)
def _(obj):
    return f"Number: {obj}"

# Dispatch based on type
process("hello")  # "String: hello"
process(42)       # "Number: 42"
```

# Comparison to stdlib singledispatch

The main improvement over `functools.singledispatch`:
- **Method dispatch** - Works correctly with class methods and inheritance.
- **MRO respect** - Follows Method Resolution Order when dispatching.
- **Better type matching** - More sophisticated type matching logic.

Use this instead of `functools.singledispatch` when:
- Dispatching methods (not just functions).
- Need proper inheritance-aware dispatch.
- Working with complex type hierarchies.

# Design Philosophy

Dispatch should:
- **Respect Python's inheritance model** - Work with MRO, not against it.
- **Be explicit** - Make dispatch logic clear and predictable.
- **Be extensible** - Easy to add new implementations without modifying existing code.

This package provides the dispatch system used throughout omlish for pluggable, type-based behavior.
