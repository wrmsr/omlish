# Runtime Reflection And Union Simplification

This note summarizes the current state after the first substantial runtime reflection pass and the beginning of checker-shaped union simplification.

## Runtime Reflection

A new runtime reflection layer now exists under `runtime/`. The `RuntimeTypeUniverse` owns synthetic `TypeInfo` objects for known builtins and selected `collections.abc` types, while `RuntimeTypeReflector` maps runtime Python type objects into the core IR.

Currently reflected forms include:

- bare runtime classes such as `int`, `str`, `list`, and `dict`
- PEP 585 generics such as `list[int]`, `dict[str, int]`, `tuple[int, str]`, and `tuple[int, ...]`
- `Any`, `None`, and `type(None)`
- runtime `TypeVar` objects, including bounds, constraints, and variance flags
- `Literal` values for the core-supported literal payloads
- transparent `Annotated`, `NewType`, `ClassVar`, and `Final`
- `Callable[[...], R]` and `Callable[..., R]`
- `type[T]` and `typing.Type[T]`
- `Optional[T]`, `Union[...]`, and PEP 604 unions

The runtime layer is intentionally separate from the core algorithm modules. It performs Python object inspection and caching, while the core remains closer to the mypy-derived, mypyc-friendly type machinery.

## Callable Shape

`CallableType` now has an `is_ellipsis_args` flag, matching the mypy field needed to represent `Callable[..., R]`. Translation, stringification, and same-type comparison preserve that flag.

This is still a narrow callable model. Runtime reflection supports positional argument lists and ellipsis argument callables, but not keyword-only argument names, `ParamSpec`, `Concatenate`, or overload extraction from runtime objects.

## Union Construction Layers

Union handling now follows the mypy layering more closely.

`UnionType.__init__` flattens direct nested unions while preserving alias items at that layer.

`make_union` is the light constructor:

- zero items becomes `UninhabitedType`
- one item becomes that item
- multiple items becomes `UnionType`

`make_simplified_union` is the new checker-shaped entry point. It currently performs:

- nested union flattening
- optional literal contraction
- structural duplicate removal
- narrow subtype-based redundant item removal
- final construction through `make_union`

This is deliberately not full mypy parity yet. It is the slot where future `make_simplified_union` behavior should grow.

## Literal Contraction

`try_contracting_literals_in_union` currently supports only one contraction case:

- `Literal[True] | Literal[False]` becomes `bool`

This mirrors one small part of mypy's literal contraction behavior without pulling in enum literal contraction or the broader subtype lattice too early. Plain `make_union` does not call this helper.

## Narrow Subtyping

A conservative `is_subtype` API now exists. Current support is intentionally small:

- same-type relation
- `TypeGuardedType` unwrapping
- nominal `Instance` subtype checks through `TypeInfo.mro`
- same-target generic `Instance` checks where arguments must be structurally equal

It does not yet map generic base arguments, handle variance, protocols, callables, unions, `Any`, promotions, tuple fallback logic, or recursive subtype assumptions.

`make_simplified_union` uses this narrow subtype relation to remove redundant nominal subtype items, such as a synthetic `int | object` when `int` has `object` in its MRO.

## Current Test State

The current package test command is:

```bash
.venv/bin/python -m pytest mypydistill/tests
```

At the time of this note, the suite reports 110 passing tests.

The package-source name constraint still holds:

```bash
rg -n "mypydistill" mypydistill
```

returns no matches.

## Important Boundaries

Runtime reflection is still a bridge from trusted runtime type forms to IR nodes. It is not a type checker.

Union simplification has a real public entry point now, but it remains conservative. The next expansions should be made in the core simplification and subtyping layers rather than inside runtime reflection.

## Likely Next Steps

Good incremental next steps include:

- add generic base argument mapping for nominal instance subtyping
- apply declared variance from `TypeInfo.variances` during same-target generic subtype checks
- add union-aware subtype checks
- expand literal contraction toward enum-like cases once enum modeling is stronger
- add runtime reflection support for `ParamSpec` and `TypeVarTuple` separately from the mypyc-friendly core
