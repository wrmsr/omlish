# Overview

Runtime reflection utilities for working with Python types, annotations, and type system features. Provides a
formalized, stable representation of type information decoupled from stdlib implementation details.

# Key Features

- **Type representation** - `Type` abstraction representing Python types in a stable, introspectable format.
- **Annotation parsing** - Parse and normalize type annotations from functions and classes.
- **Type manipulation** - Substitute type parameters, resolve generic types, inspect type structure.
- **Stdlib decoupling** - Isolates code from Python version-specific type system changes.
- **Generic support** - Full support for generic types, type parameters, and type substitution.

# Core Concepts

- **Type** - Normalized representation of a Python type, independent of `typing` module internals.
- **Type substitution** - Replace type variables with concrete types (e.g., `List[T]` → `List[int]`).
- **Type inspection** - Query type properties (is it generic? what are its parameters? what's its origin?).

# Notable Modules

- **[types](https://github.com/wrmsr/omlish/blob/master/omlish/reflect/types.py)** - Core `Type` abstraction and type
  representation.
- **[inspect](https://github.com/wrmsr/omlish/blob/master/omlish/reflect/inspect.py)** - Type inspection utilities for
  extracting type information from objects.
- **[subst](https://github.com/wrmsr/omlish/blob/master/omlish/reflect/subst.py)** - Type parameter substitution for
  generic types.
- **[ops](https://github.com/wrmsr/omlish/blob/master/omlish/reflect/ops.py)** - Type operations and manipulations.

# Example Usage

```python
from omlish import reflect as rfl

# Get normalized type representation
ty = rfl.type_(list[int])
print(ty.origin)  # list
print(ty.args)    # (int,)

# Type substitution
from typing import TypeVar, Generic
T = TypeVar('T')

class Box(Generic[T]):
    pass

# Substitute T with int
box_int = rfl.substitute(Box[T], {T: int})  # Box[int]

# Inspect function signatures
def func(x: int, y: str) -> bool:
    pass

sig = rfl.inspect_signature(func)
print(sig.parameters['x'].annotation)  # int
```

# Why Reflection?

Python's `typing` module internals change across versions (3.8, 3.9, 3.10, 3.11 all have incompatibilities). This
package:
- **Normalizes** type representations across Python versions.
- **Stabilizes** APIs so code doesn't break when type system internals change.
- **Simplifies** working with types at runtime.

This is notoriously difficult to maintain across Python versions, which is one reason omlish targets 3.13+ only for
standard code.

# Design Philosophy

Reflection should:
- **Hide complexity** - Abstract away `typing` module internals.
- **Be stable** - Provide consistent APIs across Python versions.
- **Be precise** - Accurately represent type information without loss.
- **Be usable** - Make runtime type introspection straightforward.

This package is used throughout omlish wherever runtime type information is needed (dependency injection, marshaling,
validation, etc.).
