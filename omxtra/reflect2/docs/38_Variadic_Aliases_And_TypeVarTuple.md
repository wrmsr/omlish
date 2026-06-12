# Variadic Aliases And TypeVarTuple

This checkpoint covers the work after `37_Core_Runtime_Restructure_And_ParamSpec_Constraints.md`.

The main arc was taking the packed-variable work from the previous checkpoint and making it reachable from realistic
runtime `typing` forms. The core constraint solver already had basic `ParamSpec` and `TypeVarTuple` slots; this round
filled in more callable coverage, tuple variadic inference, runtime `TypeVarTuple` reflection, variadic alias
substitution, and cache/key tests around the new shapes.

## Callable And Overload Constraints

The callable constraint work from the previous checkpoint was tightened with more tests rather than broad new
semantics.

New coverage now pins:

- overload selection where the selected item contains `Callable[P, R]`;
- overload selection where the selected item contains `Callable[Concatenate[..., P], R]`;
- fail-closed behavior when multiple ParamSpec overload items match;
- ParamSpec packing for mixed argument shapes, including positional, optional positional, named, and optional named
  arguments;
- `Concatenate` preserving the remaining argument kinds and names after the fixed prefix;
- overload selection by named prefix shape, not only by positional type.

The implementation already handled most of this through the existing single-matching-overload path. The value of the
work was making that contract explicit before extending packed-variable behavior further.

## Tuple Variadic Constraint Inference

Tuple constraint inference now supports a single variadic capture in the template tuple.

Supported forms include:

```text
tuple[*Ts] against tuple[int, str]
tuple[int, *Ts, bytes] against tuple[int, str, bool, bytes]
```

These infer `Ts` to a `TupleType` containing the captured actual slice. Empty captures are supported, so a template like
`tuple[int, *Ts, str]` can match `tuple[int, str]` and infer `Ts` to an empty tuple type.

The supported template marker can be either `UnpackType(TypeVarTupleType)` or a bare `TypeVarTupleType` in tuple item
position, matching the current IR shapes we have been using.

The implementation remains intentionally narrow:

- variadic actual tuples still fail closed;
- multiple variadic template markers fail closed;
- `Unpack` of anything other than `TypeVarTupleType` still fails closed in this inference path;
- this does not attempt a general variadic tuple lattice.

## Runtime TypeVarTuple Reflection

Runtime reflection now understands `typing.TypeVarTuple`.

`RuntimeTypeReflector` reflects:

- `TypeVarTuple('Ts')` to `TypeVarTupleType`;
- `Unpack[Ts]` to `UnpackType(TypeVarTupleType(...))`;
- tuple forms such as `tuple[*Ts]` and `tuple[int, *Ts, bytes]` to the core tuple shapes that constraint inference now
  supports.

Runtime tests now prove that reflected `typing` forms can flow into the core algorithm:

```text
tuple[*Ts] against tuple[int, str]
tuple[int, *Ts, bytes] against tuple[int, str, bool, bytes]
```

This is an important step toward making the runtime surface more than a normalizer. The user can hand it modern heap
typing objects, and the resulting IR participates in real inference.

## Variadic Alias Substitution

Substitution and alias expansion now understand tuple variadics.

Inside a `TupleType`, replacing a `TypeVarTupleType` with a `TupleType` or `TypeList` splices the replacement items into
the containing tuple. This is deliberately scoped to tuple variadic positions:

```text
tuple[int, *Ts, bool], Ts -> tuple[str]
=> tuple[int, str, bool]
```

Ordinary type variable replacement remains nested:

```text
tuple[T], T -> tuple[int, str]
=> tuple[tuple[int, str]]
```

This behavior is what makes nonrecursive variadic aliases usable. An alias target like `tuple[*Ts]` can be expanded
after `Ts` has been bound to a packed tuple argument.

## Runtime Parameterized Variadic Aliases

Runtime `TypeAliasType` reflection now supports parameterized aliases with one `TypeVarTuple` parameter.

For example:

```python
Ts = typing.TypeVarTuple('Ts')
Alias = typing.TypeAliasType('Alias', tuple[*Ts], type_params=(Ts,))
Alias[int, str]
```

reflects as a `TypeAliasType` whose single alias argument is a packed `TupleType[int, str]`. Expanding the alias then
produces `tuple[int, str]`.

Mixed fixed and variadic parameters are also supported:

```python
Alias = typing.TypeAliasType('Alias', tuple[T, *Ts, U], type_params=(T, Ts, U))
Alias[int, str, bool, bytes]
```

reflects with alias args equivalent to:

```text
[int, tuple[str, bool], bytes]
```

and expands to:

```text
tuple[int, str, bool, bytes]
```

The binder remains fail-closed:

- nonvariadic aliases still require exact argument counts;
- aliases with multiple `TypeVarTuple` parameters are rejected;
- too few arguments for fixed prefix or suffix parameters are rejected;
- direct alias objects and subscripted alias forms are distinguished, so an empty subscription like `Alias[*()]` is not
  confused with an unsubscripted alias.

## Type Keys And Caches

The new variadic alias shapes are now covered by key and cache tests.

Tests pin that:

- packed tuple alias arguments appear in normal type keys;
- tuple-key output includes alias identity, alias name, packed args, and expanded target shape;
- structural keys erase nonrecursive alias identity while preserving the packed tuple structure;
- repeated reflected parameterized variadic alias forms reuse the reflector cache and type-key cache.

This matters for the marshal use case. Top-level marshal operations hit reflection and type-key-ish machinery often,
so these runtime forms need predictable cache behavior even before the final cache/threading design is settled.

## Alias Collection Cleanup

`typeops.collect_aliases` was translated from a large recursive `if`/`elif` helper into a direct `TypeVisitor[None]`
implementation.

The behavior is intentionally preserved:

- every encountered alias reference is appended;
- each alias target is followed only once by `TypeAlias` symbol identity;
- alias arguments are still traversed;
- recursive-alias detection shares the same `seen` set semantics as before.

This was mostly a maintainability cleanup. The visitor now lines up with the old branch order, making future changes to
type traversal easier to audit.

One related observation: in this codebase `SyntheticTypeVisitor` is currently mostly a compatibility and intent marker.
In mypy, some synthetic/internal nodes assert that their visitor is a `SyntheticTypeVisitor`. In this distillation,
`TypeVisitor` already declares all node methods and the `accept()` implementations do not enforce the synthetic split.

## Verification

The current suite after this work is:

```bash
.venv/bin/python -m pytest -q mypydistill
```

which reports:

```text
984 passed
```

The standard gate also passes:

```bash
make fix check
```

This includes docstring fixing, ruff, flake8, and mypy.

## Near-Term Goals

The next work should keep focusing on fundamentals and runtime-reachable capability.

Good immediate slices:

- add more TypeVarTuple coverage outside tuple aliases only where it is locally well-defined, while keeping the general
  variadic lattice punted;
- strengthen tuple variadic behavior in structural equality, structural keys, subtype, meet, and join where tests show
  gaps;
- add fail-closed tests for unsupported variadic combinations before adding support;
- keep adding runtime tests whenever a core algorithm path is expected to work from real `typing` heap objects;
- audit whether runtime annotation emission handles tuple variadics and variadic aliases correctly, especially for
  generated dataclass signatures.

Callable-related near-term goals remain:

- improve callable constraint coverage where it intersects with aliases, overloads, ParamSpec, and Concatenate;
- keep generic callable actuals and hard cases fail-closed until there is a deliberate model.

## Mid-Term Goals

Important mid-term goals remain unchanged, but the variadic work clarifies part of the path.

The main goals are:

- recursive alias/type-key behavior strong enough for marshal caches, including recursive aliases, alpha-equivalent
  variables, packed variables, and alias-erased structural keys;
- eventual recursive constraint solving, built on structural equivalence and structural keys that already understand
  the relevant shapes;
- broader mypy-derived algorithms: substitution, expansion, constraints, solve, subtyping, meet, join, and eventually
  inference helpers should continue to move together;
- runtime reflection that can replace the old `_reflect.types` affordances in dataclass, marshal, and injector use
  cases without requiring downstream packages to know core IR details;
- NewType identity preservation wherever nominal runtime dispatch needs it;
- explicit runtime annotation emission policies, including alias-preserving and alias-expanding modes;
- an in-memory cache/thread-safety design that can support high-frequency `typeof`-style entrypoints and eventually
  free-threaded Python.

Still later:

- protocol checking closer to mypy semantics;
- a curated public API pass after the package is closer to its final in-repo location;
- a decision about whether the `SyntheticTypeVisitor` split is worth preserving as an enforced distinction or should
  become a simple compatibility alias in this distillation.
