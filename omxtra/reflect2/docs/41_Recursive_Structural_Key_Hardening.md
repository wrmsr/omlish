# Recursive Structural Key Hardening

This checkpoint follows `40_Recursive_Alias_Near_Term_Closure.md`.

The focus of this pass was the first mid-term goal: make recursive structural keys robust enough to serve as the
foundation for marshal caches. The work was intentionally mostly tests. The key builder already had the main machinery:
alias-erased structural policy, alpha variable canonicalization, recursive alias backrefs, union order normalization,
opaque union buckets, and reflector-level key caches. The missing piece was a tighter regression corpus proving those
pieces behave together under realistic recursive shapes.

## Why This Matters

Marshal cache keys need to answer a narrower question than source-level type checking:

```text
Do these runtime type forms describe the same reflected shape for dispatch/cache purposes?
```

For this project, the answer must:

- erase runtime alias object identity for structural keys;
- preserve `NewType` identity by default;
- ignore `Annotated` metadata by default, matching mypy's structural behavior;
- optionally preserve `Annotated` metadata through `TypeKeyPolicy`;
- canonicalize alpha-equivalent variables when requested;
- treat recursive aliases and finite unrollings as the same structural shape;
- keep union order irrelevant, including when some union members require opaque key payloads;
- fail closed when alias expansion cannot be trusted.

That combination is the practical replacement for the old marshal escape hatch where callers could install arbitrary
reflection sentinels to break recursive loops manually.

## Core Structural Key Invariants

`mypydistill/core/tests/test_typekeys.py` now has a JSON-like recursive alias corpus:

```text
Jsonish = None | bool | int | str | list[Jsonish] | dict[str, Jsonish]
```

The test uses shared `TypeInfo` identities for the builtin leaves, matching how the runtime universe reflects builtin
classes. It proves that:

- the alias matches its target;
- the alias matches one deeper unrolling;
- a differently named alias with reordered union branches matches the same key;
- unrolled forms from both aliases compare structurally.

This is a better marshal-cache proxy than the older `int | list[Node]` tests because it has multiple recursive branches
and a realistic data-shape union.

The core tests also now pin repeated variable positions:

```text
LeftPair[T] = tuple[T, T, LeftPair[T]]
RightPair[U] = tuple[U, U, RightPair[U]]
WrongPair[U, V] = tuple[U, V, WrongPair[U, V]]
```

`LeftPair[T]` and `RightPair[U]` have the same alpha-structural key. `WrongPair[U, V]` does not. This matters because
alpha equivalence is not just "rename every variable"; repeated positions must stay repeated.

## Policy Boundaries

The default structural policy continues to erase `Annotated` metadata. A separate test now proves the knobs remain
independent when recursion is involved:

```text
MetaNode = int | Annotated[list[MetaNode], ('cfg', 1.5)]
```

The default structural key equals the annotation-erased unrolling. A custom `TypeKeyPolicy` with
`include_annotated_metadata=True` keeps the metadata and still produces deterministic recursive union keys. If metadata
is unhashable under that policy, keying returns `None` and the strict entrypoint raises `ReflectionError`.

That gives callers room to opt into metadata-sensitive cache keys later without changing the default marshal-friendly
policy.

## Runtime Cache-Facing Coverage

`mypydistill/tests/test_ops.py` now has runtime equivalents built from real heap `typing.TypeAliasType` forms.

The JSON-like alias test proves:

- `reflect_is_structurally_equivalent` recognizes differently named recursive aliases with reordered branches;
- structural keys match aliases and unrolled runtime forms;
- repeated reflection of the same alias reuses the reflected `Type`;
- `structural_type_key` and `structural_type_key_or_none` reuse the reflector's cached key object.

The repeated-variable runtime test mirrors the core `Pair` shape and proves alpha-structural keying preserves variable
position shape through forward references and runtime `TypeVar` objects.

This is the important hot path for marshal-style calls such as:

```python
msh.unmarshal(value, SomeRecursiveAlias[int])
```

The cache key can now be computed from the runtime form and compared with equivalent aliases or finite unrollings.

## Opaque Union Members

String-squashed keys intentionally do not stringify every literal value. Float literals are valid literal values, but
they are kept as opaque key payloads rather than compact scalar text.

This pass added recursive alias tests with float literal union members:

```text
FloatNode = Literal[1.5] | Literal[2.5] | list[FloatNode]
```

The core and runtime tests prove that reordered literal branches and recursive branches still produce the same
structural key. This pins the opaque union bucket behavior in the recursive case, where deterministic ordering matters
for cache-grade keys.

## Fail-Closed Expansion

The previous suite already covered unsupported recursive targets. This pass added a narrower alias-expansion failure:
a recursive generic alias encountered with the wrong number of arguments.

For a shape like:

```text
BadGeneric[T] = list[BadGeneric[T]]
```

the malformed internal form `BadGeneric[int, str]` now has explicit coverage:

- `structural_type_key_or_none` returns `None`;
- `alpha_structural_type_key_or_none` returns `None`;
- strict key functions raise `ReflectionError`;
- reflector-level `_or_none` caches remember `None` and do not populate strict key caches.

That is the intended behavior while this system is incremental: unsupported or malformed recursive forms must not get
approximate keys.

## Current Position

Recursive structural keys are now substantially better covered as a cache primitive:

- alias identity is erased where intended;
- alpha-equivalent variables are canonicalized without losing repeated-position information;
- realistic recursive JSON-like aliases work through core and runtime surfaces;
- finite unrollings key the same as the recursive alias;
- float literal opaque payloads remain order-insensitive inside recursive unions;
- malformed recursive alias expansion fails closed and caches `None`.

This does not mean the recursive type engine is complete. It means the currently supported recursive subset is now
better specified and safer to use as the next marshal-cache foundation.

## Next Near-Term Work

The next practical step is to move back into mypy-derived algorithms and make sure the key/equivalence foundation can
support real operations:

- improve constraints and solve for recursive generic shapes beyond the current bounded cases;
- keep substitution and expansion aligned with recursive alias keying;
- broaden subtype, meet, and join only where marshal/DI shapes need them;
- add negative tests whenever a new recursive algorithm path remains intentionally unsupported.

## Mid-Term Direction

The larger direction remains:

- use these structural keys in a thin old-reflection adapter or spike, without pulling in marshal internals;
- measure whether module-global runtime type forms hit reflector caches predictably;
- keep the default key policy marshal-friendly while preserving policy knobs for metadata-sensitive or NewType-erasing
  callers;
- revisit thread-safe cache storage after the single-threaded semantics are stable;
- continue moving toward native recursive alias support so old sentinel override hacks become unnecessary.
