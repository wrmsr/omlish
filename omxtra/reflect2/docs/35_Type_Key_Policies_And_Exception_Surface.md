# Type Key Policies And Exception Surface

This checkpoint covers the work after `34_Overloads_NewTypes_And_Constraint_Depth.md`.

The recent arc had three themes:

- type-key policy configuration;
- production-oriented exception cleanup;
- one more narrow constraint-inference slice.

The implementation stayed aligned with the current direction: keep the core mypyc-friendly, keep runtime reflection
isolated, and make unsupported behavior fail closed through package-level exceptions.

## Type Key Policy Refactor

Type keys now have an explicit policy object instead of hardcoded helper-specific behavior.

`TypeKeyPolicy` is a frozen dataclass with independent knobs:

- `alpha`;
- `structural`;
- `include_annotated_metadata`;
- `preserve_alias_identity`;
- `preserve_newtype_identity`.

The existing helpers remain as presets:

- `type_key`;
- `alpha_type_key`;
- `structural_type_key`;
- `alpha_structural_type_key`.

There are also policy-based entrypoints:

- `type_key_with_policy`;
- `type_key_with_policy_or_none`;
- `tuple_type_key_with_policy`;
- `tuple_type_key_with_policy_or_none`.

The older private policy helper still forwards to the public-core policy helper for local compatibility.

This keeps the user-facing surface stable while making it possible to build future marshal/cache-specific key policies
without adding a combinatorial set of helpers.

## Writer And Builder Cleanup

The type-key builder is now one configurable builder instead of separate nominal and structural builder classes.

The structural behavior that previously lived in a subclass was folded into `_TypeKeyBuilder` and controlled by
`TypeKeyPolicy`. This matters because recursive alias handling, annotation handling, alias identity, alpha variable
canonicalization, and NewType identity all need to compose without duplicated traversal logic.

`_TypeKeyFragment` was also changed from a dataclass into a simple slots class. That keeps the core style closer to the
mypyc-friendly shape used elsewhere in the type IR.

## NewType Key Policy

The `preserve_newtype_identity` policy knob is now real.

`TypeInfo` now carries optional NewType metadata:

- `new_type_supertype`;
- internally `_new_type_supertype`.

Runtime reflection populates this metadata for NewTypes. For class-backed NewTypes, the universe records a simple
class-backed supertype. The reflector then records the accurately reflected `__supertype__`, including cases such as
`NewType('Mode', Literal['a', 'b'])`.

Default type keys still preserve NewType identity. When a policy sets `preserve_newtype_identity=False`, NewType
instances key as their recorded supertype.

This gives future cache users a real choice:

- preserve NewType identity for marshal/DI dispatch where nominal distinction matters;
- erase NewType identity for optional structural/deduping use cases.

## Exception Surface Cleanup

Deliberate package-level exceptions now go through `ReflectionError` or a subclass.

The current hierarchy includes:

- `ReflectionError`;
- `ReflectionTypeError`;
- `ReflectionValueError`;
- `ReflectionRuntimeError`;
- `ReflectionInternalError`;
- `UnsupportedTypeOperationError`;
- `UnreflectableTypeError`;
- `ProtocolReflectionError`.

The important mypyc-facing rule is that these do not subclass builtin exception families like `TypeError`,
`ValueError`, or `RuntimeError`. Tests now pin that behavior.

Direct, intentional package raises such as `raise TypeError(...)`, `raise ValueError(...)`, and `raise RuntimeError(...)`
were converted. Catch sites that are meant to catch package failures were updated to catch `ReflectionError` or a
specific reflection subclass.

Incidental builtin errors are still allowed to bubble naturally. For example, code may still catch builtin `TypeError`
from Python operations such as hashing an unhashable `typing` object, using `inspect.signature`, or attempting runtime
subscription.

This is not a defensive wrap-everything policy. It is a rule for exceptions the package chooses to raise.

## Constraint Inference Progress

The constraints layer added two small pieces after the previous checkpoint.

First, strict ordered `Overloaded` vs `Overloaded` constraint inference was added. It mirrors the already-supported
ordered overload subtyping, meet, and join behavior:

- both sides must be `Overloaded`;
- item counts must match;
- items are compared in order;
- each pair uses existing same-shape callable constraint inference;
- unsupported item shapes fail closed.

Second, narrow same-shape `TypedDictType` constraint inference was added:

- both sides must be `TypedDictType`;
- item keys must match exactly;
- required keys must match exactly;
- readonly keys must match exactly;
- fallbacks must be the same type;
- readonly items infer covariantly;
- mutable items infer invariantly by adding constraints in both directions.

This intentionally does not try to implement broad mypy TypedDict matching. It supports the obvious same-shape extraction
case and raises `UnsupportedTypeOperationError` for shape mismatches.

## Verification Policy

The completion gate changed.

Going forward, a work chunk is not done until:

```bash
make fix check
```

passes. This runs the project fix/check stack, including ruff, flake8, and mypy. The core is expected to remain
mypyc-compliant, though mypyc itself is not currently part of this local verification step.

The latest verification run was:

```bash
make fix check
```

and it passed.

## Current State

The core operation surface now includes:

- nominal and structural subtype checks;
- alpha and alpha-structural equivalence;
- recursive alias-aware structural operations;
- nominal and structural meet/join;
- direct `TypeType` lattice behavior;
- same-shape callable subtyping, meet, join, and constraints;
- ordered pairwise overload subtyping, meet, join, and constraints;
- basic substitution and expansion;
- constraint inference for type variables, instances, aliases, unions, fixed tuples, same-shape TypedDicts, callables,
  overloads, and `TypeType`;
- first-pass constraint solving;
- policy-configurable type keys;
- runtime reflection of NewType identity and NewType supertype metadata.

The runtime surface now also has a cleaner production exception boundary. Application-level reflection failures are
package exceptions rooted at `ReflectionError`.

## Current Boundaries

Important unsupported areas remain:

- recursive alias constraint solving;
- fully structural recursive type keys for the hardest marshal-cache equivalence cases;
- ParamSpec and Concatenate solving;
- TypeVarTuple / variadic tuple solving;
- overload reordering or best-match semantics;
- overload-vs-callable subtyping, meet, and join;
- protocol-member-driven constraint inference;
- broader mypy-style union heuristics;
- richer TypedDict constraint matching beyond exact same shape;
- structural constraint inference variants;
- thread-safe cache design.

These remain fail-closed. Unsupported algorithm shapes should raise `ReflectionError` subclasses rather than returning
misleading results.

## Immediate Goals

The next likely direction is to return to recursive alias and type-key design.

The type-key policy refactor gives the right foundation for this. The next step should be to align structural recursive
keys more tightly with structural equivalence and with the cache behavior marshal ultimately needs.

Useful near-term slices:

- add more direct tests comparing structural keys against `is_structurally_equivalent` for recursive aliases;
- identify where current recursive key canonicalization still depends on alias entrypoint shape;
- keep NewType identity preservation as the default while testing policy-erased variants;
- continue keeping recursive constraint solving unsupported until the structural key story is firmer.

## Mid-Term Goals

The mid-term goals remain mostly unchanged:

- implement recursive alias/type-key behavior strong enough for marshal caches;
- align recursive structural equivalence, structural subtype, structural keys, and eventual recursive solving;
- keep expanding mypy-derived operations without importing source-checker assumptions;
- preserve runtime reflection usability for dataclass, marshal, and injector use cases;
- keep the runtime layer separate from the mypyc-friendly core;
- revisit in-memory caching and thread-safety once the operation surfaces are stable enough to freeze around.
