# Overview

A [Jackson](https://github.com/FasterXML/jackson)-style serialization and deserialization (serde) system. Provides
type-driven marshaling and unmarshaling of Python objects to/from generic value representations (dicts, lists,
primitives), typically for JSON but adaptable to other formats.

# Core Concepts

- **Marshaler** - Converts Python objects to generic `Value` representations (primitives, dicts, lists).
- **Unmarshaler** - Converts generic `Value` representations back to typed Python objects.
- **MarshalerFactory** / **UnmarshalerFactory** - Generate marshalers and unmarshalers for specific types based on
  runtime reflection.
- **Context** - Carries configuration and state during marshaling/unmarshaling operations.
- **Value** - Generic type alias for marshaled data (`str | int | float | bool | None | list | dict`).
- **Config** - Type-specific configuration attached via class metadata to customize marshaling behavior.

# Key Features

- **Type-driven** - Automatic marshaler/unmarshaler generation from type annotations using runtime reflection.
- **Dataclass support** - First-class support for `omlish.dataclasses` with field-level metadata and options.
- **Polymorphism** - Multiple strategies for handling inheritance hierarchies:
  - **WrapperTypeTagging** - Wraps values in `{"TypeName": {...}}` dicts.
  - **FieldTypeTagging** - Adds a type discriminator field (e.g., `"type": "TypeName"`).
  - **PolymorphismUnion** - Maps Python unions to tagged representations.
- **Composite types** - Built-in support for `list`, `dict`, `set`, `frozenset`, `Optional`, `Union`, `Literal`,
  `ta.NewType`, and `lang.Maybe`.
- **Singular types** - Marshalers for `datetime`, `UUID`, `Decimal`, `Enum`, base64-encoded `bytes`.
- **Name translation** - Convert between Python naming conventions (snake_case) and JSON conventions (camelCase) via
  `Naming` configs.
- **Field metadata** - Per-field marshaling options: rename fields, mark as optional, apply custom marshalers, or skip
  fields entirely.
- **Factory composition** - Chain multiple `MarshalerFactory` instances via `MultiMarshalerFactory` to build complex
  marshaling pipelines.
- **Type caching** - `TypeCacheMarshalerFactory` caches generated marshalers for performance.
- **Recursive types** - `RecursiveMarshalerFactory` handles self-referential types.
- **Module imports** - `ModuleImportingMarshalerFactory` dynamically imports and applies marshalers from specified
  modules.
- **Forbidden types** - Explicitly reject marshaling of certain types for security or design constraints.

# Notable Modules

- **[base](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/base)** - Core abstractions and types:
  - **[types](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/base/types.py)** - `Marshaler`,
    `Unmarshaler`, `MarshalerFactory`, `UnmarshalerFactory`.
  - **[contexts](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/base/contexts.py)** - Marshaling and
    unmarshaling context types.
  - **[configs](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/base/configs.py)** - Configuration registry
    for attaching type-specific metadata.
- **[objects](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/objects)** - Object marshaling:
  - **[dataclasses](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/objects/dataclasses.py)** - Marshaling
    for `omlish.dataclasses` with field metadata support.
  - **[metadata](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/objects/metadata.py)** - `FieldInfo`,
    `FieldOptions`, `ObjectMetadata` for field-level customization.
  - **[helpers](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/objects/helpers.py)** - Utilities like
    `update_fields_metadata()` for modifying field metadata.
- **[polymorphism](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/polymorphism)** - Polymorphic type
  handling:
  - **[metadata](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/polymorphism/metadata.py)** -
    `Polymorphism`, `TypeTagging`, `Impl` for defining type hierarchies.
  - **[marshal](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/polymorphism/marshal.py)** /
    **[unmarshal](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/polymorphism/unmarshal.py)** -
    Polymorphism-aware marshalers.
- **[composite](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/composite)** - Composite type marshalers for
  iterables, optionals, unions, literals, wrapped types.
- **[singular](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/singular)** - Singular type marshalers for
  primitives, enums, UUIDs, datetimes, base64.
- **[factories](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/factories)** - Advanced factory
  implementations:
  - **[typemap](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/factories/typemap.py)** - Direct type-to-marshaler mapping.
  - **[typecache](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/factories/typecache.py)** - Caches
    generated marshalers.
  - **[multi](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/factories/multi.py)** - Chains multiple
    factories.
  - **[recursive](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/factories/recursive.py)** - Handles
    recursive types.
  - **[moduleimport](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/factories/moduleimport)** - Imports
    marshalers from modules.
- **[naming](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/naming.py)** - Name translation utilities for
  converting between naming conventions.
- **[standard](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/standard.py)** - Standard factory
  configurations with common marshalers pre-configured.
- **[globals](https://github.com/wrmsr/omlish/blob/master/omlish/marshal/globals.py)** - Global marshaler/unmarshaler
  factory instances and convenience functions (`marshal()`, `unmarshal()`).

# Example Usage

```python
from omlish import dataclasses as dc
from omlish import marshal as msh

@dc.dataclass(frozen=True)
class User:
    name: str
    age: int

# Marshal to dict
user = User('Alice', 30)
data = msh.marshal(user)  # {'name': 'Alice', 'age': 30}

# Unmarshal from dict
user2 = msh.unmarshal({'name': 'Bob', 'age': 25}, User)
```

# Comparison to Lite Marshal

The standard marshal system offers significantly more features than `omlish.lite.marshal`:
- Polymorphism support
- Advanced factory composition
- Field metadata and options
- Name translation
- Recursive type handling
- Module imports
- Extensive configuration

Use the lite marshal when targeting Python 3.8+ or when a minimal footprint is required.
