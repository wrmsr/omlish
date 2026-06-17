# Core Skeleton Progress

This note records the first implementation pass after the initial project assessment. It does not replace the initial notes; it captures what has actually been added so far and the near-term direction from here.

## Current Shape

The package now has a small core-only skeleton, deliberately separated from runtime reflection. The code added so far is still in the mypy-like core layer; no `typing` runtime inspection or object reflection has been implemented yet.

The current core files are:

- `symbols.py`
- `types.py`
- `type_visitor.py`
- `typetraverser.py`
- `typeops.py`
- `strconv.py`

Tests live under `tests/` inside the package and use relative imports.

The package source continues to avoid absolute imports of itself. A useful check is:

```bash
rg -n "mypydistill" mypydistill
```

which should return no matches.

## Type Hierarchy

`types.py` defines the initial mypy 2.1.0-inspired `Type` hierarchy. The root is `Type`, not `TypeInfo`. `TypeInfo` lives in `symbols.py` as class/type-definition metadata used by `Instance`.

The skeleton currently includes:

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

The classes are intentionally explicit and simple, with `__slots__` and direct `accept()` visitor dispatch. This keeps the core close to mypy's mypyc-friendly style.

## Symbol Metadata

`symbols.py` contains the small non-type metadata surface needed by the current type nodes:

- variance constants: `INVARIANT`, `COVARIANT`, `CONTRAVARIANT`, `VARIANCE_NOT_READY`
- argument kind enum and constants: `ArgKind`, `ARG_POS`, `ARG_OPT`, `ARG_STAR`, `ARG_NAMED`, `ARG_STAR2`, `ARG_NAMED_OPT`
- `SymbolNode`
- `TypeInfo`
- `TypeAlias`

This is intentionally much smaller than mypy's `nodes.py`. Source AST classes, file metadata, and source location concepts have not been carried over.

## Visitors And Traversal

`type_visitor.py` now contains:

- `TypeVisitor`
- `SyntheticTypeVisitor`
- `TypeTranslator`
- `TypeQuery`
- `BoolTypeQuery`
- `ANY_STRATEGY`
- `ALL_STRATEGY`

`typetraverser.py` contains `TypeTraverserVisitor`, which recursively walks the fields currently defined by the skeleton. It is enough to exercise the visitor surface and gives future operations a standard traversal primitive.

`TypeQuery` and `BoolTypeQuery` provide a first recursive query pattern. They already include a simple `seen_aliases` guard and a `skip_alias_target` switch, modeled after mypy's query visitors but reduced to the current skeleton.

## Type Translation

`TypeTranslator` is now a recursive identity transformer over the current skeleton. It returns atomic nodes unchanged and rebuilds composite/wrapper nodes recursively.

This is important because future operations such as substitution, alias expansion, erasure, and generic normalization can now be implemented as small translator subclasses instead of hand-rolled recursive functions.

The translator currently preserves metadata objects such as `TypeInfo` and `TypeAlias`; it only rebuilds type nodes.

## Core Type Operations

`typeops.py` currently contains a deliberately narrow helper set:

- `get_proper_type()`
- `get_proper_types()`
- `HasTypeVars`
- `has_type_vars()`
- `flatten_nested_unions()`
- `make_union()`

These are not full mypy-equivalent implementations yet. In particular, union simplification does not do subtype-based redundancy removal, literal contraction, or special handling of recursive aliases. The purpose of this pass was to establish foundational helper names and behavior without importing the whole checker.

## String Conversion

`strconv.py` adds the first debug stringification pass:

- `TypeStrVisitor`
- `type_str()`
- `type_info_str()`

`Type.__str__` and `Type.__repr__` delegate to `type_str()` using a local import to avoid an import cycle.

The formatting is stable and useful for tests/debugging, but it is not intended to exactly match mypy's full formatting. Examples include:

- `Any`
- `None`
- `Never`
- `T`
- `Box[T]`
- `Union[Box[T], None]`
- `type[T]`
- `def (A, B) -> R`
- `TypedDict({'x': A, 'y'?=: ReadOnly[B]})`

## Tests

The package tests currently cover:

- the core type class list/order
- traversal behavior
- boolean query aggregation
- basic type operations
- string conversion
- recursive identity translation and a simple rewriting translator

The current test command is:

```bash
.venv/bin/python -m pytest mypydistill/tests
```

At the time of this note, that reports 17 passing tests.

The direct console-script form `.venv/bin/pytest ...` did not reliably put the repo root on `sys.path` in this environment, so `python -m pytest` remains the working command.

## Design Notes Reinforced So Far

Starting from blank files has been useful. Each retained field and operation has been introduced intentionally, and the code has avoided importing source-awareness from mypy's AST/checker world.

The core/runtime split still looks right:

```text
runtime typing objects
        |
        v
runtime reflection layer
        |
        v
core mypy-like type IR + algorithms
```

The work so far is entirely in the core layer. The runtime reflection layer should be added later in separate files, likely under a `runtime/` package.

## Likely Next Step

The next small implementation step should be `expandtype.py` with basic type-variable substitution.

A narrow first slice would include:

- `expand_type(typ, env)`
- an `ExpandTypeVisitor` subclass of `TypeTranslator`
- support for replacing `TypeVarType` by `TypeVarId` or by the variable object itself
- recursive substitution through existing composites via `TypeTranslator`
- tests such as `Box[T] -> Box[A]`, `Callable[[T], T] -> Callable[[A], A]`, and preserving unmapped variables

This would be the first real type operation beyond traversal/query/stringification, and it builds directly on the translator that now exists.
