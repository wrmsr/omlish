# Initial Notes

`mypydistill` is intended to be a distilled, runtime-oriented extraction of mypy's internal type IR and the useful type operations built on top of it. The project is not a source-code type checker. It should operate on type forms that already exist in the Python heap, such as `typing.Union`, `list[int]`, `typing.TypeAliasType`, runtime classes, protocols, aliases, and type variables.

The core idea is to keep the parts of mypy that are valuable as type machinery while removing the parts that only exist because mypy parses source files, reports source locations, serializes cache data, and runs as a static checker.

## Goals

The main goal is a proper high-level toolbox for runtime-reflected types, grounded in mypy's real type checker machinery. That includes:

- A mypy-like type IR, ideally tracking the full mypy 2.1.0 `Type` hierarchy.
- Visitors, traversers, translators, and type queries.
- Runtime reflection from `typing` and builtin generic objects into the IR.
- Core operations such as subtype checks, meet, join, inference, constraint solving, expansion, substitution, and related helper operations.
- Recursive type support, including equivalence checks for structurally equivalent recursive types.
- Equivalence that can account for type variables in corresponding positions, even when the variable names differ.
- Practical debugging niceties such as useful stringification and reprs.
- Tests adapted from relevant mypy unit tests, plus runtime reflection tests informed by the existing `_reflect` package.

## Non-Goals

The project should not read or understand source files. It should not have AST parsing, file offsets, line and column reporting, import graph handling, durable serialization, or persistent cache machinery.

It should also not become a runtime value checker. It may enable external code to build value-checking or marshalling systems, but the core project is about reflecting and operating on type forms, not checking arbitrary runtime values against those types.

## Source Material

The repo contains three important references:

- `mypy/`: mypy 2.1.0 as the source of truth. The checked-out version reports `__version__ = "2.1.0"`.
- `_mypydistill_old/`: an older manual distillation attempt. It already contains many copied or pared-down mypy modules, including `types`, `type_visitor`, `subtypes`, `meet`, `join`, `constraints`, `solve`, and tests.
- `_reflect/`: the current runtime reflection implementation from `omcore`. It is smaller, pragmatic, runtime-oriented, and already handles many modern `typing` objects, but it lacks the deeper type-system machinery this project wants.

## Initial Findings

The new `mypydistill` package was initially empty except for `__init__.py`.

The current `_reflect` package is a runtime typing normalizer. It reflects Python objects into a small custom IR with nodes such as `Union`, `Generic`, `Protocol`, `TypeAlias`, `NewType`, `Annotated`, `Literal`, `ForwardRef`, `Recursive`, and `Any`. It already contains useful runtime knowledge about private `typing` implementation details and Python 3.14-era objects. However, its equality and substitution behavior are shallow compared with what this project needs.

The old `_mypydistill_old` package is much closer to mypy internals. It includes a broad chunk of the type machinery and mypy-derived tests. However, starting from it directly would pull in a lot of baggage: source-location fields, AST node scaffolding, serialization methods, checker assumptions, old compatibility choices, and import cycles. It also does not exactly match mypy 2.1.0; for example, mypy 2.1.0 includes `PlaceholderType` and `InstanceCache`, and has some class organization differences.

Mypy's actual type hierarchy is rooted at `Type`, not `TypeInfo`. `TypeInfo` is metadata for class-like definitions and is used by `Instance`, but it is not the root of the type IR.

The mypy 2.1.0 core type hierarchy includes:

- `Type`
- `TypeAliasType`
- `TypeGuardedType`
- `RequiredType`
- `ReadOnlyType`
- `ProperType`
- `TypeVarLikeType`
- `TypeVarType`
- `ParamSpecType`
- `TypeVarTupleType`
- `UnboundType`
- `CallableArgument`
- `TypeList`
- `UnpackType`
- `AnyType`
- `UninhabitedType`
- `NoneType`
- `ErasedType`
- `DeletedType`
- `Instance`
- `FunctionLike`
- `Parameters`
- `CallableType`
- `Overloaded`
- `TupleType`
- `TypedDictType`
- `RawExpressionType`
- `LiteralType`
- `UnionType`
- `PartialType`
- `EllipsisType`
- `TypeType`
- `PlaceholderType`

Mypy represents recursive aliases with `TypeAliasType` pointing at `TypeAlias`, plus recursion-aware subtype/equivalence logic and assumption stacks in type state. The current `_reflect.Recursive` representation is much thinner, so recursive type equivalence will need careful treatment.

Raw mypy type variable equality is ID-based. Supporting alpha-equivalence-style comparisons such as `Sequence[T]` and `Sequence[U]` when `T` and `U` are unbound in corresponding positions will likely require a distinct canonicalization or equivalence layer, not just direct object equality.

## Constraints

The code should largely follow `CODESTYLE.md` from the repo.

Important local style constraints include:

- Use relative imports inside the package.
- The package name should not appear in package source lines.
- Prefer small source files over one large module.
- Prefer explicit, simple constructs in core code.
- Use `import typing as ta` and `import dataclasses as dc` if those modules are needed.
- Tests should use pytest.

There is also a mypyc-related constraint. Mypy itself is written with mypyc in mind, and the algorithm-heavy core of this project should preserve that option. The initial direction is therefore to keep the core IR and algorithms mypyc-friendly: explicit classes, `__slots__`, direct visitor dispatch, limited metaprogramming, and simple containers.

Runtime reflection code is different. It will necessarily inspect weird runtime `typing` objects and may use Python-version-specific tricks. That layer does not need to be mypyc-compatible initially, though it should remain isolated from the core so the core can stay clean and compilable.

## Initial Direction

The project should start from new blank source files rather than copying `_mypydistill_old` and paring it down. Copying first would make source-awareness and checker baggage the default. Starting fresh lets each retained field and operation be an explicit type-space choice.

The dependency direction should be:

```text
runtime typing objects
        |
        v
runtime reflection layer
        |
        v
core mypy-like type IR + algorithms
```

The core should not import the runtime reflection layer. Runtime reflection can import the core and produce core `Type` nodes.

A tentative package split is:

```text
mypydistill/
  types.py          # core IR, mypyc-friendly
  symbols.py        # TypeInfo, TypeAlias, ArgKind, variance constants
  type_visitor.py   # core visitors/translators/queries
  typetraverser.py  # core traversal
  typeops.py        # core type operations
  subtypes.py
  meet.py
  join.py
  constraints.py
  solve.py
  expandtype.py

  runtime/
    inspecting.py   # runtime typing/get_origin/get_args/private typing details
    reflecting.py   # runtime object -> core IR
    aliases.py      # Python typing alias handling
    universe.py     # synthetic TypeInfo universe for runtime classes
```

The first implemented slice created a skeletal core:

- `mypydistill/symbols.py`
- `mypydistill/types.py`
- `mypydistill/type_visitor.py`
- `mypydistill/typetraverser.py`
- `mypydistill/tests/test_core_skeleton.py`

The skeleton defines the mypy 2.1.0 type class list using explicit `__slots__` classes and direct `accept()` visitor methods. The tests live under `mypydistill/tests` and use package-relative imports.

At this point the tests pass with:

```bash
.venv/bin/python -m pytest mypydistill/tests/test_core_skeleton.py
```

A direct `.venv/bin/pytest ...` invocation did not place the repo root on `sys.path` in this environment, so `python -m pytest` is the working invocation for now.
