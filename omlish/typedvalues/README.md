# Overview

A toolkit for type-safe "boxed" values whose container types convey semantic meaning beyond the bare value. A rebellion
against stringly-typed kwargs, environment variables, and giant config objects: instead of `foo(bar=1, baz=2)`, write
`foo(Bar(1), Baz(2))`.

# Core Concepts

- **TypedValue** - Base class for boxed values. Each subclass represents a distinct semantic type.
- **UniqueTypedValue** - TypedValue that can only appear once in a collection (enforces uniqueness by type).
- **ScalarTypedValue** - TypedValue wrapping a single scalar value.
- **TypedValues** - Collection of TypedValue instances with type-based lookup.
- **TypedValuesAccessor** - Provides typed access to values in a collection.
- **TypedValuesConsumer** - Ensures all values in a collection are consumed, detecting unused values.

# Key Features

- **Type safety** - Each value type is a distinct class, enabling compile-time checking and preventing mixups.
- **Uniqueness enforcement** - `UniqueTypedValue` prevents duplicate values of the same type in a collection.
- **Collection operations** - `collect()` gathers typed values into a `TypedValues` collection with type-based lookup.
- **Generic support** - `TypedValueGeneric` enables parameterized typed value types.
- **Reflection** - `reflect_typed_values_impls()` discovers all TypedValue subclasses in a module.
- **Marshal integration** - Automatic marshaling support via `omlish.marshal` integration.
- **Consumer pattern** - `TypedValuesConsumer` ensures all values are used, preventing configuration errors.

# Example Usage

```python
from omlish import dataclasses as dc
from omlish import typedvalues as tv

# Define typed values
@dc.dataclass(frozen=True)
class MaxRetries(tv.UniqueScalarTypedValue[int]):
    pass

@dc.dataclass(frozen=True)
class Timeout(tv.UniqueScalarTypedValue[float]):
    pass

# Use instead of kwargs
def fetch(url: str, *values: tv.TypedValue) -> None:
    config = tv.collect(*values)
    max_retries = config.get(MaxRetries, MaxRetries(3)).value
    timeout = config.get(Timeout, Timeout(30.0)).value
    # ...

fetch("https://example.com", MaxRetries(5), Timeout(60.0))
```

# Benefits Over Traditional Approaches

**Instead of this:**
```python
def fetch(url, max_retries=3, timeout=30, retry_delay=1, ...):
    # Easy to mix up parameters
    fetch("url", 30, 3)  # Oops, swapped!
```

**Write this:**
```python
def fetch(url, *values: TypedValue):
    # Impossible to mix up - types are distinct
    fetch("url", Timeout(30), MaxRetries(3))
```

# Notable Modules

- **[values](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/values.py)** - Core value types:
  `TypedValue`, `UniqueTypedValue`, `ScalarTypedValue`.
- **[collection](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/collection.py)** - `TypedValues`
  collection with `collect()` and `as_collection()`.
- **[accessor](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/accessor.py)** - `TypedValuesAccessor`
  for typed value access.
- **[consumer](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/consumer.py)** - `TypedValuesConsumer`
  for ensuring all values are used.
- **[holder](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/holder.py)** - `TypedValueHolder` for
  wrapping values.
- **[generic](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/generic.py)** - `TypedValueGeneric` for
  parameterized value types.
- **[of_](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/of_.py)** - `of()` function for creating value
  instances.
- **[reflect](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/reflect.py)** - Reflection utilities for
  discovering value types.
- **[marshal](https://github.com/wrmsr/omlish/blob/master/omlish/typedvalues/marshal.py)** - Marshal integration for
  serialization.

# Design Philosophy

TypedValues replace untyped "bags of config" with strongly-typed, self-documenting value objects. This approach:
- Prevents parameter mixups at compile time.
- Makes APIs self-documenting via type names.
- Enables IDE autocomplete and refactoring.
- Allows extensibility without modifying function signatures.
- Enforces uniqueness constraints where needed.

Use TypedValues when you have configuration or parameters that:
- Have semantic meaning beyond their primitive types.
- Should be extensible without breaking existing code.
- Need uniqueness enforcement.
- Would benefit from type-driven validation.
