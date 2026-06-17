# Algorithm Surface Audit

This checkpoint follows `41_Recursive_Structural_Key_Hardening.md`.

The next mid-term goal is to put more real type-checker machinery behind the reflection surface:

```text
constraints, solve, substitution, subtype, meet, and join
```

The project is already more than a normalizer, but the algorithm layer is still intentionally partial. This audit
records what is currently solid, where it fails closed, and what order is most useful for the next implementation
chunks.

## Style Note

For operations on one `Type` object, prefer `TypeVisitor` or `DefaultTypeVisitor` over long repeated
`isinstance(..., TypeSubclass)` checks. That matches the direction of the core IR and keeps single-type traversal logic
maintainable.

Pairwise operations are different. Constraint inference, subtype, meet, and join compare two type objects and branch on
their relationship, so they should not be forced into a single-object visitor shape. Helper traversals inside those
algorithms should still use visitors where practical.

`substitute.py` already follows this direction by delegating to `ExpandTypeVisitor`.

## Substitution And Expansion

Current state:

- `substitute_type` and `substitute_types` validate replacement keys and values, then call `expand_type`.
- `ExpandTypeVisitor` handles `TypeVarType`, `ParamSpecType`, `TypeVarTupleType`, and tuple unpack expansion.
- Variadic tuple substitution is covered, including recursive variadic aliases from the recent near-term pass.
- Invalid substitution keys and values raise reflection errors rather than builtin exceptions.

Known gaps and cautions:

- Most behavior comes from generic `TypeTranslator` traversal, so it is broad but not deeply policy-aware.
- Alias target expansion depends on callers using `get_type_alias_target` or the algorithms that already expand aliases.
- More tests are useful around recursive aliases that combine ordinary `TypeVar` and `TypeVarTuple` parameters in the
  same target.

Next useful work:

- Add cross-operation tests proving that constraint solutions can be fed through substitution and reconstruct expected
  runtime shapes.
- Add mixed generic plus variadic recursive alias substitution coverage before changing algorithm code.

## Constraint Inference

Current state:

- Direct `TypeVarType`, `ParamSpecType`, and `TypeVarTupleType` capture is supported.
- Instance constraints understand variance and generic base remapping through `get_base_instance`.
- `AnnotatedType` and `TypeGuardedType` are transparent.
- `TypeType`, fixed `TupleType`, `TypedDictType`, `CallableType`, `Overloaded`, and `UnionType` have focused support.
- Callable constraints include `ParamSpec` and `Concatenate`-like prefix capture.
- Tuple constraints include a single variadic capture in the template with prefix and suffix support.
- Recursive aliases are handled through a coinductive alias-pair assumption set.
- Ambiguous unions, unsupported variadics, malformed aliases, and callable shapes outside the current subset raise
  `UnsupportedTypeOperationError`.

Known gaps and cautions:

- Union matching is intentionally strict and can reject useful but ambiguous-looking shapes.
- Actual-side variadic tuples remain unsupported.
- Generic callable variables beyond the current `ParamSpec` pattern fail closed.
- Recursive alias support is bounded and practical, not a full recursive constraint solver.
- Constraint inference currently treats concrete leaf disagreement as unsupported rather than using subtype-compatible
  fallback in every place.

Next useful work:

- Build a shared recursive algorithm corpus mirroring the structural-key tests.
- Add constraints for JSON-like recursive aliases, repeated variable positions, and NewType/literal leaves.
- Add cross-operation tests that solve constraints and substitute them back into templates.

## Solve

Current state:

- `solve_constraints` groups constraints by original variable identity.
- Ordinary `TypeVarType` solution uses joined lower bounds and met upper bounds.
- Type variable value restrictions and upper-bound validation are implemented.
- `ParamSpecType` and `TypeVarTupleType` solutions require packed candidates of the expected shape and exact same-type
  agreement.
- Strict unconstrained solving returns `UninhabitedType`; loose solving returns special-form `AnyType`.

Known gaps and cautions:

- Packed variable solving is intentionally conservative and equality-based.
- Recursive alias solutions rely on `is_same_type`, so structural-equivalent recursive solutions are not automatically
  accepted.
- There is no policy knob for structural solving.
- There is no dependency ordering between variables beyond independent grouping.

Next useful work:

- Add tests for repeated constraints that solve to recursive aliases and finite unrollings.
- Decide case by case whether solve should stay nominal/same-type or gain an explicit structural solve variant.

## Subtyping

Current state:

- Nominal and structural subtype entrypoints exist.
- `AnnotatedType` and `TypeGuardedType` are transparent.
- `AnyType`, `UninhabitedType`, unions, literals, fixed tuples, callables, overloaded callables, `TypeType`,
  `TypedDictType`, and `Instance` have support.
- Instance subtyping handles MRO membership and generic base remapping.
- Recursive alias subtyping is bounded by an alias-pair assumption set.
- Variadic tuple subtype cases fail closed.

Known gaps and cautions:

- Protocol behavior is not mypy-complete.
- Generic callable variables fail closed in subtype checks.
- Variadic tuple subtype support is deliberately narrow.
- Some unsupported subtype checks bubble into meet/join as `UnsupportedTypeOperationError`.

Next useful work:

- Add law tests around recursive aliases: if structural equivalence holds, subtype both directions should hold.
- Improve only the subtype cases that block constraints, meet, or join for marshal/DI shapes.

## Meet And Join

Current state:

- Nominal and structural meet/join entrypoints exist.
- `AnnotatedType` and `TypeGuardedType` are transparent.
- Unions are simplified with subtype/equivalence callbacks.
- Fixed tuples synthesize itemwise meet/join when fallbacks match.
- Simple callable shapes synthesize contravariant/covariant meet/join.
- Overloaded callables are itemwise when counts and callable shapes line up.
- TypedDict meet/join has focused support.
- Structural meet/join expands nonrecursive aliases and handles recursive aliases, including variadic recursive tuple
  aliases from recent work.
- NewType identity is preserved through structural alias operations.

Known gaps and cautions:

- Variadic tuple meet/join outside recognized alias-to-fixed forms fails closed.
- Generic callables fail closed.
- Incompatible recursive aliases currently produce a union for join and uninhabited for meet.
- Operations rely heavily on subtype; unsupported subtype relations therefore block meet/join.

Next useful work:

- Add shared recursive corpus tests for meet/join using JSON-like aliases and repeated variable aliases.
- Add cross-operation laws: if `A <: B`, then `join(A, B) == B` and `meet(A, B) == A`.
- Keep broad callable and variadic lattice work out of scope unless runtime adapter work exposes it.

## Runtime Ops

Current state:

- Runtime tests exercise constraints, solve, substitution, subtype/assignability, meet, join, structural keys, and MRO
  remapping through `reflect_*` entrypoints.
- Module-global-style typing forms hit reflector caches for reflection, keys, and annotation emission.
- Recursive alias runtime tests now cover structural keys, equivalence, join, meet, and constraint inference.

Known gaps and cautions:

- Runtime operation tests are broad, but not yet organized as a reusable compatibility suite for old `_reflect` users.
- No adapter spike has yet forced the algorithms through the exact marshal factory dispatch path.
- Thread-safe cache semantics remain future work.

Next useful work:

- Keep adding runtime tests alongside each core algorithm improvement.
- Prefer realistic `typing` forms over hand-built IR for runtime tests.

## Proposed Implementation Order

The next autonomous chunks should be:

1. Add shared recursive algorithm tests in core for constraints, solve, subtype, meet, and join using the same JSON-like
   and repeated-variable shapes from structural keys.
2. Patch only the algorithms exposed by those tests, keeping unsupported cases fail-closed.
3. Add runtime `reflect_*` parity tests for the same shapes.
4. Add substitution reconstruction tests: infer constraints, solve them, substitute into the template, and compare with
   the expected actual or recursive unrolling.
5. Repeat with NewType and Literal leaves, because marshal dispatch depends on preserving both.

The strategic constraint remains: build the machinery toward real recursive alias support without trying to recreate
all of mypy in one pass.
