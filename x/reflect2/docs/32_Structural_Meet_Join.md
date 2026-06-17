# Structural Meet Join

This checkpoint covers the algorithm and runtime work after `31_Runtime_Parity_And_Callable_Subtyping.md`.

The main arc was to keep moving away from a runtime normalizer and toward a useful type-operation toolbox. The recent
work strengthened `TypeType`, callables, meet/join, and recursive aliases while keeping the nominal and structural
surfaces explicitly separated.

## What Changed

`TypeType` now participates in subtype, meet, and join operations.

The implemented rule is intentionally narrow and mypy-aligned: `type[Child]` is a subtype of `type[Base]` when `Child`
is a subtype of `Base`. The broader mypy behavior around constructor callables, metaclasses, and `TypeForm` is still out
of scope. Unsupported item relations still fail closed.

Meet and join now handle class-object types directly:

- `meet(type[Child], type[Base])` produces `type[Child]`;
- `join(type[Child], type[Base])` produces `type[Base]`;
- unrelated class-object meets produce `type[Never]`;
- unrelated class-object joins produce `type[Union[A, B]]`;
- union meet distribution treats `type[Never]` as empty, just like `Never`.

This gives class-object forms enough lattice behavior to be useful without pretending constructor signatures are solved.

## Callable Meet And Join

Same-shape, non-generic callables now have synthesized meet and join results instead of only benefiting from subtype
short-circuiting.

For eligible callables, the implemented behavior is:

- callable meet joins argument types contravariantly and meets return types covariantly;
- callable join meets argument types contravariantly and joins return types covariantly;
- argument names and kinds are preserved when the shape matches exactly;
- generic callable, ellipsis callable, ParamSpec, Concatenate, varargs, and mismatched shapes remain conservative.

This is still not the full mypy callable matrix. It is a small useful subset that supports normal callback-like forms
while keeping hard cases visible.

## Structural Meet And Join

New core structural entrypoints were added:

- `structural_meet_types`;
- `structural_meet_type_list`;
- `structural_join_types`;
- `structural_join_type_list`.

The nominal entrypoints remain unchanged:

- `meet_types`;
- `meet_type_list`;
- `join_types`;
- `join_type_list`.

The implementation was refactored so nominal and structural operations share the same meet/join algorithm body. The
difference is which subtype and equivalence predicates are threaded through recursive calls:

- nominal operations use `is_subtype` and `is_same_type`;
- structural operations use `is_structural_subtype` and `is_structurally_equivalent`.

That mode is preserved through recursive calls, `TypeType`, union simplification, callable synthesis, and TypedDict
item handling.

Structural union simplification uses structural subtype/equivalence, so recursive aliases and finite unrollings can
collapse correctly in structural mode without changing nominal behavior.

## Recursive Alias Behavior

The structural meet/join tests now cover recursive aliases directly:

- `Node = int | list[Node]` structurally meets and joins with `int | list[Node]`;
- two different aliases with the same recursive structure compare structurally through meet/join;
- incompatible recursive aliases meet to `Never`;
- incompatible recursive aliases join to a union of the alias forms;
- unsupported recursive callable targets still fail closed.

This is not a complete recursive type engine, but it is a meaningful step: recursive alias equivalence, structural keys,
structural subtyping, and structural meet/join now point in the same direction.

## Runtime Structural Ops

The runtime layer now exposes explicit structural meet/join operations:

- `reflect_structural_meet`;
- `reflect_structural_meet_list`;
- `reflect_structural_join`;
- `reflect_structural_join_list`.

The existing `reflect_meet` and `reflect_join` entrypoints remain nominal. This keeps behavior stable while making the
new structural operations reachable from runtime `typing` forms.

Runtime tests cover:

- recursive `typing.TypeAliasType` values against finite unrollings;
- different runtime alias identities with equivalent recursive structure;
- incompatible recursive aliases;
- list folds;
- fail-closed recursive ParamSpec callable aliases.

## Runtime Views

No new view or facade API was added.

Instead, tests now prove that `RuntimeTypeView` composes with the runtime structural operations. A caller can perform a
structural meet or join, then use `get_runtime_type_view` on the resulting IR node and get coherent shape, dispatch, and
key facts.

This keeps the runtime view layer as a small bundle over existing query APIs rather than turning it into a larger
operation facade prematurely.

## Current State

The core algorithm surface is now stronger in several practical areas:

- nominal instance subtyping and variance;
- structural and alpha-structural equivalence;
- recursive alias-aware structural subtype checks;
- structural keys for recursive aliases and unrollings;
- nominal and structural meet/join;
- direct `TypeType` support;
- a useful same-shape callable meet/join subset;
- runtime entrypoints for both nominal and structural meet/join.

The latest full verification run was:

```bash
.venv/bin/python -m pytest mypydistill
```

with `806 passed`.

## Current Boundaries

Important limits remain:

- callable compatibility is still intentionally partial;
- overload subtyping and overload meet/join are still mostly fail-closed;
- ParamSpec and Concatenate are reflected but not deeply solved by core operations;
- recursive meet/join is practical for current alias/unrolling shapes, not full mypy-strength recursion;
- constraints, solve, and inference are still mostly ahead of us;
- runtime cache thread safety remains a known future issue;
- public API organization remains deliberately unsettled while the package is still expected to move in-repo.

The recent style direction is also worth carrying forward: raw dataclass fields may increasingly become private with
public getters, while internal implementation code can still use private fields directly when that is the clearer and
cheaper path.

## Immediate Goals

The next useful technical direction is a minimal constraints/solve assessment and first slice.

Before implementing too much, inspect the current `constraints.py` and `solve.py` state, compare the relevant small
parts of mypy, and identify a narrow runtime-relevant case. A good first target is likely inference against simple
generic instances or callables where the existing subtype/meet/join behavior already has enough support.

Other near-term options:

- add a small amount of overload subtyping or overload join/meet if constraints are still too early;
- add structural meet/join runtime tests around generic dataclass field replacement if a concrete marshal-style usecase
needs it;
- continue hardening fail-closed behavior for recursive unsupported nodes.

## Mid-Term Goals

Mid-term work should keep deepening the mypy-derived core while staying runtime-oriented:

- build a minimal but real constraint collection path;
- add a first solving pass that can support common generic runtime forms;
- keep recursive alias equivalence, structural keys, structural subtyping, and structural meet/join aligned;
- decide later whether runtime structural meet/join should become default behavior for selected high-level helpers;
- preserve the core/runtime split so algorithm-heavy modules remain plausible mypyc candidates;
- revisit cache and thread-safety design after operation surfaces stabilize further.

The strategic direction remains the same: avoid API polish and adapter finalization until the core algorithms can carry
more weight.
