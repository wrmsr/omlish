# Near Term Fundamentals

This checkpoint records a small fundamentals-focused pass after `26_Runtime_Dispatch_Surface.md`.

The intent of this pass was to step back from runtime API convenience and strengthen lower-level behavior that should
survive a later move into the real codebase. The main areas were type-key coverage, callable/member signature facts,
and runtime annotation robustness.

## Type-Key Coverage

`TypeKey` support now covers more of the core IR directly.

Newly keyed nodes include:

- `Overloaded`;
- `UnboundType`;
- `CallableArgument`;
- `TypeList`;
- `UnpackType`;
- `ErasedType`;
- `DeletedType`;
- `Parameters`;
- `TypedDictType`;
- `RawExpressionType`;
- `EllipsisType`;
- `PlaceholderType`.

`PartialType` remains intentionally unsupported and is now used by tests that need a still-unkeyable node. This keeps
fail-closed behavior visible without relying on nodes that now have deterministic keys.

Overload keys preserve item order. This matches the practical semantics of overload resolution: a reordered overload set
is not assumed equivalent by the key system.

TypedDict keys sort item names and key sets so construction order does not affect the key. This does not make TypedDict
a priority for the target application code, but it closes a hole where the runtime reflector could already produce an
IR node that could not be keyed.

## Callable And Member Signatures

The member inspection model already recorded `inspect.Parameter.kind` and default presence. Tests now explicitly lock
that down for positional-only, positional-or-keyword, keyword-only, and defaulted parameters.

Member signature keys also now have tests proving that parameter kind and default presence affect key identity. This is
important for dependency-injection-style callers where call surfaces are meaningful even when the raw annotation types
are otherwise the same.

Overload behavior is now pinned down more explicitly:

- overload equality and alpha-equivalence preserve overload item order;
- an overload is a subtype of itself through exact type matching;
- nontrivial overload subtyping fails closed for now;
- meet and join support exact overload matches and fail closed for different overloads or overload/callable pairs;
- runtime member inspection preserves overload order through reflected call signatures and signature keys.

This keeps overload handling usable for identity, keying, and diagnostics while avoiding a premature partial
implementation of mypy's overload-callable subtyping rules.

Simple callable subtyping now has a bounded first implementation. It supports non-generic `CallableType` pairs with
matching argument kinds, names, ellipsis state, and arity. Arguments are checked contravariantly and return types
covariantly. `Callable[..., R]` ignores arguments and compares only the return type.

Generic callable forms, including ParamSpec-shaped callables, still fail closed unless they are exactly the same type.
This keeps the implementation useful for common runtime `Callable[[A], B]` shapes without pretending to implement the
full mypy callable and overload subtyping model.

## Runtime Annotation Emission

Callable annotation emission now recognizes equivalent ParamSpec nodes by type-variable id rather than requiring the
two `ParamSpecType` nodes used for `*args` and `**kwargs` to be the same Python object.

This matters for copied, substituted, or reconstructed IR. A direct reflection of `Callable[P, R]` naturally reuses the
same object in both positions, but the core should not depend on that identity shortcut for correctness.

## Recursive Alias Comparison

Recursive alias comparison now keeps checking alias arguments when it sees an already-assumed alias pair.

The previous coinductive shortcut treated an already-assumed pair as immediately equal. That is safe for the recursive
cycle itself, but too broad for parameterized backrefs: `A[int]` and `B[str]` inside an assumed `A`/`B` cycle must still
compare their arguments. The comparison now returns to the assumption only after the current backref arguments match.

The recursive alias tests now also cover:

- corresponding entrypoints in equivalent mutually recursive alias graphs;
- the fact that different entrypoints in the same mutual graph produce different stack-relative keys today;
- alpha keys for parameterized mutually recursive aliases with different type-variable names;
- rejection of mismatched recursive backref arguments;
- runtime-reflected `typing.TypeAliasType` recursive aliases, not only hand-built IR.

This is still not the final recursive key design. Mutually recursive graph canonicalization remains a future problem,
but the current behavior is now more explicitly pinned down.

## Current Boundary

This pass did not attempt to finalize public runtime APIs. The current query and dispatch helpers are still scaffolding
for tests and integration experiments.

## Core Operation Audit

The copy, expansion, substitution, subtype, meet, join, and runtime annotation paths now have more explicit
fail-closed coverage.

`copy_type`, `expand_type`, and `substitute_type` are covered across newer IR nodes that matter for later callable and
generic work: overloads, parameters, callable arguments, type lists, unpack, TypedDict, placeholders, and aliases inside
callable items. Expansion still preserves callable type variables rather than substituting the callable's own
`variables` list, matching the current shallow model.

`meet` and `join` now normalize `TypeGuardedType` and `AnnotatedType` before exact/subtype checks. This removes a side
dependent inconsistency where wrapper nodes could be returned from one operand order but not another. Other wrappers
such as `RequiredType`, `ReadOnlyType`, `UnpackType`, and `TypeType` remain fail-closed for subtype, meet, and join.

Runtime annotation emission now has explicit failure tests for unsupported IR nodes and mismatched ParamSpec
`*args`/`**kwargs` pairs. Unsupported forms raise `TypeError`; optional APIs are the only places that should suppress
unsupported behavior.

The main remaining near-term fundamentals are:

- recursive alias/type-key behavior beyond the current stack-relative model;
- broader callable operation semantics, especially where overloads need to participate in subtype and assignability
  operations;
- more tests around fail-closed behavior for unsupported operation combinations;
- cache design work that preserves the current fast-path behavior while leaving room for later thread-safe
  implementation.

After those, the project is closer to the mid-term work: native recursive type support, deeper mypy-derived operations,
and eventually experimental in-repo adoption below marshal, DI, and other higher-level packages.
