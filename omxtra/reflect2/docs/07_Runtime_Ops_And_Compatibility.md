# Runtime Ops And Compatibility

This note records the runtime-facing operation helpers added on top of the core IR machinery.

## Shape

Runtime operation helpers live in `runtime/ops.py`.

They are intentionally thin wrappers:

1. Reflect runtime objects into distilled `Type` nodes with `RuntimeTypeReflector`.
2. Call the corresponding core operation.
3. Return the distilled result or boolean answer.

This keeps runtime object inspection separated from the core type algorithms. The core operations continue to work only on `Type` objects and remain the better target for mypyc-compatible code.

Every helper accepts an optional `RuntimeTypeReflector`. Passing one explicitly lets callers reuse the same universe and reflection cache across a larger operation.

## Join And Meet

Runtime join helpers:

- `reflect_join(left, right, reflector=None)`
- `reflect_join_list(items, reflector=None)`

Runtime meet helpers:

- `reflect_meet(left, right, reflector=None)`
- `reflect_meet_list(items, reflector=None)`

These mirror `join_types`, `join_type_list`, `meet_types`, and `meet_type_list`.

Examples:

```python
reflect_join(int | str, int)        # int | str
reflect_meet(int | str, int)        # int
reflect_meet(int | str, float)      # Never
reflect_join(list[int], list[str])  # list[int] | list[str]
```

The generic alias example remains a union because builtin `list` is invariant in the current universe.

Runtime generic inheritance participates through the reflected `TypeInfo.bases` graph:

```python
T = TypeVar('T')

class Box(Generic[T]):
    pass

class IntBox(Box[int]):
    pass

reflect_join(IntBox, Box[int])  # Box[int]
reflect_meet(IntBox, Box[int])  # IntBox
reflect_join(IntBox, Box[str])  # IntBox | Box[str]
reflect_meet(IntBox, Box[str])  # Never
```

## Assignability

Core compatibility helpers live in `compat.py`.

- `is_assignable(source, target)` is the strict predicate.
- `is_assignable_or_false(source, target)` is the conservative predicate.

The strict predicate currently delegates to `is_subtype(source, target)`. In this IR, `Any` compatibility is already handled by subtype checks in both directions.

Runtime wrappers:

- `reflect_is_assignable(source, target, reflector=None)`
- `reflect_is_assignable_or_false(source, target, reflector=None)`

Examples:

```python
reflect_is_assignable(int, int | str)      # True
reflect_is_assignable(int | str, int)      # False
reflect_is_assignable(Any, int)            # True
reflect_is_assignable(int, Any)            # True
reflect_is_assignable(IntBox, Box[int])    # True
reflect_is_assignable(IntBox, Box[str])    # False
```

The strict form raises `UnsupportedTypeOperationError` if the underlying semantic relation is not implemented. The conservative form catches that specific error and returns `False`.

## Substitution

Runtime substitution helpers:

- `reflect_substitute_type(typ, replacements, reflector=None)`
- `reflect_substitute_types(typs, replacements, reflector=None)`

They reflect the input type object, reflect replacement values, and then call the core substitution helpers.

Runtime replacement keys may be:

- already-distilled `TypeVarId`
- already-distilled `TypeVarLikeType`
- runtime `typing.TypeVar` objects

Runtime `TypeVar` keys are reflected with the same reflector used for the input type. This matters because TypeVar identity is cache-sensitive: the key must correspond to the same reflected variable object that appears inside the reflected input.

Example:

```python
T = TypeVar('T')

reflect_substitute_type(list[T], {T: int})  # list[int]

reflect_substitute_types(
    [list[T], dict[str, T]],
    {T: int},
)  # [list[int], dict[str, int]]
```

Non-TypeVar runtime replacement keys raise `TypeError`.

Replacement values remain one-to-one runtime type objects. Higher-order substitutions such as replacing a type variable with a list of argument types are not implemented.

## Error Policy

Runtime helpers preserve the same fail-closed policy as the core operations.

Reflection failures raise `UnreflectableTypeError`. For example, passing an arbitrary object instance where a runtime type object is expected is not silently accepted.

Unsupported core semantic operations raise `UnsupportedTypeOperationError` in strict helpers. For example, callable assignability and callable join/meet relations are still outside the implemented subtype fragment.

Conservative helpers are named explicitly with `_or_false`. Currently this applies to assignability. These helpers only suppress `UnsupportedTypeOperationError`; they do not suppress reflection failures.

## Current Boundary

The runtime operation layer is not a separate type checker. It is a convenience boundary for runtime `typing` objects.

It does not validate arbitrary values against reflected types, read source code, or infer source-level annotations. It reflects type-form objects that already exist in the Python heap, then applies the distilled IR operations implemented so far.

Likely future additions:

- runtime wrappers for future solve/infer operations
- runtime-friendly helpers for type argument extraction through `get_base_instance`
- richer callable support once callable subtyping exists
- broader ABC and protocol metadata reflection
