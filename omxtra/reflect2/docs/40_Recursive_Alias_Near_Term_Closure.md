# Recursive Alias Near Term Closure

This checkpoint follows `39_Runtime_Variadics_And_Tuple_Algorithms.md` and the subsequent near-term push around
recursive aliases, variadic aliases, constraints, substitution, runtime annotation emission, and cache surfaces.

The main goal for this pass was to stop treating recursive aliases as only a structural-key concern. The system already
had good coverage for recursive structural equivalence and for variadic tuple aliases separately. This round connected
those pieces through the other near-term surfaces that will matter for marshal and DI use cases.

## Constraint Inference

Constraint inference no longer rejects recursive aliases categorically.

The inferrer now carries a small coinductive alias-pair assumption set while it recursively descends into alias targets.
That lets it intentionally unroll recursive aliases far enough to compare an alias with one unrolling, while avoiding
infinite recursion on the self-reference.

The important supported shape is now:

```python
Ts = typing.TypeVarTuple('Ts')
TupleNode = typing.TypeAliasType(
    'TupleNode',
    tuple[*Ts, 'TupleNode[*Ts]'],
    type_params=(Ts,),
)
```

For `TupleNode[int, str]` and one unrolling `tuple[int, str, TupleNode[int, str]]`, runtime and core tests now show
constraint inference is intentional rather than accidentally unsupported. The generic template form can solve `Ts` to
the packed tuple `tuple[int, str]`.

Type variables can also capture a recursive alias as their constraint target. This is more useful than expanding the
actual side and then failing merely because recursion exists.

The implementation remains narrow and fail-closed. It does not try to solve arbitrary recursive systems. It performs
bounded unrolling through aliases under an assumption set and otherwise keeps unsupported forms explicit.

## Substitution And Expansion

Substitution and expansion already had the core behavior needed for recursive variadic aliases. This pass added focused
tests so that behavior is now pinned.

For the hand-built core shape:

```text
Alias[*Ts] = tuple[*Ts, Alias[*Ts]]
```

expanding or substituting `Ts -> tuple[int, str]` now has explicit coverage for both:

- alias arguments: `Alias[tuple[Unpack[Ts]]] -> Alias[tuple[int, str]]`;
- alias targets: `tuple[*Ts, Alias[*Ts]] -> tuple[int, str, Alias[int, str]]`.

The alias target itself is not mutated by these operations. The translator returns rewritten type trees while leaving
the alias definition as the generic source of truth.

## Runtime Annotation Emission

Runtime annotation emission already preserves recursive aliases even when the requested alias policy is `expand`. This
is deliberate: fully expanding a recursive alias into a runtime annotation is not representable as a finite `typing`
object.

This pass added tests for the variadic recursive case. For `TupleNode[int, str]`, both default emission and preserve
mode emit the runtime alias form rather than trying to produce an infinite tuple annotation.

The emitter also has stricter fail-closed coverage for malformed preserved variadic alias args. If a `TypeAliasType`
whose alias parameter is a `TypeVarTuple` is carrying something other than a packed `TupleType`, annotation emission
raises `ReflectionError` instead of guessing how to spread it.

## Cache Surfaces

Recursive structural keys are intended to become marshal-cache-grade keys. This pass added hot-path cache coverage for
recursive variadic aliases:

- repeated reflection of a module-global-style alias form reuses the reflected `Type`;
- `structural_type_key` and `structural_type_key_or_none` reuse the same key object;
- `alpha_structural_type_key` and `alpha_structural_type_key_or_none` reuse the same key object;
- runtime annotation emission caches recursive variadic alias annotations under both default and preserve policies.

These tests do not finalize the thread-safety model. They pin the single-threaded cache behavior that current marshal
entrypoints need, while leaving the larger free-threaded cache design for later.

## Current Position

The system now has coherent recursive variadic alias behavior across:

- runtime reflection;
- core hand-built IR;
- structural and alpha-structural type keys;
- structural equivalence;
- structural join and meet;
- constraint inference and solve;
- substitution and expansion;
- runtime annotation emission;
- key and annotation caches.

This is still not a full mypy-strength recursive type engine. The important difference is that the supported subset is
now broad enough to carry real runtime use cases without relying on the old reflection system's sentinel override hack
for every recursive shape.

## Next Near-Term Work

The immediate near-term list from the previous checkpoint is effectively closed.

Small follow-ups that remain reasonable before moving fully to mid-term work:

- add a few negative tests for recursive aliases whose unrolling shapes genuinely disagree, if a future change touches
  constraints again;
- keep fail-closed tests close to any new recursive/variadic operation support;
- avoid broad API facade work until this machinery is exercised by an adapter or spike.

## Mid-Term Direction

The next larger phase should move toward proving this can replace old `_reflect` usage in realistic flows:

- build a thin compatibility spike for old dataclass and marshal reflection queries;
- use structural keys for marshal-cache experiments, especially recursive aliases and alpha-equivalent variables;
- continue filling algorithm gaps in constraints, solve, subtype, meet, join, and callable handling where real adapter
  work exposes them;
- revisit cache and thread-safety design with the current hot-path cache behavior as the baseline;
- decide which broader variadic tuple lattice cases deserve implementation and which should stay fail-closed.
