# Fail Closed Unsupported Operations

This note records the current policy for operations that are only partially implemented.

## Motivation

The package is being built iteratively. During that process, a public operation should not silently answer a semantic question it does not understand. In particular, a subtype or comparison function returning `False` can mean two different things:

- the relation is known to be false
- the implementation does not know how to decide the relation yet

Those need to be separated.

## Error Surface

Named fail-closed errors live in `errors.py`.

- `TypeIrError` is the shared package-local base error.
- `UnsupportedTypeOperationError` is for semantic operations that are outside the implemented core type machinery.
- `UnreflectableTypeError` is for runtime annotation objects that the reflection layer cannot turn into IR nodes.

Both named specific errors are also `TypeError` subclasses, so callers can catch either the narrow package errors or ordinary type-operation failures.

## Runtime Reflection

Runtime reflection is fail-closed for unsupported runtime forms.

Unsupported objects, unsupported callable shapes, unsupported wrappers, malformed `type[...]` arguments, and unsupported literal payloads raise `UnreflectableTypeError`.

This gives callers a way to distinguish an unhandled runtime annotation form from an ordinary internal programming error.

## Same-Type Comparison

Structural same-type comparison is intended to be exhaustive over the current IR node classes.

Unknown future `Type` subclasses now raise `TypeError`, even when compared against a known type. For implemented node classes, structural inequality still returns `False`.

This means adding a new node type should force an explicit comparison decision instead of silently falling through to a misleading answer.

## Subtyping

Subtyping has a strict public API and a conservative helper.

`is_subtype` is strict. It raises `UnsupportedTypeOperationError` when the relation is outside the currently implemented subtype fragment.

`is_subtype_or_false` is conservative. It calls `is_subtype`, catches `UnsupportedTypeOperationError`, and returns `False`. It is intended for internal best-effort algorithms that should only act on relations they understand.

The implemented subtype fragment currently includes:

- same-type relation
- `Any` compatibility in both directions
- `TypeGuardedType` unwrapping
- union rules
- nominal `Instance` checks through `TypeInfo.mro`
- same-target generic `Instance` checks using declared variance

It explicitly does not yet implement generic base argument mapping, callable subtyping, protocols, tuple fallback logic, promotions, recursive subtype assumptions, or most special forms.

## Conservative Internal Use

Some internal algorithms need conservative behavior instead of strict failure. `make_simplified_union` is the main current example.

Union simplification should remove an item only when redundancy is understood. If a subtype relation is unsupported, simplification treats it as not redundant and keeps the item. This is handled through `is_subtype_or_false`.

This keeps public API behavior fail-closed while preserving safe simplification behavior.

## Direction

As more of mypy's subtype machinery is ported, unsupported cases should become implemented cases. Until then, public semantic queries should raise rather than guess.

Good future follow-ups:

- add strict/conservative helper pairs where more APIs need both modes
- audit same-type comparison for cases where structural inequality is being used to stand in for unsupported semantics
- expand tests that assert unsupported relations raise, especially around recursive aliases, callable types, and generic base mapping
- keep runtime reflection errors specific as new runtime-only forms are added
