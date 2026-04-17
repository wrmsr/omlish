# Typed Values

A type-safe heterogeneous collection system for managing typed values with compile-time type checking and runtime
validation.

## Overview

The `typedvalues` package provides a framework for building type-safe collections of heterogeneous values where types
themselves serve as keys. It combines the benefits of compile-time type safety with runtime validation, enabling
patterns like type-based dependency injection, configuration management, and option passing.

## Core Concepts

### TypedValue

The base abstract class for all typed values. Typed values are meant to be used as types-as-keys in collections, not as
boolean conditions.

```python
from omlish import typedvalues as tv

class MyValue(tv.TypedValue):
    pass
```

All `TypedValue` instances explicitly prevent boolean conversion to avoid accidental misuse:

```python
if my_value:  # TypeError: Cannot convert MyValue to bool - use '.v' or 'is not None'
    pass
```

### UniqueTypedValue

An abstract class for typed values where only one instance per unique type family can exist in a collection. The
immediately inheriting class becomes the "unique key" for all its descendants.

```python
from omlish import typedvalues as tv

class ResponseFormat(tv.UniqueTypedValue):
    pass

class JsonResponseFormat(ResponseFormat):
    pass

class TextResponseFormat(ResponseFormat):
    pass
```

In a `TypedValues` collection, you can have either a `JsonResponseFormat` or `TextResponseFormat`, but not both
(unless override mode is enabled).

### ScalarTypedValue

A generic typed value wrapper for scalar values, inheriting from `dc.Box[T]`. Access the wrapped value via the `.v`
attribute.

```python
from omlish import typedvalues as tv

class TopK(tv.ScalarTypedValue[int]):
    pass

top_k = TopK(10)
print(top_k.v)  # 10
```

### UniqueScalarTypedValue

Combines both `ScalarTypedValue` and `UniqueTypedValue` characteristics.

```python
from omlish import typedvalues as tv

class Temperature(tv.UniqueScalarTypedValue[float]):
    pass
```

**Important MRO requirement:** When a class inherits from both `ScalarTypedValue` and `UniqueTypedValue`,
`ScalarTypedValue` must appear first in the inheritance hierarchy to ensure proper method resolution order.

```python
# Correct
class Good(tv.ScalarTypedValue[int], tv.UniqueTypedValue):
    pass

# Incorrect - raises TypeError
class Bad(tv.UniqueTypedValue, tv.ScalarTypedValue[int]):
    pass
```

## Collections

### TypedValues

The main immutable collection class for managing typed values. It preserves insertion order and provides type-safe
access methods.

```python
from omlish import dataclasses as dc
from omlish import typedvalues as tv

class TopK(tv.ScalarTypedValue[int], tv.UniqueTypedValue):
    pass

@dc.dataclass(frozen=True)
class Tool(tv.TypedValue):
    name: str

opts = tv.TypedValues(
    TopK(5),
    Tool('hammer'),
    Tool('wrench'),
)
```

#### Type-based Indexing

Access values by their type:

```python
# For unique types, returns the single instance
top_k = opts[TopK]  # TopK(5)

# For non-unique types, returns a sequence
tools = opts[Tool]  # (Tool('hammer'), Tool('wrench'))

# Integer indexing also works
first = opts[0]  # TopK(5)
```

#### Safe Access with get()

```python
# Returns None if not found
temp = opts.get(Temperature)  # None

# Provide a default
temp = opts.get(Temperature, Temperature(0.5))  # Temperature(0.5)

# Pass an instance to use as both key and default
temp = opts.get(Temperature(0.5))  # Temperature(0.5)
```

#### Contains Checks

```python
TopK in opts  # True
Temperature in opts  # False

# Works with both unique base class and concrete class
ResponseFormat in opts  # True
JsonResponseFormat in opts  # True
```

#### Filtering and Updates

```python
# Filter out specific types
filtered = tv.TypedValues(*opts.without(Tool))

# Immutable discard
new_opts = opts.discard(Tool)

# Immutable update
updated = opts.update(Temperature(0.7), TopK(10), override=True)
```

### Override Mode

By default, duplicate unique typed values raise `DuplicateUniqueTypedValueError`:

```python
tv.TypedValues(
    TextResponseFormat(),
    JsonResponseFormat(),  # DuplicateUniqueTypedValueError
)
```

Enable override mode for last-in-wins semantics:

```python
opts = tv.TypedValues(
    TopK(5),
    Tool('hammer'),
    TopK(10),  # This wins
    override=True,
)

assert opts[TopK] == TopK(10)
```

With override enabled, later unique values replace earlier ones while preserving the order of the final set.

## Consumer Pattern

### TypedValuesConsumer

A context manager for consuming typed values with validation that all values are processed.

```python
from omlish import typedvalues as tv

opts = tv.TypedValues(
    TopK(10),
    Tool('hammer'),
    Temperature(0.5),
)

with tv.TypedValuesConsumer(opts) as consumer:
    top_k = consumer.pop(TopK)  # TopK(10)
    temp = consumer.pop(Temperature)  # Temperature(0.5)
    tool = consumer.pop(Tool)  # (Tool('hammer'),)
    # Exits successfully - all values consumed
```

If values remain unconsumed on exit, raises `UnconsumedTypedValuesError`:

```python
with tv.TypedValuesConsumer(opts) as consumer:
    consumer.pop(TopK)
    # UnconsumedTypedValuesError: [Tool('hammer'), Temperature(0.5)]
```

#### pop() Method

The `pop()` method has the same overloaded behavior as accessor's `get()`:

```python
# For unique types, returns scalar
temp = consumer.pop(Temperature)  # Temperature(0.5)

# For non-unique types, returns tuple
tools = consumer.pop(Tool)  # (Tool('hammer'), Tool('wrench'))

# With default
temp = consumer.pop(Temperature, Temperature(1.0))  # Temperature(1.0)

# Raises KeyError if not found and no default
temp = consumer.pop(Temperature)  # KeyError
```

#### Extracting Scalar Kwargs

Convert scalar typed values directly to function kwargs:

```python
kwargs = consumer.pop_scalar_kwargs(
    top_k=TopK,
    temperature=Temperature,
)
# {'top_k': 10, 'temperature': 0.5}

model.generate(**kwargs)
```

#### Convenience Function

```python
from omlish import typedvalues as tv

with tv.consume(TopK(10), Temperature(0.5)) as c:
    # Use consumer
    pass
```

## Accessor

### TypedValuesAccessor

An abstract base class providing read-only sequence-like access to typed values. `TypedValues` implements this
interface.

Custom accessor implementations can extend this to provide specialized views:

```python
from omlish import typedvalues as tv

class MyAccessor(tv.TypedValuesAccessor[MyValueType]):
    def _typed_value_contains(self, cls):
        # Implementation
        pass

    def _typed_value_getitem(self, key):
        # Implementation
        pass

    def _typed_value_get_any(self, cls):
        # Implementation
        pass
```

## Common Patterns

### Configuration Management

```python
from omlish import dataclasses as dc
from omlish import typedvalues as tv

class MaxRetries(tv.UniqueScalarTypedValue[int]):
    pass

class Timeout(tv.UniqueScalarTypedValue[float]):
    pass

class Debug(tv.UniqueScalarTypedValue[bool]):
    pass

config = tv.TypedValues(
    MaxRetries(3),
    Timeout(30.0),
    Debug(True),
)

# Type-safe access
max_retries = config[MaxRetries].v  # 3
timeout = config.get(Timeout, Timeout(60.0)).v  # 30.0
```

### Option Passing

```python
from omlish import dataclasses as dc
from omlish import typedvalues as tv

class ChatOption(tv.TypedValue):
    pass

@dc.dataclass(frozen=True)
class Tool(ChatOption):
    name: str

class ResponseFormat(ChatOption, tv.UniqueTypedValue):
    pass

@dc.dataclass(frozen=True)
class JsonResponseFormat(ResponseFormat):
    schema: dict | None = None

def chat(message: str, *options: ChatOption):
    opts = tv.TypedValues(*options)

    tools = opts.get(Tool, ())
    response_format = opts.get(ResponseFormat)

    # Use options...
```

## Performance

The `_init_typed_values_collection()` function has an optional C extension implementation for improved performance when
working with large collections. The extension is automatically used if available.

## Type Safety

The package makes extensive use of `typing.overload` to provide accurate type hints for static type checkers:

```python
# Type checker knows this is TopK
top_k: TopK = opts[TopK]

# Type checker knows this is Sequence[Tool]
tools: ta.Sequence[Tool] = opts[Tool]

# Type checker knows this is TopK | None
maybe_top_k: TopK | None = opts.get(TopK)
```
