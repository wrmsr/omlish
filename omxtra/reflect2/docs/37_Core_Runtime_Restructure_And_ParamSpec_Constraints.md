# Core Runtime Restructure And ParamSpec Constraints

This checkpoint covers the work after `36_Recursive_Runtime_Keys_And_Enum_Literals.md`.

The main arc was a return to algorithmic machinery, especially constraints and solving. There was also an important
package restructure and a small memory/GC optimization for atomic type nodes.

## Package Restructure

The package layout changed to make the intended layering clearer:

```text
mypydistill/core/
    mypy-faithful type IR and algorithms

mypydistill/
    runtime reflection, runtime queries, records, members, protocols, annotations, and user-facing operations
```

The old top-level core modules moved under `mypydistill/core/`. The old `mypydistill/runtime/` modules moved to the
top-level package.

This matches the architecture we have been converging on:

- `core` is the gritty type-system layer, close to mypy's model and intended to stay mypyc-friendly.
- the top-level package is the runtime-facing layer that inspects Python `typing` objects, runtime classes, dataclasses,
  protocols, and other heap objects;
- runtime code depends on core, but core does not depend on runtime reflection.

This also reflects the likely future shape when the package moves into the larger codebase: it is a low-level
foundation below marshal, DI, dataclasses, and related systems, not a package that should know about those users.

## Atomic Type Memoization

The nullary atomic core type nodes and `AnyType` were memoized:

- `NoneType`;
- `UninhabitedType`;
- `ErasedType`;
- `EllipsisType`;
- `AnyType`, keyed by `TypeOfAny`.

This is a small allocation and GC-pressure optimization. It is semantically safe because these nodes carry no
tree-parent identity and no mutable payload. The code should continue to treat these forms structurally, using
`isinstance` and semantic comparisons rather than relying on identity. The optimization just means equivalent atoms may
share an object.

Payload-bearing or container-bearing nodes were intentionally not included. That avoids accidentally canonicalizing
forms where identity, child list mutation, alias object identity, or future metadata could matter.

## Structural Key And Lattice Coverage

The recursive structural-key work was strengthened with additional tests rather than large implementation changes.

New invariant-style tests now cover recursive structural keys involving:

- callable argument and return positions;
- overload items;
- tuple plus `TypeType` plus `Annotated`;
- NewType leaf identity inside recursive aliases;
- alpha-structural generic recursive aliases with reordered union members.

The tests assert that structural keys agree with structural equivalence for supported recursive shapes, and disagree
when structural equivalence rejects the forms.

The same idea was applied one layer up to structural subtyping, meet, and join. New tests pin that:

- non-recursive aliases are erased structurally;
- `Annotated` is ignored structurally;
- NewType identity is preserved even when supertypes match;
- literal aliases narrow in meet and widen in join against their fallback.

Most of this behavior already existed. The value of the work was making the contract explicit before building heavier
constraint and solve behavior on top.

## Constraint And Solve Work

The largest algorithmic progress since the last checkpoint was in constraint inference and solving.

### Alias And Literal/NewType Coverage

Constraint tests now explicitly cover:

- `Annotated` aliases in both template and actual positions;
- recursive aliases failing closed in actual position as well as template position;
- nested runtime-reflected collection shapes such as `Mapping[str, list[T]]` against a `TypeAliasType` for
  `Mapping[str, list[Mode]]`, where `Mode` is a literal-backed `NewType`.

This keeps the marshal/DI use cases in view: runtime callers need constraints to preserve NewType identity and to work
through practical alias and collection wrappers.

### TypeVarLike Constraints

`Constraint` and `solve_constraints` already accepted `TypeVarLikeType`, but inference only really produced constraints
for ordinary `TypeVarType`. That mismatch has been narrowed.

Constraint inference now supports direct constraints for:

- `ParamSpecType` to `Parameters` or another `ParamSpecType`;
- `TypeVarTupleType` to `TupleType`, `TypeList`, or another `TypeVarTupleType`.

Unsupported direct shapes still fail closed.

### Callable ParamSpec Constraints

Callable constraints now support reflected and hand-built forms like:

```text
Callable[P, R] against Callable[[int, str], bool]
```

The solver can infer:

```text
R -> bool
P -> Parameters([int, str], ...)
```

The implementation also supports simple `Concatenate` forms:

```text
Callable[Concatenate[int, P], R] against Callable[[int, str], bool]
```

The fixed prefix is inferred contravariantly, and the remaining actual argument shape is packed into a `Parameters`
solution for `P`.

This is deliberately not full ParamSpec solving. It does not attempt arbitrary callable compatibility, callable
subtyping with generic actual callables, or every possible `Concatenate` edge case. Unsupported forms continue to raise
`UnsupportedTypeOperationError`.

### Packed Solver Behavior

`solve_constraints` now treats `ParamSpecType` and `TypeVarTupleType` specially before the generic join/meet path.

For packed variables, solving is currently consistency-based:

- all lower and upper candidate targets must have an allowed packed shape;
- all candidates must be `is_same_type`-consistent;
- conflicting packed shapes return `None`;
- arbitrary non-packed targets return `None`.

This avoids accidentally sending `Parameters`, `TupleType`, or `TypeList` through unrelated lattice behavior before we
have a deliberate variadic lattice.

## Verification

The current suite after the restructure and constraint work is:

```bash
.venv/bin/python -m pytest -q mypydistill
```

which reports:

```text
952 passed
```

The standard gate also passes:

```bash
make fix check
```

This includes docstring fixing, ruff, flake8, and mypy.

## Near-Term Goals

The next useful work should stay algorithm-heavy rather than API-polishing.

Immediate goals:

- continue filling constraint inference gaps for callable forms, while keeping unsupported generic callable cases
  fail-closed;
- add runtime-facing tests whenever a core algorithm improvement is meant to survive reflection from `typing` objects;
- keep aligning structural equivalence, structural keys, structural subtype, meet, join, constraints, and solve;
- audit any new atomic memoization assumptions if identity-sensitive behavior appears in tests or caches;
- keep the new `core` versus runtime dependency direction clean.

Useful next slices:

- add more constraint coverage for overloads combined with ParamSpec-supported callables;
- decide whether a small helper for constructing `Parameters` from callable arg lists belongs in core;
- improve fail-closed diagnostics around callable constraint shape mismatches;
- add a few runtime tests for alias-preserved callable annotations flowing through constraints.

## Mid-Term Goals

The major mid-term goals are unchanged, but the route is clearer now.

Important goals:

- recursive alias/type-key behavior strong enough for marshal caches, including recursive aliases and alpha-equivalent
  variables;
- eventual recursive constraint solving, built on the now-stronger key/equivalence foundation;
- broader mypy-derived algorithm coverage: constraints, solve, meet, join, subtyping, expansion, substitution, and
  eventually inference helpers;
- runtime reflection that can serve as a practical drop-in replacement for the old reflection system in dataclass,
  marshal, and injector use cases;
- NewType identity preservation wherever runtime systems need nominal dispatch;
- runtime annotation emission policies that remain explicit and cache-friendly;
- later cache/thread-safety design, including in-memory runtime reflection caches suitable for high-frequency entrypoint
  calls and eventual free-threaded Python.

Nice-to-have later:

- fuller callable/ParamSpec/Concatenate semantics;
- TypeVarTuple support beyond direct packed constraints;
- protocol checking closer to mypy semantics;
- a public API pass after the package is closer to its final in-repo location.
