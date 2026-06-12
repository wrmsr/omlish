# Recursive Runtime Keys And Enum Literals

This checkpoint covers the work after `35_Type_Key_Policies_And_Exception_Surface.md`.

The main line of work returned to recursive aliases and structural type keys. The smaller aside tightened literal
handling around mypyc compatibility and added mypy-style runtime enum literal support.

## Recursive Key Alignment

The previous checkpoint left recursive type keys as the next strategic pressure point. The important question was
whether structural keys agree with structural equivalence for the recursive alias shapes that marshal caches will
eventually rely on.

The first slice strengthened the core type-key builder:

- recursive alias canonicalization now uses `is_alpha_structurally_equivalent` when the active key policy is
  alpha-aware;
- non-alpha structural policies continue to use `is_structurally_equivalent`;
- recursive canonicalization still fails closed by returning `None` when the comparison path raises a reflection error.

This was deliberately small. It did not redesign recursive keys. It made the existing policy-driven builder use the
same equivalence flavor that the caller requested.

New core tests now pin the key/equivalence contract for:

- concrete parameterized recursive aliases with different alias identities;
- alpha-equivalent generic recursive aliases;
- one-unrolled recursive aliases;
- mutually recursive alias graphs;
- negative cases where recursive structures are not structurally equivalent and must not share structural keys.

The tests are written as invariants: when structural equivalence says two forms are equivalent, the matching structural
key helper should agree; when equivalence rejects the forms, the keys should differ.

## Runtime Recursive Key Coverage

The next slice moved the same contract through the actual runtime-facing path:

```text
typing object -> RuntimeTypeReflector -> core Type -> structural key
```

Runtime tests now cover recursive `typing.TypeAliasType` forms including:

- concrete generic recursive aliases;
- reordered union unrollings;
- mutually recursive aliases;
- incompatible recursive aliases;
- alpha-structural generic recursive aliases.

These tests matter because the marshal-facing cache path starts with runtime type objects, not hand-built IR. They make
sure the useful property survives runtime reflection and reflector-level key caching.

## Broader Recursive Runtime Shapes

After the basic recursive alias/key contract was pinned, we broadened the tested shape coverage. Runtime structural keys
now have explicit tests for recursive aliases involving:

- callable return positions;
- callable argument positions;
- `ParamSpec` and `Concatenate`;
- fixed tuples;
- nested `typing.Mapping[str, list[Alias]]`;
- `Annotated` wrappers around recursive targets and recursive references.

Most of these shapes were already supported by the existing machinery. The tests make that fact explicit and give us a
better boundary map before attempting deeper recursive key or recursive constraint work.

One real reflection gap showed up during this pass. Runtime `TypeAliasType` type parameters were only accepted if they
reflected to `TypeVarType`. The core `TypeAlias` model already accepts `TypeVarLikeType`, so runtime alias parameter
reflection was widened to accept all type-var-like nodes. This enabled ParamSpec-backed runtime aliases without changing
runtime class generic parameter handling.

## Enum Literal Aside

The aside started from a mypyc blocker: `LiteralType.value` is annotated as `LiteralValue`, but tests were intentionally
constructing `LiteralType` with arbitrary opaque objects such as tuples, dataclass instances, frozensets, and lists.

That was not a good invariant. Mypy's model keeps `LiteralType.value` narrow. Even enum literals are not represented as
the enum object itself. In mypy, a form like `Literal[Color.RED]` is represented as:

```text
LiteralType(value='RED', fallback=Instance(Color))
```

The enum member identity is split between the member name string and the enum fallback type.

The implementation now follows that model:

- `LiteralType` validates that its value is a supported `LiteralValue`;
- runtime reflection maps enum members to `LiteralType(member.name, Instance(member.__class__))`;
- runtime enum classes produce `TypeInfo` objects marked as enums, with enum member names recorded;
- `type_str()` renders enum literals using the enum fallback and member name;
- type keys already include the literal fallback key, so `Literal['RED']` and `Literal[Color.RED]` remain distinct.

The tests that previously used invalid opaque literal values were rewritten to use `AnnotatedType` metadata instead.
That preserves coverage for opaque `$n` reference payloads and order-insensitive opaque union buckets without corrupting
the `LiteralType` invariant.

## Runtime Enum Literal Query

The internal IR remains mypy-style, which means ordinary literal value queries return enum member names for enum
literals. That is useful for keeping core algorithms close to mypy.

Runtime users such as marshal validation often want actual runtime enum members. To support that without changing the
core IR, the runtime query layer now has:

- `RuntimeLiteralValueType`;
- `get_runtime_literal_value_type`;
- `reflect_runtime_literal_value_type`.

These reconstruct enum members from `LiteralType.value` plus the enum fallback when the runtime enum class is available
from the universe. Mixed enum-member and plain-string literal sets intentionally return `None` from the runtime-value
query, even though the mypy-style query can still see a homogeneous string-name set internally.

Runtime annotation emission also uses the same reconstruction path. A reflected enum literal can round-trip back to a
runtime annotation like `Literal[Color.RED]` rather than `Literal['RED']`.

## Verification

The focused checks covered:

- type-key behavior;
- runtime query behavior;
- runtime annotation behavior;
- runtime operation behavior.

The full test suite was also run:

```bash
.venv/bin/python -m pytest mypydistill
```

and passed.

The standard completion gate also passed:

```bash
make fix check
```

## Current Direction

The recursive key and runtime reflection story is now stronger for common marshal-cache shapes, but the larger strategic
problem remains open.

Immediate useful next steps:

- keep comparing structural keys against structural equivalence for harder recursive shapes;
- remove any remaining dependence on alias entrypoint identity where structural policies should erase aliases;
- keep recursive constraint solving fail-closed until recursive keys and equivalence are firmer;
- continue cleaning small mypyc blockers where public core annotations do not match real runtime values.

Mid-term goals remain:

- recursive alias/type-key behavior strong enough for marshal caches;
- eventual recursive constraint solving;
- better alignment among structural equivalence, structural subtype, structural keys, meet/join, and solve;
- stable runtime reflection surfaces for dataclass, marshal, and injector use cases;
- eventual cache/thread-safety design once the operation surfaces settle.
