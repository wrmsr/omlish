# Recursive Algorithm Strengthening

This checkpoint follows `42_Algorithm_Surface_Audit.md`.

The goal of this pass was to move from auditing algorithm gaps to tightening the machinery that recursive marshal/DI
shapes will actually hit: constraints, solve, substitution, subtype, meet, join, and runtime parity.

## Shared Recursive Corpus

The core tests now have reusable recursive alias helpers for broader algorithm coverage.

`RecursiveJsonLikeAliasCase` models a realistic data shape:

```text
Jsonish = None | bool | int | str | list[Jsonish] | dict[str, Jsonish]
```

It is intentionally richer than `int | list[Node]` because it has multiple recursive branches and several scalar leaves.
It is now used across constraint, subtype, meet, and join tests.

`RecursiveMixedTupleAliasCase` models a recursive alias with both an ordinary type variable and a type-var tuple:

```text
MixedNode[T, *Ts] = tuple[T, *Ts, MixedNode[T, *Ts]]
```

That shape proves ordinary type substitution and variadic tuple splicing compose correctly in recursive aliases.

## Constraint Inference

Constraint inference now has a structural fallback for concrete union branch matching.

Previously, recursive alias constraints like this failed:

```text
Jsonish
~ None | bool | int | str | list[Jsonish] | dict[str, Jsonish]
```

The recursive alias and one finite unrolling were structurally equivalent, but `infer_unions` matched concrete branches
with nominal `is_same_type` only. That meant branches such as `list[Jsonish]` and `list[<one unrolling>]` failed to
match even though structural equivalence already knew they described the same recursive shape.

The matcher now keeps nominal same-type as the first path and falls back to structural equivalence for concrete
constraint matching. Unsupported structural comparisons simply do not match, preserving fail-closed behavior.

New tests cover:

- JSON-like recursive alias against one unrolling in both directions;
- recursive aliases containing `Literal` and `NewType` leaves;
- repeated recursive type variable positions;
- mixed `T, *Ts` recursive aliases;
- an ambiguous structural union case that must raise rather than choose an arbitrary branch.

## Substitution Reconstruction

The constraints tests now prove solved constraints can be fed back through substitution.

For:

```text
PairNode[T] = tuple[T, T, PairNode[T]]
```

constraint inference against:

```text
tuple[int, int, PairNode[int]]
```

solves `T -> int`, then substituting into `PairNode[T]` produces a type structurally equivalent to the finite unrolling.

The same reconstruction is now covered at runtime through `typing.TypeAliasType`, using the reflected IR and reflector
structural keys.

## Mixed Variadics

The mixed recursive tuple alias demonstrates that substitution and constraints handle both normal and variadic
parameters in one recursive alias:

```text
MixedNode[T, *Ts] = tuple[T, *Ts, MixedNode[T, *Ts]]
```

Core tests now cover:

- substituting alias args: `MixedNode[T, *Ts] -> MixedNode[str, int, bool]`;
- substituting alias targets: `tuple[T, *Ts, MixedNode[T, *Ts]] -> tuple[str, int, bool, MixedNode[str, int, bool]]`;
- inferring constraints from the generic alias against one unrolling;
- solving `T -> str` and `Ts -> tuple[int, bool]`;
- substituting the solution back and comparing structurally.

Runtime tests cover the same shape using:

```python
T = typing.TypeVar('T')
Ts = typing.TypeVarTuple('Ts')
MixedNode = typing.TypeAliasType(
    'MixedNode',
    tuple[T, *Ts, 'MixedNode[T, *Ts]'],
    type_params=(T, Ts),
)
```

## Solve

`solve_constraints` now has a structural fallback for recursive alias bounds.

Nominal solving remains the first path:

- lower bounds still join through `join_type_list`;
- upper bounds still meet through `meet_type_list`;
- subtype validation still tries nominal `is_subtype` first.

If that nominal path hits a reflection type error, solving falls back to the structural variants:

- `structural_join_type_list`;
- `structural_meet_type_list`;
- `is_structural_subtype`.

This fixes repeated constraints such as:

```text
T :> Node
T :> int | list[Node]
```

where `Node` and its one unrolling are structurally equivalent but nominal recursive alias expansion cannot join them.

The fallback is deliberately narrow. It does not make solve a general structural solver in all cases; it gives recursive
alias bounds the same bounded structural treatment now used by keys, subtyping, meet, join, and constraints.

## Runtime Parity

Runtime tests now cover:

- JSON-like recursive alias constraints;
- `Literal` plus `NewType` leaves inside recursive aliases;
- repeated recursive type variable positions;
- repeated recursive alias bounds solved structurally;
- mixed `TypeVar` plus `TypeVarTuple` recursive aliases;
- substitution reconstruction through reflected IR and structural keys.

This matters because marshal entrypoints start from runtime `typing` forms, not hand-built core IR.

## Current Position

The algorithm layer now handles a more realistic recursive subset:

- structural keys and structural equivalence already had strong recursive coverage;
- constraints can match recursive alias/unrolling concrete union branches;
- solve can reconcile structurally equivalent recursive lower/upper bounds;
- substitution composes ordinary and variadic type variables in recursive aliases;
- subtype, meet, and join have shared corpus coverage for realistic recursive shapes;
- runtime tests prove the public reflection path reaches the same behavior.

Unsupported shapes still fail closed. In particular, broad callable generics, broad variadic tuple lattice operations,
and full mypy-strength recursive solving remain out of scope for this pass.

## Next Work

The next useful algorithm chunks are:

- add more cross-operation laws for recursive aliases and concrete collection shapes;
- broaden subtype/meet/join only where a marshal/DI-shaped test exposes a real gap;
- keep adding runtime parity tests beside core algorithm tests;
- start a thin old-reflection adapter spike once the current algorithm surface feels stable enough to exercise against
  marshal factory dispatch.
