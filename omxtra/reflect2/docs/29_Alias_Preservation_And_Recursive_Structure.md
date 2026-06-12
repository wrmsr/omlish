# Alias Preservation And Recursive Structure

This checkpoint covers the work after `28_Runtime_NewType_Literal_Surface.md`.

The main theme was moving from “aliases expand away for convenience” toward a two-view model: runtime aliases are
preserved as nominal facts, while callers that need structural behavior can explicitly ask for expanded/effective
comparison. This is important for marshal and injector use cases because alias identity can carry meaning, but the
same code also needs to understand that an alias may structurally be a `list[Mode]`, a recursive union, or some other
runtime-usable shape.

## What Changed

Runtime reflection now preserves non-recursive `typing.TypeAliasType` objects as `TypeAliasType` IR nodes. Before this
work, non-recursive aliases reflected as their expanded targets. For example, an alias like:

```python
ModeList = TypeAliasType('ModeList', list[Mode])
```

now reflects as an alias node whose symbol retains the original runtime alias object. The expanded target remains
available through helper paths, but it is no longer the only representation.

Runtime annotation emission gained an explicit alias policy:

- `expand`, the default, emits expanded annotations such as `list[Mode]`;
- `preserve` emits the original runtime alias object when available, including parameterized alias forms.

This keeps generated-signature behavior stable while giving DI/marshal-style code access to nominal alias identity
when that identity matters.

`RuntimeTypeShape` now exposes alias facts directly:

- `alias`, with the runtime alias object, alias node, and expanded target;
- `unaliased`, the alias-expanded type;
- `effective`, which expands aliases and then unwraps a top-level `NewType` supertype.

The query layer also gained effective type-key helpers so callers can choose between nominal alias keys and structural
effective keys.

Type keys now preserve runtime alias object identity for non-recursive runtime aliases. Two distinct runtime aliases
with the same name and target no longer collapse into the same nominal key. This is intentionally different from
effective structural comparison.

Protocol/member keying was adjusted to use effective type keys where the operation is structural. This means a
protocol member annotated as an alias can still match a concrete member annotated as the expanded type, while raw
nominal keys continue to distinguish the alias.

## Recursive Comparisons

The larger recursive-type work started with explicit structural comparison APIs instead of changing existing nominal
ones.

Core APIs added:

- `is_structurally_equivalent(left, right)`;
- `is_alpha_structurally_equivalent(left, right)`;
- `is_structural_subtype(left, right)`.

Runtime wrappers added:

- `reflect_is_structurally_equivalent`;
- `reflect_is_structurally_equivalent_or_false`;
- `reflect_is_alpha_structurally_equivalent`;
- `reflect_is_alpha_structurally_equivalent_or_false`;
- `reflect_is_structural_subtype`;
- `reflect_is_structural_subtype_or_false`.

These operations expand aliases on either side and use local recursive alias-pair assumptions to avoid infinite
expansion. They are intentionally separate from `is_same_type` and `is_subtype`, which remain nominal/current-behavior
operations.

The tested recursive cases now include:

- non-recursive alias vs expanded target;
- recursive alias vs one unrolling of itself;
- same recursive structure under different alias names;
- negative recursive comparisons with different leaves;
- alpha-equivalent generic recursive aliases;
- alpha-equivalent mutually recursive generic aliases;
- directional structural subtyping through recursive unions;
- recursive structural subtype through covariant container arguments.

The runtime surface now demonstrates that an alias-preserved dataclass field can still participate in structural
equivalence/subtyping against its expanded form, while protocol checking continues to accept compatible expanded
members.

## Why

The original motivation for this repo was the need for a real foundation for recursive runtime types. The old
reflection system could normalize many runtime annotations, but recursive type support would have been an increasingly
fragile special case layered onto a small ad hoc IR.

Alias preservation is part of that foundation. Recursive aliases need stable identity anchors; non-recursive aliases
can also carry runtime meaning for marshal and injector dispatch. Expanding all aliases away made some structural
queries easy, but it destroyed nominal information that callers need.

The new direction is to keep both views available:

- nominal view: aliases, NewTypes, and runtime identity matter;
- structural view: aliases expand, recursive cycles are compared through assumptions, and callers can ask whether two
  forms have the same runtime-relevant shape.

This is not full mypy parity. It is a deliberately narrower runtime-useful recursive engine. The goal is not to become a
source checker; it is to give runtime systems reliable answers for reflected type forms.

## Current Boundaries

The recursive structural engine is still young.

It handles the recursive alias shapes now covered by tests, but it is not yet a full mypy-strength subtype engine.
Important current boundaries:

- structural subtyping only covers the subtype features already present in the local subtype implementation;
- unsupported relations still raise in strict APIs and return `False` in `or_false` wrappers;
- recursive assumptions are local to each comparison call and are not cached;
- alpha-equivalent structural comparison exists, but alpha-equivalent structural subtyping does not yet;
- recursive alias type keys still serve nominal/cache needs, not a complete canonical structural cache-key story;
- meet/join do not yet use recursive structural assumptions.

This is an acceptable boundary for now. The system can answer more real runtime questions than before without
pretending unsupported forms are understood.

## Immediate Goals

The next immediate work should keep strengthening the recursive runtime path without broad API polish.

Likely next steps:

- add more negative/fail-closed tests around recursive structural subtype for unsupported callable/generic/protocol
  cases;
- decide whether `is_assignable` should gain an explicit structural sibling at the core layer, or whether
  `is_structural_subtype` is the right primitive name for now;
- add structural comparison tests involving `Annotated`, `NewType`, and aliases together;
- exercise recursive structural comparison through record/dataclass field types, not only direct runtime ops;
- audit any remaining call sites that use nominal `type_key` where an effective key or structural comparison is more
  appropriate.

## Mid-Term Goals

The mid-term path is now clearer.

Important goals:

- design structural recursive type keys that line up with `is_structurally_equivalent`, including mutually recursive
  aliases and alpha-equivalent variables;
- decide how nominal alias keys, effective keys, and structural keys should coexist in cache-heavy callers;
- extend structural subtype carefully, especially around variance, callable forms, and union normalization;
- investigate recursive-aware meet/join only after structural subtype/equivalence have more coverage;
- add the thin experimental adapter that can mimic the old reflection system’s marshal-facing facts without depending
  on higher-level packages;
- keep reflection caches fast for module-global runtime type forms while deferring the final thread-safe/nogil cache
  design;
- preserve the core/runtime separation so the algorithm-heavy core remains mypyc-friendly.

Lower priority, but still relevant:

- richer recursive alias annotation-emission behavior;
- better diagnostics for recursive comparison failures;
- compound literal payload support if real marshal cases require it;
- broader protocol/callable assignability semantics borrowed from mypy where useful.

The important milestone is that recursive aliases are no longer just reflectable and keyable. They now participate in
explicit recursive structural equivalence and subtype operations, while nominal alias identity remains available for
runtime dispatch.
