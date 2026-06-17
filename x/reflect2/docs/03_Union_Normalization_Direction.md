# Union Normalization Direction

This note records the current conclusion about unions after checking the local mypy 2.1.0 source.

## What Mypy Does

Mypy has layered union construction rather than one all-purpose constructor.

`UnionType.__init__` performs structural flattening of nested unions. It calls `flatten_nested_unions(..., handle_type_alias_type=False)`, so direct nested unions are flattened, but aliases are preserved at this layer when possible.

`UnionType.make_union` is a small cardinality helper:

- zero items becomes `UninhabitedType`
- one item becomes that item
- multiple items becomes `UnionType(items)`

The heavier checker-grade normalization lives in `typeops.make_simplified_union`. That function flattens nested unions, collapses one item, removes redundant items using subtype checks, handles duplicate-like cases, and contracts some literal unions such as `Literal[True] | Literal[False]` to `bool`.

`Optional[T]` is represented as `Union[T, NoneType]`. In mypy's semantic analysis path, `typing.Optional[T]` is lowered through `make_optional_type`, which avoids full simplification because semantic analysis cannot assume fully initialized type information.

## Direction For This Package

We should preserve the same layering.

The near-term runtime reflection path can safely use a small union helper equivalent to `UnionType.make_union`: flatten direct nested unions, collapse zero or one item, and otherwise keep a `UnionType`.

We should leave room for a later `make_simplified_union` equivalent rather than baking eager simplification into runtime reflection. That later function should be part of the core algorithm layer and should eventually track mypy's behavior closely, including subtype-based redundancy elimination and literal contraction.

This matters because the runtime bridge should construct accurate type forms, while the core toolbox should own normalization policies. Reflection should not become the only place where union simplification happens.

## Open Work

- Add a core union constructor/helper that mirrors the light mypy behavior.
- Teach runtime reflection for `typing.Optional` to lower to `Union[T, NoneType]` through that helper.
- Later, port a real `make_simplified_union` once subtyping is strong enough to support redundant-item elimination correctly.
- Add tests that distinguish direct union construction from checker-grade simplification so future expansion has a clear slot.
