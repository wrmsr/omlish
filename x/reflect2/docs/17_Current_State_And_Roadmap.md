# Current State And Roadmap

This is a checkpoint summary of the system after the first broad runtime
reflection and type-operation pass.

## What This Is

`mypydistill` is now a small runtime-oriented type IR and operation toolbox
inspired by mypy's internal type machinery. It still does not read source code,
parse ASTs, track file locations, serialize caches, or perform static checking.

The current shape is:

```text
runtime typing/class objects
        |
        v
runtime reflection layer
        |
        v
core Type IR + visitors + operations
```

The core stays source-unaware and mostly mypyc-friendly. Runtime inspection
lives under `runtime/`.

## Current Runtime Surface

Users can reflect many Python 3.14 runtime type forms into the core IR:

- builtin classes and generic aliases such as `int`, `list[int]`,
  `dict[str, int]`, `tuple[int, ...]`, and fixed tuples,
- `typing.Any`, `None`, `typing.Never`, and `typing.NoReturn`,
- PEP 604 and `typing.Union` / `typing.Optional`,
- `typing.Literal`, `typing.Annotated`, `typing.NewType`,
  `typing.ClassVar`, `typing.Final`, `type[T]`, and `typing.Type[T]`,
- runtime `typing.TypeVar` objects, including variance, constraints, bounds,
  and defaults where available,
- Python 3.14 `typing.TypeAliasType`, currently by transparent expansion,
- `typing.TypeGuard[T]` as `TypeGuardedType(T)`,
- runtime classes and generic class hierarchies.

Known builtins and collection ABCs use stable names and known generic metadata.
Dynamic runtime classes receive identity-qualified names such as:

```text
some.module.User@7fabc123
some.module.User@1
```

`RuntimeTypeUniverse(dynamic_type_name_suffix='counter')` gives
deterministic per-universe suffixes for tests and reproducible diagnostics.

Forward references fail closed by default. A caller can supply an in-memory
resolver through:

```python
make_runtime_reflector(forward_ref_resolver=resolver)
```

The recommended runtime entry point for application code is an explicit,
reused reflector:

```python
reflector = make_runtime_reflector(...)
```

That reflector should be passed into runtime ops so the reflection cache,
dynamic `TypeInfo` identities, runtime `TypeVar` namespace, and forward-ref
resolution state stay coherent.

## Runtime Operations Available

The runtime ops layer currently exposes:

- `reflect_type_str()` and `reflect_type_strs()` for display,
- `reflect_instance()`, `reflect_instance_info()`, and
  `reflect_instance_args()` for fail-fast instance extraction,
- `reflect_is_same_type()` and `reflect_is_alpha_equivalent()`,
- `reflect_is_assignable()` and `reflect_is_assignable_or_false()`,
- `reflect_join()` / `reflect_join_list()`,
- `reflect_meet()` / `reflect_meet_list()`,
- `reflect_substitute_type()` / `reflect_substitute_types()`,
- `reflect_base_args()` and `reflect_base_instance()` with `or_none` variants,
- `reflect_mro_instances()` and `reflect_mro_instances_or_none()`,
- `reflect_mro_entries()` and `reflect_mro_entries_or_none()`,
- `reflect_mro_type_strs()` for debugging instantiated generic MROs.

The instantiated MRO helpers are the current replacement for the old
`generic_mro` behavior. Given a runtime type like `Child[int]`, they can produce
entries such as:

```text
Child@1[builtins.int]
Middle@2[builtins.dict[builtins.str, builtins.int]]
Base@3[builtins.list[builtins.dict[builtins.str, builtins.int]], builtins.str]
typing.Generic
builtins.object
```

Each `MroEntry` exposes `info`, `instance`, and `args`.

## Core Operations Available

The core currently has:

- the mypy-like `Type` hierarchy skeleton,
- `TypeInfo`, `TypeAlias`, arg kinds, and variance constants,
- visitors, synthetic visitors, translators, and traversers,
- stringification via `type_str()`,
- copying,
- substitution and expansion,
- union normalization helpers,
- recursive-alias-aware same-type and alpha-equivalence foundations,
- conservative subtyping,
- meet, join, and assignability wrappers,
- generic base-instance mapping through `TypeInfo.bases`.

The code is intentionally fail-closed. Unsupported runtime forms generally
raise `UnreflectableTypeError`; unsupported type operations raise
`UnsupportedTypeOperationError` rather than returning misleading answers.

## Important Current Limits

The system is useful now, but it is not yet the full intended toolbox.

Major limits:

- `ParamSpec` and `TypeVarTuple` are recognized as unsupported at runtime.
- `typing.TypeIs` is rejected until we model its distinct mypy semantics.
- Callable behavior is shallow compared with mypy.
- Constraint solving, inference, overload behavior, and full application of
  callable type variables are not yet ported.
- Protocol, structural subtype, TypedDict, tuple precision, Literal precision,
  and variance behavior are still partial.
- Runtime `TypeAliasType` is expanded transparently; alias identity is not
  preserved for those runtime alias objects yet.
- Recursive runtime type construction and recursive alias equivalence need more
  deliberate machinery.
- Caching is strong-reference and in-memory only; weakrefs and eviction remain
  punted.
- Display strings are debug output, not serialization.

## Short-Term Goals

Useful next steps from here:

- Add focused docs/tests around the current runtime entry-point surface only
  where they clarify behavior, avoiding doc churn for every small change.
- Add ergonomic wrappers only when they remove repeated application code, as
  with `reflect_instance()` and instantiated MRO helpers.
- Continue filling runtime reflection gaps for common Python 3.14 type forms,
  but keep unsupported forms fail-closed.
- Improve callable reflection and operations enough for ordinary marshalling
  and typeclass-style dispatch use cases.
- Add higher-level runtime queries over reflected instances, such as origin,
  args, instantiated bases, and possibly normalized display/debug summaries.

## Mid-Term Goals

The next substantial layer should move from representation to useful type
machinery:

- Port more of mypy's constraint/inference/solve/apply machinery in a distilled
  form.
- Strengthen substitution and expansion around callables, aliases, and generic
  classes.
- Add more precise handling for `ParamSpec`, `TypeVarTuple`, and `Unpack` once
  the needed core operations are ready.
- Preserve runtime alias identity where useful, while still supporting
  transparent expansion as a convenience.
- Expand generic base mapping toward more mypy-equivalent behavior, including
  harder variance and tuple cases.
- Add richer equivalence tests for recursive types and type variables in
  corresponding positions.

## Long-Term Goals

The original intent is still broader than the current implementation:

- A grown-up replacement foundation for the current `omcore` reflection system.
- Runtime type reflection that is fast enough for production use through
  coherent in-memory caching.
- A high-level toolbox for marshalling, typeclass dispatch, schema derivation,
  and similar runtime type-form applications.
- Recursive type support with robust equivalence, including alpha-equivalent
  type variable positions.
- A distilled but recognizable subset of mypy's real type checker machinery,
  without source awareness or durable cache machinery.
- A core that remains isolated enough to be plausibly mypyc-compatible, with
  runtime inspection kept outside that core.

The current system is already useful for reflecting runtime type forms,
inspecting generic class hierarchies, substituting runtime TypeVars, comparing
strict or alpha-equivalent shapes, and debugging the resulting IR. The next
phase should deepen the algorithms rather than just adding more isolated type
form corners.
