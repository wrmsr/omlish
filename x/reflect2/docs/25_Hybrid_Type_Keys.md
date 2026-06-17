# Hybrid Type Keys

This checkpoint records the first step away from deeply nested tuple type keys and toward compact hybrid keys.

## Why

Type keys are intended to support runtime caches for marshal, dependency injection, dataclass reflection, protocol
inspection, and related type operations. The old key shape was a nested tuple tree. That shape is semantically clear,
but it is not ideal for hot dictionary lookups:

- deep tuple equality recursively compares many Python objects;
- tuple hashes are recomputed from nested objects rather than being cached like string hashes;
- common runtime forms such as `list[int]`, `int | str`, and `Callable[[A], B]` can be represented as compact strings.

The direction is to keep one practical key kind while making the common case string-backed. The desired runtime shape
is:

```python
str
tuple[str, object, ...]
```

The string is the structural spine. When a key needs a hashable Python object that cannot be string-encoded without
losing fidelity, the string contains a local `$n` reference and the finished tuple contains the real object in that
position.

This preserves process-local Python equality semantics without any global interning table or durable serialization
format.

## Fullnames And Type Keys

Runtime `TypeInfo.fullname` values remain nominal identities. They answer which class-like thing an `Instance` refers
to, such as `builtins.list`, `collections.abc.Sequence`, or `some.module.Dynamic@1`.

Hybrid type keys use those fullnames as atoms inside a larger structural key. For example, a nominal fullname can
distinguish `builtins.list` from `builtins.dict`, but the type key distinguishes `list[int]` from `list[str]`.

Dynamic fullname suffixes using `@` are universe-level nominal naming details. Type-key opaque references use `$n`
markers only inside writer-controlled reference positions, so the two mechanisms do not overlap.

## This Chunk

The type-key module now has a small private writer/fragment layer.

The public `TypeKey` alias is now a `NewType` over `object`. The actual values produced today are compact strings when
possible, or tuples whose first element is the compact string spine followed by opaque payload objects.

Examples from the new public key shape:

```python
"I['builtins.int']"
"I['builtins.list',I['builtins.int']]"
"U[I['builtins.int'],I['builtins.str']]"
"RA[I['builtins.list',AR[0]]]"
("L[$0,I['tuple']]", (1.5,))
```

The previous tuple representation still exists as a private migration/debug helper:

```python
_tuple_type_key(...)
_tuple_type_key_or_none(...)
```

Those helpers intentionally produce the old nested tuple shape, and tests use them where exact recursive-alias
structure is still easier to read that way.

The current string writer is deliberately conservative:

- inline literal scalars are limited to `bool`, exact `int`, `str`, and `bytes`;
- floats are opaque for now;
- unhashable opaque payloads still fail closed;
- ordered forms such as `Annotated` can use opaque payload refs;
- unions are string-keyed only when all members are fully stringable.

The union limitation is intentional for this chunk. Unions are semantically unordered, so opaque payload refs cannot be
assigned by traversal order without creating order-sensitive keys.

## Union Direction

The next type-key step should make only the hard union case use an unordered opaque bucket.

The target model is:

- build union child fragments independently;
- sort fully stringable child fragments by deterministic string text;
- if hybrid child fragments remain, put their finished child keys into a `frozenset`;
- add a distinct union-bucket marker in the parent string, such as `OU[$0]`;
- store the `frozenset[TypeKey]` as the referenced opaque object.

That keeps common unions string-only while preserving correctness for cases like unions of opaque literal values.

This is intentionally distinct from `Literal[frozenset(...)]`: the union bucket marker lives in the string spine, so the
structural meaning remains explicit.

## Recursive Types

Recursive alias support is preserved at the current level.

Direct, indirect, and parameterized recursive aliases still use stack-relative alias references. In the compact string
form these appear as markers such as `RA[...]` for recursive aliases and `AR[...]` for alias backreferences.

This work does not attempt to solve mutually recursive graph canonicalization, graph isomorphism, or full coinductive
recursive equality. Those remain punted. The hybrid key work is intended to preserve the existing recursive behavior
while making the common non-recursive and current recursive paths cheaper to compare.

## Next

Near-term follow-up work:

- implement the opaque union bucket instead of failing closed for hybrid union members;
- add more tests around opaque literals, ordered `Annotated` metadata, and union order-insensitivity;
- consider per-reflector caching of exact and alpha type keys;
- decide whether member-signature keys should get a dedicated builder helper instead of manually returning tuple keys;
- keep recursive alias keying stack-relative for now and revisit deeper recursive canonicalization later.
