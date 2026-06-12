# Overloads NewTypes And Constraint Depth

This checkpoint covers the work after `33_Constraint_Inference_First_Pass.md`.

The recent arc continued strengthening the mypy-derived algorithm machinery, with emphasis on areas that marshal,
dataclass, and injector-style runtime users are likely to care about: literal values, NewType identity, overloads,
callables, and fail-closed constraint behavior.

## Import And Symbol Style

A source policy changed during this stretch: new and touched code should import individual items rather than importing
the `types` or `symbols` modules wholesale.

New focused tests and core edits now follow that policy. Some older large test modules still use the old style, but
recent additions avoid extending it.

The old c-style integer constants for argument kinds and variance were also moved to enum classes:

- `ArgKind`;
- `VarianceKind`.

Core algorithm code was adjusted to compare enum values directly, typically with identity checks.

## Literal And NewType Tightening

The constraint and subtype layers were tightened around concrete leaves.

Previously, concrete leaf constraint inference could return an empty constraint list even when two concrete leaves were
not actually the same. That is unsafe because an unsupported or mismatched concrete form can look like a successful
"nothing to infer" result.

The new behavior is stricter:

- matching concrete leaves still produce no constraints;
- mismatched concrete leaves raise `UnsupportedTypeOperationError`;
- this is especially important for `LiteralType`, where values matter.

`LiteralType` now participates in subtype checks through its fallback:

- `Literal['x'] <: str`;
- `Literal['x'] <: object`;
- `Literal['x']` is not a subtype of `Literal['y']`;
- `str` is not a subtype of `Literal['x']`.

Runtime NewType handling was also corrected for bound validation. Class-backed NewTypes already inherited from their
runtime class supertype, but literal-backed NewTypes such as `NewType('Mode', Literal['a', 'b'])` had no base. They now
fall back to `object` as a base, preserving nominal NewType identity while still validating against the default object
upper bound of runtime type variables.

Known runtime MRO data was expanded for primitive builtins:

- `builtins.type`;
- `builtins.None`;
- `builtins.bool`;
- `builtins.int`;
- `builtins.float`;
- `builtins.complex`.

This made `NewType('UserId', int)` validate correctly as a subtype of `object`, because the reflected `int` chain now
continues to `object`.

New focused tests cover:

- literal subtype behavior;
- NewType assignability to supertype and object;
- distinct NewTypes staying nominally distinct;
- NewType type keys preserving identity;
- literal and NewType shapes through constraint inference.

## Overload Constraint Inference

Overload constraint inference now has two narrow supported directions.

First, `Overloaded` template against `CallableType` actual is supported. Each overload item is tried against the actual
callable using the existing callable constraint inference path. Exactly one item must match:

- zero matches raises;
- multiple matches raises;
- one match returns that item's constraints.

Second, `CallableType` template against `Overloaded` actual is supported. The template is inferred against every
overload item, and all constraints are concatenated. This leaves compatibility of the resulting bounds to the existing
solver:

- covariant return constraints can join to a union;
- contravariant argument constraints can meet down to `Never`;
- unsupported overload item shapes still raise.

`Overloaded` against `Overloaded` constraint inference remains unsupported for now. That is intentional. Pairwise
overload constraint solving has more semantic choices and should not be smuggled in through a broad fallback.

## Overload Subtyping

Ordered pairwise overload subtyping was added.

The supported rule is deliberately strict:

- both sides must be `Overloaded`;
- item counts must match;
- items are compared in order;
- each item pair uses existing callable subtyping;
- overload-vs-callable remains unsupported.

This does not implement mypy's full overload compatibility semantics. It is a small, predictable subset that supports
same-shape overload families without introducing overload selection or reordering.

Mismatched item counts fail closed. Ordered item mismatches return `False` when the callable item comparisons are
understood.

## Overload Meet And Join

Ordered pairwise overload meet and join were added after the subtype behavior was pinned down.

The supported rule mirrors overload subtyping:

- both sides must be `Overloaded`;
- item counts must match;
- items are combined in order;
- each pair must be a callable pair supported by the same-shape callable meet/join machinery;
- the result is a new `Overloaded` containing synthesized callable items.

Unsupported overload shapes raise `UnsupportedTypeOperationError`. Overload-vs-callable remains unsupported.

This intentionally preserves the limited scope. There is no overload reordering, no best-match selection, and no
overload-vs-overload constraint inference yet.

## Runtime Surface Impact

Most of this round was core algorithm work rather than runtime API work.

Runtime behavior was affected in a few important ways:

- reflected NewTypes over literal/type-form supertypes now have `object` as a fallback base;
- primitive known-type MROs now include object tails;
- runtime constraints involving NewType and Literal values now solve through default object bounds correctly;
- runtime assignability tests now cover NewType-to-supertype, NewType-to-object, and distinct NewType rejection.

The key runtime promise remains: NewType identity is preserved for keys, dispatch, annotation emission, and nominal
comparison, even when the NewType is assignable to a broader supertype.

## Current State

The core operation surface now includes:

- nominal and structural subtype checks;
- alpha and alpha-structural equivalence;
- recursive alias-aware structural operations;
- nominal and structural meet/join;
- direct `TypeType` lattice behavior;
- same-shape callable subtyping, meet, and join;
- ordered pairwise overload subtyping, meet, and join;
- basic substitution and expansion;
- constraint inference for type variables, instances, aliases, unions, fixed tuples, callables, overload-template vs
  callable-actual, callable-template vs overload-actual, and `TypeType`;
- first-pass constraint solving;
- literal and NewType behavior aligned with runtime use cases.

The latest full verification run was:

```bash
.venv/bin/python -m pytest mypydistill
```

with `883 passed`.

## Current Boundaries

Important unsupported areas remain:

- recursive alias constraint solving;
- recursive type-key design for cache equivalence in the hardest cases;
- ParamSpec and Concatenate solving;
- TypeVarTuple / variadic tuple solving;
- overload-vs-overload constraint inference;
- overload reordering or best-match semantics;
- overload-vs-callable subtyping, meet, and join;
- protocol-member-driven constraint inference;
- TypedDict item constraint inference;
- broad mypy-style union heuristics;
- structural constraint inference variants;
- thread-safe cache design.

These boundaries remain intentionally fail-closed. Unsupported algorithm shapes should raise rather than returning
misleading `True`, `False`, or empty constraints.

## Immediate Goals

The next useful work can go in a few directions.

Short-term algorithm options:

- add one more narrow constraint slice, such as TypedDict item constraints, only if a concrete runtime use case justifies
  it;
- add overload-vs-overload constraint inference in a very strict ordered pairwise form;
- harden callable forms around keyword-only/default-like shapes if runtime signatures need it;
- add structural variants of selected constraint operations only when there is a real consumer.

Short-term safety options:

- add more tests around fail-closed behavior for unsupported recursive aliases in constraints;
- audit legacy tests that still use old import style only when touched for behavior changes;
- add targeted tests for enum-based variance and argument kind comparisons where a future refactor could regress.

## Mid-Term Goals

The strategic mid-term goals are mostly unchanged:

- design and implement recursive alias/type-key behavior strong enough for marshal caches;
- align recursive structural equivalence, structural subtype, structural keys, and eventual recursive solving;
- continue expanding mypy-derived operations without importing source-checker assumptions;
- keep runtime reflection separate from mypyc-friendly core algorithms;
- preserve NewType identity in all user-visible and cache-relevant surfaces;
- revisit in-memory caching and thread-safety once the operation surfaces stabilize.

The package is now more than a runtime normalizer. It has a growing core algorithm layer that can infer, solve, compare,
join, meet, and substitute over a useful set of runtime-reflected type forms. The next larger step is deciding how much
more incremental constraint work to do before returning to recursive alias/type-key design.
