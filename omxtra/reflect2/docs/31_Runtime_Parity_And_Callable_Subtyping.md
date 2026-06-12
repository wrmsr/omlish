# Runtime Parity And Callable Subtyping

This checkpoint covers the work after `30_Structural_Keys_And_Cache_Surfaces.md`.

The main arc was to prove the new runtime reflection surface against old `_reflect`-style marshal and dataclass use
cases, then pivot back toward algorithm depth. The adapter work is intentionally still experimental. The priority is
now to make sure the type machinery underneath the runtime surface can support heavier operations later.

## What Changed

Generic dataclass substitution now handles recursive aliases in inherited fields. A case like:

```python
Node = int | list['Node']

@dataclasses.dataclass
class Box[T]:
    value: T

@dataclasses.dataclass
class NodeBox(Box[Node]):
    pass
```

now reflects the inherited `value` field as the recursive alias shape, and its structural key matches finite unrollings
such as `int | list[Node]` and `int | list[int | list[Node]]`.

The core change behind this was allowing direct `T -> TypeAliasType` substitution in `expand_type`. The previous guard
rejected a direct replacement of a proper `TypeVarType` with a non-proper `TypeAliasType`. That was too strict for the
runtime reflection model, where alias nodes are intentionally preserved for identity and recursion.

## Recursive Structural Key Boundaries

Structural key fail-closed behavior was hardened. Tests now cover unsupported recursive alias targets and unsupported
unrolled recursive shapes. The strict APIs raise, while `_or_none` variants return `None` and cache that `None` without
populating strict key caches.

This keeps cache behavior conservative. A shape outside the currently supported recursive-key model should not silently
produce a misleading key.

## Recursive Containers

Runtime collection query coverage now includes recursive aliases inside common marshal-facing containers:

- `list[Node]`;
- `NodeList = list[Node]`;
- `Mapping[str, Node]`;
- `NodeMap = Mapping[str, Node]`;
- finite unrolled equivalents.

These tests prove both dispatch facts and cache facts:

- sequence item recovery;
- mapping key/value recovery;
- effective mapping base arguments;
- structural key equality between alias-wrapped containers and expanded/unrolled containers.

This exposed and fixed a real structural-key issue. Non-recursive alias erasure in `_StructuralTypeKeyBuilder` was
pushing the erased alias onto the recursive alias stack. That shifted recursive alias reference indexes, causing
`NodeList = list[Node]` to key differently from `list[Node]`. Structural non-recursive alias erasure now expands the
alias without adding it to the recursive alias stack.

## Old Reflect Parity Spike

A new parity-style test module was added:

```text
mypydistill/runtime/tests/test_oldreflectparity.py
```

It is not an adapter API. It is a compact checklist of old `_reflect`-style facts that marshal and dataclass-like users
need:

- optional item extraction;
- finite literal value extraction;
- NewType identity and supertype/effective shape;
- nested collection dispatch for `list[Mode]` and `Mapping[str, list[Mode]]`;
- generic dataclass field replacement for `Box[T]` and `ModeBox(Box[Mode])`;
- record field facts for dataclasses;
- recursive alias cache facts for `Node` and `NodeList`.

This also clarified an important usage boundary: runtime-object `reflect_*` helpers and IR-level `get_*` queries are
different surfaces. When code already has a `types.Type`, it should use the `get_*` query functions instead of feeding
that IR node back through runtime reflection.

## Runtime Type View

A small experimental view bundle was added:

```text
mypydistill/runtime/views.py
```

It defines:

```python
RuntimeTypeView(
    typ,
    shape,
    collection,
    mapping,
    dispatch,
    keys,
)
```

with helpers:

- `get_runtime_type_view`;
- `reflect_runtime_type_view`.

This is deliberately just composition over existing query APIs:

- `get_runtime_type_shape`;
- `get_runtime_collection_shape`;
- `get_runtime_mapping_shape`;
- `get_runtime_dispatch`;
- `get_runtime_type_keys`.

It is not intended to finalize the public API. It gives adapter and replacement experiments one small object to pass
around while preserving the lower-level query surfaces.

## Callable Subtyping

The algorithm work then pivoted back to `subtypes`.

`CallableType` subtyping now handles a slightly broader but still conservative subset:

- return types are covariant;
- parameter types are contravariant;
- the left/implementation callable may accept extra optional positional arguments;
- the left/implementation callable may accept extra optional keyword-only arguments;
- extra required arguments still make the subtype relation fail;
- keyword-only required arguments must match by name;
- generic callable and ParamSpec cases still fail closed;
- star args and `**kwargs` remain conservative and require exact shape for now.

This is not a full port of mypy's callable compatibility algorithm. Mypy's logic is much broader, with substantial
handling for overloads, partial overlap, varargs, ParamSpec, Concatenate, and name matching policy. The current slice is
meant to support realistic method and callback shapes without committing to that entire matrix yet.

## Current State

The runtime replacement surface is now meaningfully stronger than a pure normalizer:

- runtime typing objects reflect into a mypy-like IR;
- generic runtime MRO and dataclass field substitution work;
- literals, NewTypes, aliases, recursive aliases, records, members, and protocols have explicit query surfaces;
- recursive structural keys are cache-usable across practical alias/unrolling cases;
- old `_reflect`-style facts have parity tests;
- a small runtime view bundle exists for adapter experiments.

The algorithm side is improved but still uneven:

- substitution and expansion are useful across many nodes;
- subtyping covers nominal instances, variance, typed dicts, unions, structural/alpha equivalence, recursive aliases,
  and a growing callable subset;
- meet and join exist for a useful subset;
- constraints, solve, and inference are still not a meaningful toolbox.

The latest full verification run was:

```bash
.venv/bin/python -m pytest mypydistill
```

with `763 passed`.

## Current Boundaries

Important boundaries remain:

- runtime view APIs are experimental and should not be treated as finalized public facade;
- recursive structural keys are practical and tested, not complete for every recursive graph;
- structural key generation is still heavier than nominal key generation;
- protocol checking still has its own key-exact behavior rather than a fully structural mode;
- callable subtyping is intentionally partial;
- `TypeType`, constructor/class-object semantics, overload subtyping, ParamSpec/Concatenate, and full callable
  compatibility remain future work;
- meet/join do not yet have recursive-structural strength;
- constraints/solve/inference are still mostly ahead of us;
- cache thread safety remains a known future issue.

## Immediate Goals

The next immediate direction is algorithm-focused rather than adapter-focused.

Recommended next steps:

- Add `TypeType` / class-object subtyping:
  - `type[Child] <: type[Base]`;
  - not the reverse;
  - preserve sensible `Any` and `Never` behavior;
  - fail closed for unsupported item relations.
- Continue callable subtyping in small increments:
  - better runtime callable forms where reflected annotations already provide enough information;
  - keep ParamSpec and Concatenate fail-closed until there is a coherent design.
- Add small meet/join tests that rely on the strengthened subtyping behavior, but avoid large rewrites.
- Keep old-reflect parity tests as a regression harness, but do not finalize adapter APIs yet.

## Mid-Term Goals

Mid-term work should deepen the mypy-derived machinery enough that runtime reflection can rest on it confidently:

- broaden subtyping with mypy-derived tests where the behavior is relevant to runtime type forms;
- strengthen meet and join around instances, unions, callables, `TypeType`, and recursive aliases;
- start a minimal constraints/solve slice only after subtyping and meet/join are less brittle;
- keep recursive alias equivalence and structural keys aligned with any new subtype/meet/join behavior;
- preserve the core/runtime separation so algorithm-heavy modules remain plausible mypyc candidates;
- revisit thread-safe cache design once the key/view/query surfaces are more stable;
- eventually build a thin old `_reflect` adapter or migration spike, using parity tests and runtime views as scaffolding,
  but only after the core algorithms have more weight behind them.

The current strategic choice is to pause API polish and adapter finalization. The runtime surface is close enough to
exercise real old-system facts; the next value comes from making the underlying type algorithms less shallow.
