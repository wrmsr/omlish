# Lattice And Runtime Bases

This note records the current state after connecting runtime class reflection to nominal generic base mapping and adding the first join/meet operations.

## Runtime TypeInfo Enrichment

Runtime reflection now does more than create a bare `Instance` for a class.

When reflecting a runtime class or generic alias, the reflector prepares the class's `TypeInfo` with:

- generic parameters from `__parameters__`
- variances copied from reflected `TypeVarType` parameters
- `mro` from the runtime class `__mro__`
- declared bases from `__orig_bases__` when available
- fallback declared bases from `__bases__`

The runtime-only reflection layer still owns this inspection. The core IR and subtype machinery continue to operate only on distilled `TypeInfo` and `Type` objects.

`typing.Generic[...]` scaffolding bases are skipped. Real declared bases are reflected into `Instance` nodes, including generic arguments.

This means a runtime hierarchy like:

```python
class Box(Generic[T]):
    pass

class IntBox(Box[int]):
    pass
```

now gives `IntBox` a declared base equivalent to `Box[int]` in its reflected `TypeInfo`.

## Generic Base Mapping

Nominal `Instance` subtyping now maps declared base arguments through direct and indirect base chains.

For example, a distilled hierarchy equivalent to:

```python
class Base(Generic[T]):
    pass

class Middle(Base[T]):
    pass

class Child(Middle[T]):
    pass
```

can prove that `Child[int]` is a subtype of `Base[int]`.

The public helper `get_base_instance()` exposes this mapping directly. It currently behaves as follows:

- if the target `TypeInfo` is the instance's own type, return the original instance
- if the target is not in the instance type's MRO, return `None`
- if the target can be reached through declared bases, return the expanded base `Instance`
- if the target is a plain non-generic nominal base with no declared mapping, synthesize an empty-argument `Instance`
- if a generic target is present but cannot be mapped accurately, raise `UnsupportedTypeOperationError`

This helper is now the common primitive behind generic nominal subtype checks and is intended to support future operations such as join, meet, substitution-aware relation checks, and runtime reflection tools.

## Union Simplification

Union simplification already used conservative subtype checks to remove redundant items. With generic base mapping in place, that behavior now applies to reflected runtime generic subclasses.

Examples:

```python
IntBox | Box[int]  -> Box[int]
Box[int] | IntBox  -> Box[int]
IntBox | Box[str]  -> IntBox | Box[str]
```

The simplifier still uses conservative behavior. Unsupported subtype relations are treated as not redundant, rather than causing simplification to fail.

## Join

`join_types()` is now a minimal high-level least-upper-bound operation.

Current behavior:

- same structural type returns the left type
- `Any` joined with anything returns `Any`
- proven subtype/supertype pairs return the supertype
- explicit unions are flattened and simplified
- supported unrelated types return a simplified union
- unsupported subtype relations raise `UnsupportedTypeOperationError`

`join_type_list()` folds `join_types()` across a list. Its empty-list identity is `UninhabitedType`.

This is intentionally much smaller than mypy's full join machinery, but it is now useful for runtime-reflected types and nominal generic subclass relationships.

## Meet

`meet_types()` is the matching minimal greatest-lower-bound operation.

Current behavior:

- same structural type returns the left type
- `Any` met with another type returns the other type
- proven subtype/supertype pairs return the subtype
- union meets distribute pairwise
- `UninhabitedType` pair results are dropped from distributed union meets
- if every distributed pair is uninhabited, the result is `UninhabitedType`
- supported unrelated types return `UninhabitedType`
- unsupported subtype relations raise `UnsupportedTypeOperationError`

`meet_type_list()` folds `meet_types()` across a list. Its empty-list identity is `AnyType(TypeOfAny.special_form)`, acting as the current top-like meet identity.

## Fail-Closed Boundaries

The split from the previous note still applies.

Public semantic operations such as subtype, join, meet, and base mapping should raise when they cannot answer accurately. Conservative helpers may choose to treat unsupported relations as false only when that is explicitly part of their contract.

Known boundaries still include:

- callable subtyping
- protocol and structural subtyping
- tuple fallback and sequence special cases
- recursive subtype assumptions
- full variance inference
- type variable solving
- complete mypy-compatible join and meet logic

## Likely Next Directions

Good next small steps:

- add substitution helpers as a public operation over the existing `expandtype` machinery
- add targeted callable join/meet failure tests before implementing callable relations
- start reflecting more runtime metadata needed for ABC relationships
- add a runtime-facing convenience API that reflects inputs and immediately computes join/meet
- begin comparing current join/meet behavior against selected mypy test cases
