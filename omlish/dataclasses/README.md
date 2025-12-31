# Overview

A fully-compatible reimplementation of stdlib `dataclasses` with numerous enhancements. Runs the complete stdlib test
suite ensuring they *are* dataclasses, just with more features.

# Key Enhancements

- **Field coercion** - Automatically coerce field values to their annotated types.
- **Field validation** - Validate field values with custom validators.
- **Multiple init/validate methods** - Use `@dc.init` or `@dc.validate` decorators multiple times, not just
  `__post_init__`.
- **Generic type substitution** - Generic type parameters are substituted in generated `__init__` for accurate
  reflection.
- **Metaclass support** - Optional metaclass removes need for re-decorating subclasses, supports parameter inheritance.
- **Base classes** - Convenient base classes with common patterns.
- **Code generation** - Ahead-of-time/build-time code generation for faster imports.
- **Extra parameters** - Additional `@dc.extra_class_params()` for common patterns (terse repr, cached hash, etc.).

# Core Features

- **Full stdlib compatibility** - Drop-in replacement for stdlib `dataclasses`.
- **Tested compatibility** - Complete stdlib test suite runs against this implementation.
- **Enhanced functionality** - Superset of stdlib features, not a different model.
- **Import-time generation** - Like stdlib, generates code at class definition time (or ahead-of-time with codegen).

# Notable Modules

- **[base](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/base.py)** - Core dataclass implementation
  and decorator.
- **[metaclass](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/metaclass)** - Optional metaclass for
  enhanced features:
  - Removes need to redecorate subclasses.
  - Inherits dataclass parameters (like `frozen`) from parent classes.
  - **[bases](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/metaclass/bases.py)** - Convenient base
    classes.
- **[configs](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/configs.py)** - Configuration classes and
  helpers.
- **[bootstrap](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/bootstrap.py)** - Package initialization
  and code generation support.
- **[contextmanagers](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/contextmanagers.py)** - Context
  manager utilities for dataclasses.
- **[maysync](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/maysync.py)** - Maysync (dual sync/async)
  dataclass support.

# Example Usage

```python
from omlish import dataclasses as dc

# Standard dataclass (stdlib compatible)
@dc.dataclass(frozen=True)
class Point:
    x: int
    y: int

# With field coercion
@dc.dataclass()
class User:
    name: str = dc.xfield(coerce=str)  # Coerce to str
    age: int = dc.xfield(coerce=int, validate=lambda x: x >= 0)  # Coerce and validate

# Multiple init methods
@dc.dataclass()
class Rectangle:
    width: int
    height: int

    @dc.init
    def _compute_area(self) -> None:
        self._area = self.width * self.height

    @dc.init
    def _validate_positive(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensions must be positive")

# Extra class parameters
@dc.dataclass()
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class CachedPoint:
    x: int
    y: int
```

# Comparison to Stdlib

Enhancements over stdlib `dataclasses`:
- **Coercion/validation** - Not available in stdlib.
- **Multiple init methods** - stdlib only has `__post_init__`.
- **Metaclass** - stdlib requires redecorating subclasses.
- **Type substitution** - stdlib doesn't substitute generics in `__init__`.
- **Code generation** - Ahead-of-time generation significantly reduces import time.

All stdlib features work identically, ensuring this is a true superset.

# Design Philosophy

The dataclasses reimplementation:
- **Maintains compatibility** - Must pass stdlib test suite.
- **Adds features conservatively** - Only add features that don't break stdlib compatibility.
- **Generates efficient code** - Generated methods should be as fast as hand-written equivalents.
- **Supports ahead-of-time generation** - Critical for reducing import times in large codebases.

This package is used throughout omlish wherever dataclasses are needed, which is nearly everywhere.
