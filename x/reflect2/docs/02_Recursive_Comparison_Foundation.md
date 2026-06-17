# Recursive Comparison Foundation

This note records the second implementation phase after the core skeleton. It covers the first real type operations added on top of visitors, traversal, and stringification.

## New Core Modules

Several small operation modules now exist in the core layer:

- `expandtype.py`
- `copytype.py`
- `subtypes.py`

These are still intentionally narrow. They provide enough behavior to start exercising type operations while avoiding full mypy checker semantics.

## Type Variable Expansion

`expandtype.py` adds a first substitution operation:

- `expand_type(typ, env)`
- `ExpandTypeVisitor`

The environment can map either a `TypeVarId` or a `TypeVarLikeType` object to a replacement `Type`.

Current supported behavior:

- Replaces `TypeVarType` directly.
- Replaces `ParamSpecType` and `TypeVarTupleType` only when directly mapped.
- Recurses through composites via `TypeTranslator`.
- Rewrites alias arguments while preserving the alias definition object and target.
- Preserves unmapped type variables.

This is not yet mypy's full `expandtype.py`. Complex ParamSpec, TypeVarTuple, and unpack behavior are intentionally deferred.

## Type Copying

`copytype.py` adds explicit type-node copying:

- `TypeCopier`
- `copy_type()`
- `copy_types()`

This is implemented as a thin wrapper over `TypeTranslator`.

Current copy semantics:

- Composite type nodes are rebuilt recursively.
- Metadata objects such as `TypeInfo` and `TypeAlias` are shared.
- Atomic nodes are preserved by identity for now.
- The copied type tree should have the same debug string as the original.

This is different from mypy's exact shallow copier, because the current skeleton does not yet have mypy's source/truthiness fields and because a recursive node copier is more immediately useful for the current operations.

## Same-Type Comparison

`subtypes.py` now contains the first comparison primitive:

- `is_same_type(left, right)`
- `is_equivalent(left, right)`

Despite the module name, this is not full subtyping yet. `is_equivalent()` is currently just an alias for `is_same_type()`.

The comparison supports the current skeleton nodes structurally, including:

- atomic types
- type variables by `TypeVarId.raw_id` and `meta_level`
- instances by `TypeInfo` identity and argument structure
- callables by argument kinds, names, argument types, return type, variables, and fallback
- tuples
- typed dicts
- literals
- wrappers such as `RequiredType`, `ReadOnlyType`, and `TypeGuardedType`
- order-insensitive unions
- aliases

This operation intentionally remains separate from Python `__eq__` on the type nodes.

## Alpha-Equivalence

`subtypes.py` also adds:

- `is_alpha_equivalent(left, right)`

This is a separate comparison mode from `is_same_type()`. It allows type variables with different IDs or names to be considered equivalent when they appear in corresponding positions.

The comparer tracks a bidirectional mapping between left and right type variable IDs. This means repeated variables must stay consistent:

- `Box[T]` can alpha-compare equal to `Box[U]`.
- `Callable[[T], T]` can alpha-compare equal to `Callable[[U], U]`.
- `Pair[T, T]` does not alpha-compare equal to `Pair[T, U]`.

This is one of the first direct steps toward the original goal of canonical/structural type equivalence with different variable names.

## Recursive Alias Detection

`typeops.py` now has basic alias traversal and recursive alias detection:

- `collect_aliases(typ)`
- `is_recursive_alias(alias)`
- `RecursiveTypeError`

`TypeAliasType` now has an `is_recursive` property. The result is cached on `TypeAlias._is_recursive`.

The recursive check is alias-identity based. It supports:

- non-recursive aliases
- direct recursive aliases
- indirect alias cycles

`get_proper_type()` is now recursion-aware. It raises `RecursiveTypeError` instead of expanding recursive aliases indefinitely.

`flatten_nested_unions()` now accepts `handle_recursive`. With `handle_recursive=False`, it preserves recursive aliases instead of expanding them. With the default behavior, recursive alias expansion fails cleanly.

## Recursive Alias Comparison

`subtypes.py` now has a first narrow coinductive comparison mechanism for recursive aliases.

The comparer tracks assumed alias pairs during recursive comparison. When it sees the same pair again, it treats that recurrence as provisionally equal, allowing comparison to terminate.

Current behavior:

- A recursive alias compares equal to itself.
- Two different recursive aliases with structurally equivalent targets compare equal.
- Recursive aliases with different base structure do not compare equal.
- This is scoped to comparison only; `get_proper_type()` still rejects recursive expansion.

This is not a full final recursive type theory, but it establishes the first practical mechanism needed for recursive equivalence.

## Test Status

The package test suite currently covers:

- core skeleton class list
- traversal
- query aggregation
- type operations
- string conversion
- translation
- expansion/substitution
- copying
- same-type comparison
- alpha-equivalence
- recursive alias detection
- recursive alias comparison

Current test command:

```bash
.venv/bin/python -m pytest mypydistill/tests
```

At the time of this note, the suite reports 50 passing tests.

## Current Boundaries

The work is still entirely in the core layer. Runtime reflection from Python `typing` objects has not started yet.

Full subtyping has not started yet. The current `subtypes.py` provides equality-style operations only.

Recursive comparison is intentionally narrow. It handles recursive alias pairs during structural comparison but does not yet support all cases mypy handles through subtype assumptions, tuple fallback logic, or alias expansion machinery.

## Likely Next Steps

Good small next steps include:

- Add a tiny `maptype.py` or generic instance helper for mapping an `Instance` to a supertype using `TypeInfo.bases`.
- Add basic variance-aware instance argument comparison as a preparatory step toward subtyping.
- Add `erasetype.py` with simple erasure of type variables to `Any` or upper bounds.
- Start a `runtime/` package with only a synthetic universe for builtin `TypeInfo` objects, before reflecting real `typing` forms.

The next choice depends on whether the immediate priority is to continue core algorithms or begin bridging runtime Python objects into the IR.
