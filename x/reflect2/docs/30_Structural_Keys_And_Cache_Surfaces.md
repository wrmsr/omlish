# Structural Keys And Cache Surfaces

This checkpoint covers the work after `29_Alias_Preservation_And_Recursive_Structure.md`.

The main theme was turning recursive structural comparison into cache-usable key machinery. The system already had
nominal keys, alpha keys, alias preservation, structural equivalence, and structural subtype checks. The next gap was
that marshal- and DI-facing caches need stable keys that can recognize equivalent recursive runtime type shapes even
when they were written through different aliases or through one or more explicit unrollings.

## What Changed

The core type-key layer now has explicit structural key APIs:

- `structural_type_key`;
- `structural_type_key_or_none`;
- `alpha_structural_type_key`;
- `alpha_structural_type_key_or_none`.

These are implemented through `_StructuralTypeKeyBuilder`, a subclass of the existing `_TypeKeyBuilder`. This kept the
writer/traversal machinery shared instead of adding a parallel key implementation.

Structural keys currently:

- erase non-recursive alias identity;
- strip `Annotated` metadata;
- preserve NewType identity;
- preserve the same literal/union ordering and opaque-literal behavior as nominal keys;
- support alpha-canonical variables through the alpha variant;
- support recursive alias binder/ref keys for corresponding recursive alias graphs.

The recursive structural-key path was then hardened so that aliases and finite unrollings produce the same structural
key. For a recursive alias like:

```python
Node = int | list['Node']
```

the following now share a structural key:

```python
Node
int | list[Node]
int | list[int | list[Node]]
```

This is still not a complete theorem-prover for arbitrary recursive type graphs, but it now lines up with the practical
recursive alias cases covered by `is_structurally_equivalent`.

## Runtime Key Caches

`RuntimeTypeReflector` now caches the new key families:

- `structural_type_key`;
- `structural_type_key_or_none`;
- `alpha_structural_type_key`;
- `alpha_structural_type_key_or_none`.

The runtime ops layer exposes matching object-reflection helpers:

- `reflect_structural_type_key`;
- `reflect_structural_type_key_or_none`;
- `reflect_alpha_structural_type_key`;
- `reflect_alpha_structural_type_key_or_none`.

The tests verify that repeated calls reuse cached key objects in the reflector, mirroring the existing nominal and alpha
key cache behavior.

## Annotation Emission

Recursive aliases exposed a runtime annotation emission boundary. Non-recursive aliases can be expanded into finite
runtime annotations, but recursive aliases cannot be faithfully expanded without infinite recursion.

The annotation policy is now:

- non-recursive aliases still expand by default;
- explicit preserve policy still preserves runtime aliases;
- recursive aliases are preserved even under the default expand policy.

This lets dataclass and namedtuple inspection handle recursive alias fields without recursing indefinitely while keeping
existing non-recursive generated-signature behavior stable.

## Cache-Facing Surfaces

Structural keys were added to runtime surfaces that are likely to feed marshal/DI caches.

Dataclass inspection now exposes:

- `field_type_keys`, the existing nominal keys;
- `field_structural_type_keys`, new structural keys.

Namedtuple inspection now exposes the same pair.

Record inspection now exposes both on each `RuntimeRecordField`:

- `type_key`;
- `structural_type_key`.

Helpers were added for field structural key maps:

- `reflect_dataclass_field_structural_type_keys`;
- `reflect_namedtuple_field_structural_type_keys`.

Member and protocol surfaces also gained structural key helpers:

- `member_structural_signature_key`;
- `get_member_call_structural_signature_key`;
- `get_member_value_structural_type_key`;
- `get_protocol_member_structural_key`;
- `get_protocol_member_structural_keys`.

`RuntimeProtocolInspection` now stores `member_structural_keys` in addition to existing `member_keys`.

Protocol checking itself was not changed. Existing checking still uses the current effective/unaliased key behavior and
special property subtype logic. The structural protocol keys are additive so callers can experiment with structural
cache matching without changing protocol-check semantics.

## Runtime Type Key Bundle

A small runtime key bundle was added for callers that need to choose key policy explicitly:

```python
RuntimeTypeKeys(
    nominal,
    structural,
    effective,
    alpha_structural,
)
```

The helpers are:

- `get_runtime_type_keys`;
- `reflect_runtime_type_keys`.

This gives cache-heavy code a single low-level place to ask for all relevant key views of a reflected type:

- `nominal` preserves alias identity and NewType identity;
- `structural` erases alias identity, handles recursive unrolling, strips `Annotated`, and preserves NewType identity;
- `effective` keys `RuntimeTypeShape.effective`, which expands aliases and unwraps top-level NewType;
- `alpha_structural` is the alpha-variable structural key.

## Effective vs Unaliased Keys

This work clarified a naming problem in the earlier runtime query layer.

There are two distinct useful concepts:

- unaliased key: expand aliases but preserve NewType identity;
- effective key: expand aliases and unwrap top-level NewType.

The old `get_runtime_effective_type_key` actually returned the unaliased key. Existing member/protocol code depended on
that behavior because it must preserve NewType identity.

To make the distinction explicit, new helpers were added:

- `get_runtime_unaliased_type_key`;
- `reflect_runtime_unaliased_type_key`.

Internal member/protocol keying now uses the new unaliased helper name. The old effective-key helpers remain as
compatibility aliases for now, with comments documenting that they preserve NewType identity.

The newer `RuntimeTypeKeys.effective` field uses the true effective key.

## Tests

The suite now covers:

- structural keys for non-recursive aliases vs expanded targets;
- structural keys preserving NewType identity;
- `Annotated` stripping for structural keys;
- alpha structural keys through type variables;
- recursive aliases vs one and multiple unrollings;
- nested recursive alias unrollings inside containers;
- mutually recursive aliases and corresponding entrypoints;
- multiple recursive aliases in one union;
- recursive alias annotation emission;
- dataclass, namedtuple, record, member, and protocol structural key surfaces;
- distinction between nominal, structural, unaliased, effective, and alpha-structural runtime key views.

The last full verification run was:

```bash
.venv/bin/python -m pytest mypydistill
```

with `747 passed`.

## Current Boundaries

The structural-key machinery is now useful, but still bounded.

Important boundaries:

- recursive structural keys are aligned with the tested alias/unrolling shapes, not every possible recursive graph;
- structural key generation consults structural equivalence for recursive alias canonicalization, so it is more
  expensive than nominal key generation;
- existing protocol checking has not switched to structural keys by default;
- the old effective-key helper names remain for compatibility even though the new unaliased helper names are clearer;
- cache/thread-safety remains single-thread-assumed mutable dict behavior for now;
- meet/join/inference/solve are not yet recursive-structural-aware.

These boundaries are acceptable for the current goal: make runtime reflection and marshal-facing cache keys materially
more capable without pretending the entire type-system problem is solved.

## Immediate Goals

Likely next steps:

- Decide whether protocol checking should gain an explicit structural mode or remain key-exact with additive
  structural helper APIs.
- Add equivalent structural-key bundle helpers for records/members if repeated caller patterns show friction.
- Add tests for structural keys involving recursive aliases inside generic dataclass inheritance and substituted MRO
  entries.
- Audit `RuntimeTypeKeys.effective` naming and old compatibility helpers after a little usage; consider deprecating the
  old names internally if no code needs them.
- Add fail-closed tests for structural key generation over unsupported recursive shapes.

## Mid-Term Goals

The mid-term direction is now cache- and replacement-focused.

Important goals:

- Build a thin experimental adapter that exposes old `_reflect`-style marshal-facing facts using the new runtime
  reflection system.
- Exercise that adapter against representative marshal use cases: literals, NewTypes, aliases, recursive aliases,
  dataclasses, generic field replacement, collections, and polymorphic unions.
- Decide which key policy marshal caches should use by default:
  - nominal for alias-sensitive dispatch;
  - structural for recursive shape caches;
  - unaliased for alias-erased but NewType-sensitive matching;
  - effective for stencil-like or representation-only dispatch.
- Improve recursive structural key canonicalization if real adapter tests find false misses.
- Revisit thread safety and cache locking once the cache surfaces stabilize.
- Keep core/runtime separation intact so core type algorithms remain plausible mypyc candidates.

Longer-term work remains:

- recursive-aware meet/join;
- better structural subtype coverage;
- inference, constraints, and solve;
- a more complete story for recursive aliases and alpha-equivalent variables in all key/comparison layers.

The key milestone from this interval is that recursive aliases are no longer only comparable. They are now keyable in a
way that is usable by runtime caches, while callers can still choose nominal, structural, unaliased, or effective views
explicitly.
