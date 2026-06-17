# Constraint Inference First Pass

This checkpoint covers the work after `32_Structural_Meet_Join.md`.

The main shift was from lattice operations alone into the first useful slice of generic inference machinery. The
package now has a small but real `constraints.py` / `solve.py` surface that can infer and solve type variables from
runtime-reflected IR shapes. This is still intentionally far from full mypy constraint solving, but it gives the project
its first practical path from "template type plus actual type" to concrete type arguments.

## What Changed

New core modules now exist for constraints and solving:

- `constraints.py`;
- `solve.py`.

The constraint representation is deliberately simple. A `Constraint` records a type variable id, an operation direction,
the target type, and the original type variable object. The two directions are:

- `SUBTYPE_OF`, meaning the variable must be below the target;
- `SUPERTYPE_OF`, meaning the variable must be above the target.

The solver groups constraints by variable. Lower bounds are joined, upper bounds are met, and a candidate is accepted
only when the joined lower bound is a subtype of the met upper bound. Unconstrained variables return `Never` in strict
mode and `Any` in non-strict mode.

For ordinary `TypeVarType` variables, the solver also checks explicit allowed values and upper bounds.

## Generic Instances

Constraint inference now handles generic `Instance` values.

The supported behavior includes:

- direct `T` against `int`;
- same-origin generic instances such as `Box[T]` against `Box[int]`;
- base-instance mapping such as `Box[T]` against `IntBox` where `IntBox` inherits `Box[int]`;
- variance-aware constraints for covariant, contravariant, and invariant type parameters;
- `TypeType` wrappers by recursing into the wrapped item type.

Invariant parameters produce constraints in both directions. This matches the shape needed by runtime classes like
`list[T]`, where solving should pin the item type rather than treating it as only a lower or upper bound.

## Callable Constraints

Same-shape callable constraint inference was added.

The supported subset is intentionally aligned with the callable meet/join/subtyping subset:

- non-generic `CallableType` only;
- no ellipsis callables;
- exact argument kind/name/length shape;
- same fallback type;
- return type constraints use the requested direction;
- argument type constraints use the opposite direction because callable arguments are contravariant.

Examples now covered include `Callable[[T], T]` against `Callable[[int], int]`, both in hand-built core IR and through
runtime reflection from `collections.abc.Callable`.

Unsupported callable forms still raise `UnsupportedTypeOperationError`, including generic callables, ellipsis
callables, ParamSpec/Concatenate-derived shapes, and mismatched argument shapes.

## Alias Expansion

Constraint inference now expands non-recursive `TypeAliasType` values on either side of inference.

Generic aliases are expanded through the existing alias-target helper, so alias arguments are substituted into the alias
target before inference continues. This means a runtime alias like `Alias[T] = list[T]` can infer `T = int` against
`list[int]`.

Recursive aliases remain fail-closed for this operation. That is deliberate. Recursive aliases already participate in
structural equivalence, structural subtype checks, structural keys, and structural meet/join, but recursive constraint
solving is a separate harder problem and should not be faked by this first pass.

## Union Constraints

Constraint inference now has a conservative `UnionType` matcher.

This is not mypy's full union inference machinery. The implemented rule is strict:

- both sides must be unions with the same number of items;
- concrete template arms are matched exactly first;
- type-variable-bearing template arms are delayed;
- each delayed arm must have exactly one viable remaining actual arm;
- ambiguous or unmatched unions raise `UnsupportedTypeOperationError`.

This supports important practical forms such as:

- `T | None` against `int | None`;
- `list[T] | None` against `list[int] | None`;
- optional generic aliases such as `Maybe[T] = T | None`.

It rejects ambiguous cases such as `T | U` against `int | str`, since choosing either branch would be a guess.

## Tuple Constraints

Fixed-arity `TupleType` constraint inference was added.

The supported rule is positional and shape-strict:

- both sides must be `TupleType`;
- lengths must match;
- tuple fallbacks must match;
- each item position is inferred recursively;
- `UnpackType` and `TypeVarTupleType` tuple items fail closed for now.

Runtime tests now cover `tuple[T, str]` against `tuple[int, str]`, plus an optional tuple alias shape. Variadic runtime
tuples such as `tuple[int, ...]` are still reflected as ordinary `Instance` values of `builtins.tuple[int]`, so they are
handled, where possible, through the instance inference path rather than this fixed tuple path.

## Runtime Coverage

The runtime tests now prove that the constraint machinery works with reflected runtime objects, not just hand-built IR.

Covered runtime forms include:

- generic runtime classes and subclasses;
- covariant and contravariant runtime type variables;
- `TypeType` around reflected generics;
- generic `typing.TypeAliasType` aliases;
- `typing.Optional`;
- optional generic aliases;
- fixed tuple generics;
- same-shape callables.

This matters for the dataclass and marshal replacement use cases because the old reflection system is mostly used from
runtime annotations, not manually built type nodes.

## Current Boundaries

The current constraint implementation is intentionally narrow and fail-closed.

Important unsupported areas remain:

- recursive alias constraint solving;
- ParamSpec and Concatenate solving;
- TypeVarTuple / variadic tuple solving;
- overload constraint inference;
- protocol-member-driven constraint inference;
- TypedDict item constraint inference;
- broad mypy-style union heuristics;
- solving extra type variables from generic actual callables;
- structural constraint inference variants.

These are not accidental omissions. The current code should raise when it does not understand a shape well enough to
infer confidently.

## Current State

The core algorithm surface now includes:

- nominal and structural subtype checks;
- alpha and alpha-structural equivalence;
- recursive alias-aware structural operations;
- nominal and structural meet/join;
- direct `TypeType` lattice behavior;
- same-shape callable meet/join/subtyping;
- basic substitution and expansion;
- constraint inference for type variables, instances, aliases, unions, fixed tuples, callables, and `TypeType`;
- first-pass constraint solving.

The latest full verification run was:

```bash
.venv/bin/python -m pytest mypydistill
```

with `849 passed`.

## Immediate Goals

After the brief pivot, the next algorithm work should probably continue filling constraint coverage around shapes that
marshal and injector code will actually hit:

- add a narrow TypedDict or record-field constraint slice only if a concrete use case needs it;
- add overload or callable-default/keyword-only depth if callable dispatch needs it;
- improve alias/union inference only where current strictness blocks a real runtime shape;
- keep adding runtime tests alongside core IR tests for every inference feature.

The next larger technical target remains recursive type keys and recursive alias-aware solving. The current system has
good structural comparison/key groundwork, but recursive constraints are still explicitly out of scope.

## Mid-Term Goals

Mid-term work should keep the package pointed toward the original goal: a runtime type toolbox with enough mypy-derived
machinery to replace the old reflection system without carrying source-checker baggage.

Important mid-term areas:

- recursive alias/type-key design that can support marshal caches without old escape hatches;
- deeper substitution, expansion, and solving support;
- runtime annotation emission hardening;
- NewType identity preservation in every relevant dispatch/key path;
- in-memory cache design for reflector and inspection surfaces;
- eventual thread-safety strategy for nogil/freethreaded CPython;
- continued separation between mypyc-friendly core algorithms and runtime typing-object inspection.

The strategic posture is unchanged: keep core behavior small, explicit, and fail-closed while steadily expanding the
set of runtime type forms it can handle correctly.
