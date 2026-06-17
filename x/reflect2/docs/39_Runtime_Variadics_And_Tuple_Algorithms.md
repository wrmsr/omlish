# Runtime Variadics And Tuple Algorithms

This checkpoint covers the work after `38_Variadic_Aliases_And_TypeVarTuple.md`.

The main arc was taking the variadic alias and `TypeVarTuple` foundation from the previous checkpoint and making it
useful through the runtime surfaces that matter for replacement: runtime annotation emission, dataclass and namedtuple
field replacement, structural subtype/equivalence, meet/join, and constraint inference. The implementation is still
intentionally narrow around variadics. We support the fixed and locally well-defined cases, and continue to fail closed
for the general variadic tuple lattice.

## Runtime Annotation Emission

Runtime annotation emission now understands tuple variadic forms.

The emitter can round-trip:

- `tuple[*Ts]`;
- `tuple[int, *Ts, bytes]`;
- `tuple[Unpack[tuple[int, str]]]`;
- parameterized variadic aliases such as `Alias[int, str]`;
- fixed-edge variadic aliases such as `Alias[int, str, bool, bytes]` where the runtime alias has parameters like
  `(T, Ts, U)`.

The alias emission policy remains explicit:

- expand mode emits the expanded runtime annotation, such as `tuple[int, str]`;
- preserve mode emits the runtime alias form where possible, such as `Alias[int, str]`.

One important implementation detail is that the IR stores a variadic alias argument as a packed `TupleType`. Preserve
mode therefore has to spread that packed tuple back into the runtime alias subscription. Without that, the runtime
annotation would incorrectly become `Alias[tuple[int, str]]` instead of `Alias[int, str]`.

Unsupported `Unpack` payloads still fail closed with `ReflectionError` rather than silently producing an approximate
annotation.

## Variadic Runtime Classes

Runtime class generic reflection now accepts `TypeVarTuple` parameters, not only `TypeVar` and `ParamSpec`.

For a class like:

```python
Ts = typing.TypeVarTuple('Ts')

class Box(typing.Generic[*Ts]):
    ...
```

the runtime universe records a `TypeVarTupleType` in the class `TypeInfo`. A subscription like `Box[int, str]` is
reflected with one packed tuple argument corresponding to `Ts`, matching the existing runtime alias representation.

The same packing model is used for fixed-edge generic classes:

```python
class Box(typing.Generic[T, *Ts, U]):
    ...
```

`Box[int, str, bool, bytes]` reflects with arguments equivalent to:

```text
T  -> int
Ts -> tuple[str, bool]
U  -> bytes
```

Multiple `TypeVarTuple` class parameters still fail closed. For now, `TypeVarTuple` class parameters are treated as
invariant.

## Dataclass And NamedTuple Surfaces

The dataclass and namedtuple field inspection paths now have explicit tests for variadic field replacement.

Covered forms include:

- inherited dataclass fields using `tuple[*Ts]`;
- fixed-edge dataclass fields using `tuple[T, *Ts, U]`;
- dataclass fields using a variadic alias, with expanded annotations by default and preserve-mode alias emission still
  available from the field's replaced IR type;
- the same set of cases for `typing.NamedTuple`.

This matters for the original dataclass/DI use case. A generic base can define a variadic field, and a concrete subclass
or parameterized runtime form can now expose a concrete runtime annotation suitable for generated signatures.

## Structural Equivalence And Subtype

Structural equivalence now has pinned coverage for `TypeVarTuple` alpha-equivalence:

```text
tuple[*Ts] ~= tuple[*Us]
tuple[int, *Ts, str, *Ts] ~= tuple[int, *Us, str, *Us]
```

The consistency checks are important. Alpha-equivalence maps variables by corresponding positions, so repeated uses of
the same `TypeVarTuple` must map to repeated uses of the same corresponding variable on the other side.

Structural subtype now supports fixed-length, nonvariadic `TupleType` item comparisons. This is a deliberately small
step:

- same-length fixed tuples compare itemwise;
- mismatched fixed tuple lengths are not subtypes;
- tuple variadic subtype shapes still raise `UnsupportedTypeOperationError`;
- structural subtype through a nonrecursive variadic alias works when alias expansion produces a fixed tuple.

This keeps subtype behavior aligned with the current reflection and key model without pretending that the full variadic
tuple lattice exists yet.

## Meet And Join

Meet and join now support same-length fixed `TupleType` shapes.

For join:

```text
join(tuple[int, object], tuple[object, str])
=> tuple[object, object]
```

For meet:

```text
meet(tuple[int, object], tuple[object, str])
=> tuple[int, str]
```

Mismatched fixed tuple lengths keep the current conservative behavior:

- join returns a union of the two tuple types;
- meet returns `Never`.

Variadic tuple shapes fail closed in both operations. The runtime ops surface has matching tests from real heap typing
forms, including `tuple[*Ts]` and parameterized variadic aliases.

## Constraint Alignment

Constraint inference already had good tuple coverage from the previous checkpoint. This round added tests to align it
with the new tuple subtype/meet/join behavior.

Pinned coverage now includes:

- fixed tuple inference where concrete items are subtype-compatible and only the variable position produces a
  constraint;
- constraints against join-derived tuple shapes;
- constraints against meet-derived tuple shapes;
- variadic aliases with packed tuple args in the template;
- variadic aliases with packed tuple args in the actual.

No production changes were needed for this part. The current constraint inference already handled these paths once the
surrounding tuple operations were tightened.

## Visitor Cleanup

The recursive alias collector used by type keys was translated from a large recursive helper into a module-level
visitor. This mirrors the earlier `typeops.collect_aliases` cleanup.

The behavior is intended to remain unchanged:

- recursive aliases are collected once by alias identity;
- alias arguments are traversed;
- the surrounding type graph is guarded by type object identity to avoid cycles;
- alias targets are not followed by this collector.

After that, `DefaultTypeVisitor` was added as a base that super-calls through the type hierarchy to a central
`visit_type` method. The collect-style visitors were moved onto that base, reducing boilerplate leaf methods while
keeping traversal explicit where needed.

## Verification

The current full suite after this work is:

```bash
.venv/bin/python -m pytest -q mypydistill
```

which reports:

```text
1022 passed
```

The standard gate also passes:

```bash
make fix check
```

## Near-Term Goals

Good immediate next slices:

- add runtime constraint tests for the tuple alignment cases that are now covered in core IR tests;
- keep adding runtime tests when core algorithms are expected to work from real `typing` heap objects;
- continue tightening fail-closed behavior around unsupported variadic forms;
- audit tuple variadic behavior in `is_assignable` and compatibility helpers if those paths are expected to be used by
  marshal-like dispatch;
- consider whether the core type-key `_key` wall of `isinstance` branches should be migrated toward a visitor after
  the current collector refactors have settled.

## Mid-Term Goals

The bigger direction is unchanged:

- recursive alias/type-key behavior strong enough for marshal caches, including recursive aliases, packed variables,
  alias-erased structural keys, and alpha-equivalent variables;
- recursive constraint solving, once the structural equivalence and structural keys are strong enough to support it;
- broader mypy-derived algorithm coverage across substitution, expansion, constraints, solve, subtype, meet, join, and
  inference helpers;
- runtime reflection surfaces that can replace the old `_reflect.types` affordances in dataclass, marshal, and injector
  use cases;
- NewType identity preservation wherever nominal runtime dispatch needs it;
- explicit runtime annotation policies where generated signatures and config metadata need different behavior;
- an in-memory cache/thread-safety design appropriate for high-frequency `typeof`-style entrypoints and eventually
  free-threaded Python.
