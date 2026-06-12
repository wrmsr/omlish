# Runtime Base Queries

This note records the base-query helpers now available in core and runtime layers.

## Purpose

Many runtime reflection use cases need to ask:

- is this type related to a particular generic base?
- what concrete base `Instance` does it map to?
- what type arguments did it bind at that base?

Examples:

```python
list[int]       -> Sequence[int]
dict[str, int]  -> Mapping[str, int]
IntBox          -> Box[int]
```

The base-query helpers expose this directly instead of requiring callers to manually combine reflection, subtype checks, and `TypeInfo` inspection.

## Core Helpers

Core helpers live in `subtypes.py` and operate on distilled IR objects.

Strict helpers:

- `get_base_instance(left, right_info)`
- `get_base_args(left, right_info)`

Conservative helpers:

- `get_base_instance_or_none(left, right_info)`
- `get_base_args_or_none(left, right_info)`

`get_base_instance()` returns the mapped base `Instance` for a source `Instance` and target `TypeInfo`.

`get_base_args()` returns only that mapped base instance's arguments.

If the target is not in the source type's MRO, both strict helpers return `None`.

If the target is present but the generic mapping cannot be computed accurately, strict helpers raise `UnsupportedTypeOperationError`. Conservative helpers catch only that error and return `None`.

## Runtime Helpers

Runtime helpers live in `runtime/ops.py` and reflect runtime objects before calling the core helpers.

Strict helpers:

- `reflect_base_instance(source, target, reflector=None)`
- `reflect_base_args(source, target, reflector=None)`

Conservative helpers:

- `reflect_base_instance_or_none(source, target, reflector=None)`
- `reflect_base_args_or_none(source, target, reflector=None)`

The runtime target may be a bare class or a parameterized alias. The target arguments are currently ignored for base lookup; the target's reflected `TypeInfo` selects the base.

Example:

```python
reflect_base_args(IntBox, Box)       # [int]
reflect_base_args(IntBox, Box[str])  # [int]
```

The second result is still `[int]` because the query asks, "what args does `IntBox` bind at `Box`?", not "is `IntBox` compatible with `Box[str]`?" Use assignability for that compatibility question.

## Collection Examples

Synthetic collection metadata in the runtime universe feeds these helpers.

```python
reflect_base_instance(list[int], Sequence)       # Sequence[int]
reflect_base_args(list[int], Sequence)           # [int]

reflect_base_instance(tuple[int, ...], Sequence) # Sequence[int]
reflect_base_args(tuple[int, ...], Sequence)     # [int]

reflect_base_instance(dict[str, int], Mapping)   # Mapping[str, int]
reflect_base_args(dict[str, int], Mapping)       # [str, int]

reflect_base_instance(set[int], Set)             # Set[int]
reflect_base_args(set[int], Set)                 # [int]
```

Concrete sequence-like builtins are also represented:

```python
reflect_base_instance(str, Sequence)    # Sequence[str]
reflect_base_args(str, Sequence)        # [str]

reflect_base_instance(bytes, Sequence)  # Sequence[int]
reflect_base_args(bytes, Sequence)      # [int]
```

## Runtime Generic Class Example

```python
T = TypeVar('T')

class Box(Generic[T]):
    pass

class IntBox(Box[int]):
    pass

reflect_base_instance(IntBox, Box)  # Box[int]
reflect_base_args(IntBox, Box)      # [int]
```

Indirect generic bases are handled through the declared base graph:

```python
class Middle(Box[T]):
    pass

class Child(Middle[int]):
    pass

reflect_base_args(Child, Box)  # [int]
```

## Error Policy

Runtime helpers preserve reflection and shape errors.

If a runtime object cannot be reflected, `UnreflectableTypeError` is raised.

If the reflected source or target is not an `Instance`, `TypeError` is raised. For example, asking for base args at a union target is currently a caller error.

The `_or_none` helpers only suppress unsupported generic base mapping. They do not suppress reflection failures or non-instance shape errors.

## Boundaries

Base queries are nominal and rely on `TypeInfo.mro` plus declared bases.

They do not implement protocols, structural matching, callable relations, or runtime ABC registry scanning. For compatibility questions, use assignability helpers; for "what base args were bound?" questions, use base-query helpers.
