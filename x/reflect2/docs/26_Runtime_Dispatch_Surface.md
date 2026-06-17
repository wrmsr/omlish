# Runtime Dispatch Surface

This checkpoint records the work after `25_Hybrid_Type_Keys.md`: finishing the first hybrid type-key pass, adding
reflector-local key caching, and adding query helpers aimed at marshal and dependency-injection dispatch.

## Why

The previous checkpoint introduced compact hybrid type keys, but left several practical pieces unfinished:

- tuple-key builder logic had been duplicated during the first implementation pass;
- unions with opaque literal payloads still failed closed;
- runtime entrypoints still recomputed type keys even when reflection was cached;
- `NewType` and `Annotated` were preserved structurally but did not have a clean query surface;
- marshal-shaped dispatch still required callers to manually chain several lower-level helpers.

The work in this chunk keeps moving toward the original replacement goal: downstream systems should be able to reflect
a runtime type form once, key it cheaply, and ask explicit questions about common shapes without reaching into the IR
by hand.

## Type-Key Writer Refactor

`typekeys.py` now has one semantic `_TypeKeyBuilder` that takes a `_TypeKeyWriter`.

The builder owns traversal decisions:

- which IR nodes are supported;
- exact versus alpha variable behavior;
- recursive alias stack handling;
- fail-closed behavior for unsupported nodes.

The writers own output representation:

- `_StringTypeKeyWriter` produces the public compact `TypeKey` shape;
- `_TupleTypeKeyWriter` preserves the old nested tuple shape for private migration/debug tests.

This removed the duplicated parallel builders and leaves future changes, such as better recursive handling, in one
semantic path.

## Hybrid Type Keys

String type keys were expanded and baked in with reader-facing tests. The tests now document simple expected outputs
for the supported node shapes, using realistic runtime fullnames such as `builtins.int` and
`collections.abc.Callable`.

Callable argument kinds now render compactly:

```python
"C[I['builtins.int'],k[ARG_POS],n[None],r[I['builtins.str']],f[I['collections.abc.Callable']]]"
```

Type-var-like keys omit default namespace and meta-level fields:

```python
"TV[1]"
"PS[2]"
"TVT[3]"
```

Non-default fields remain explicit and unambiguous:

```python
"TV[4,ns,'scope',meta,2]"
```

Literal scalar inlining remains conservative:

- `bool`;
- exact `int`;
- `str`;
- `bytes`.

Floats and other hashable literal values are opaque payloads.

## Opaque Union Buckets

Hybrid keys now support unions containing opaque child keys.

Fully stringable unions stay string-only:

```python
"U[I['builtins.int'],I['builtins.str']]"
```

Unions with opaque members use a distinct unordered bucket marker:

```python
("U[OU[$0]]", frozenset({("L[$0,I['builtins.tuple']]", value)}))
```

Mixed unions keep stringable members in the string spine and bucket only the opaque members:

```python
("U[L[int:1,I['builtins.int']],None,OU[$0]]", frozenset({...}))
```

The `OU[...]` marker is deliberately part of the structural string spine. This keeps a union bucket distinct from a
literal frozenset value.

## Reflector Key Caches

`RuntimeTypeReflector` now caches exact and alpha type keys per reflected `Type` object.

The new reflector methods are:

- `type_key`;
- `type_key_or_none`;
- `alpha_type_key`;
- `alpha_type_key_or_none`.

Runtime operation entrypoints such as `reflect_type_key(...)` now use those methods after reflection. This means a
marshal-style hot path that repeatedly receives a module-global runtime type form can hit both:

- runtime object to reflected `Type`;
- reflected `Type` to `TypeKey`.

Tests cover repeated key object reuse for simple, nested, literal-union, and opaque-bucket forms.

The cache is still a plain strong-ref dict. It is useful now, but it is not the final thread-safe cache design.

## NewType Queries

`NewType` reflection already preserves identity by creating a distinct nominal `TypeInfo` and retaining the original
runtime `NewType` object in the universe. This chunk added query helpers so downstream users do not need to inspect the
nominal encoding directly.

New query surface:

- `RuntimeNewType`;
- `get_runtime_new_type`;
- `get_runtime_new_type_info`;
- `require_runtime_new_type_info`;
- `get_runtime_new_type_supertype`;
- `reflect_runtime_new_type_info`;
- `reflect_runtime_new_type_supertype`.

The query record exposes:

- the original runtime `NewType` object;
- the runtime `__supertype__`;
- the reflected supertype.

Tests cover distinct `NewType`s over the same supertype, key separation from the supertype, and annotation emission
round-tripping to the original `NewType` object.

## Annotated Queries

`Annotated` metadata is preserved through reflection, type keys, and runtime annotation emission. This chunk adds a
clean query surface for config and marshal code.

New query surface:

- `RuntimeAnnotated`;
- `get_annotated`;
- `strip_annotated`;
- `reflect_annotated`;
- `reflect_strip_annotated`.

Nested `Annotated` nodes are flattened while preserving metadata order from outer to inner. Non-annotated types return
`None` from `get_annotated` and pass through unchanged from `strip_annotated`.

## Runtime Type Shape

A first combined marshal-dispatch record now exists:

```python
RuntimeTypeShape
```

It contains:

- `original`;
- `annotated`;
- `unannotated`;
- `new_type`;
- `effective`;
- `optional_item`;
- `literal_value_type`;
- `literal_union`;
- `primitive_union`.

The helper flow is:

1. preserve the original reflected type;
2. strip top-level `Annotated`;
3. detect top-level `NewType`;
4. use the NewType supertype as the effective type if present;
5. run optional, literal, literal-union, and primitive-union queries against the effective type.

This gives marshal and dependency-injection code a small dispatch summary while preserving access to the exact original
shape and metadata.

Tests cover:

- `Annotated[NewType(...), metadata]`;
- `Annotated[Optional[T], metadata]`;
- `Annotated[Literal['a', 'b'], metadata]`;
- `NewType` inside collections remaining an argument shape rather than a top-level NewType dispatch.

## Current Boundaries

The new shape helper is intentionally shallow. It does not recursively classify every nested argument. For example,
`list[UserId]` is still an effective `list[...]` at the top level, and callers can inspect its base args if they need
to recurse.

Recursive alias handling remains stack-relative and unchanged. Mutually recursive graph canonicalization, graph
isomorphism, and coinductive equality are still punted.

Thread safety is also still punted. The new caches are strong-ref, per-reflector dictionaries and should be treated as
single-thread-oriented or externally synchronized until the cache/threading design is revisited.

## Next

Likely next steps:

- add focused tests or helpers for collection argument dispatch using `RuntimeTypeShape` plus base-arg queries;
- decide whether member-signature keys should move onto the shared type-key writer path;
- add a small adapter/spike surface that mimics the old reflection queries used by marshal factories;
- continue filling callable/member signature gaps that dependency injection will hit;
- revisit recursive alias/type-key design when native recursive marshal cases become the active focus;
- revisit thread-safe cache abstractions before relying on shared reflectors in nogil/multithreaded use.
