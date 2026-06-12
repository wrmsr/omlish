# Runtime Surface For Marshal

This checkpoint covers the runtime-facing work after the dataclass and marshal review.

## What Changed

The reflection layer now exposes higher-level runtime helpers for the concrete use cases found in the old dataclass and
marshal systems.

### Dataclasses

`runtime.dataclasses` now provides a dataclass inspection surface:

- ordered dataclass instance fields;
- field owner tracking;
- raw reflected field types;
- generic-replaced field types;
- runtime annotations emitted from replaced types;
- structural type keys for replaced field types.

This directly targets the old `generic_replaced_field_type` and `generic_replaced_field_annotations` behavior used by
generated initializers and marshal field handling.

### Runtime Annotation Emission

`runtime.annotations.to_runtime_annotation` converts the currently supported IR subset back into runtime annotation
objects. It supports common marshal/init forms such as:

- instances and parameterized generic instances;
- unions;
- literals;
- tuples;
- `type[T]`;
- callables;
- `Any` and `None`;
- simple wrappers such as `Required`, `NotRequired`, and `ReadOnly`.

Unsupported forms raise rather than guessing.

### Runtime Queries

`runtime.queries` provides marshal-shaped helpers over the IR:

- runtime class recovery;
- optional union extraction;
- literal value type extraction;
- literal union destructuring;
- primitive union destructuring;
- base argument queries for collection-like dispatch;
- single-argument and mapping-argument helpers for iterable and mapping factories.

These helpers are intended to keep downstream code from open-coding `Instance`, `UnionType`, `LiteralType`, and MRO/base
mapping details.

### NamedTuples

`runtime.namedtuples` now mirrors the dataclass inspection style for `typing.NamedTuple` classes, including generic
specialization. It exposes ordered fields, replaced field types, runtime annotations, and field type keys.

The runtime reflector also filters the `typing.NamedTuple` pseudo-base from `__orig_bases__`, allowing generic
`NamedTuple` classes to reflect cleanly.

### Type Keys

`typekeys` provides explicit opt-in structural keys:

- `type_key`;
- `type_key_or_none`;
- runtime wrappers in `runtime.ops`.

The goal is not to replace identity caching. The universe and reflector still provide identity reuse where possible.
Type keys exist for consumers such as marshal caches that need equivalent freshly-created IR nodes to map to the same
cache entry.

The key surface is deliberately fail-closed for unsupported or recursive forms.

### Records

`runtime.records` normalizes dataclass and namedtuple instance data fields into one small field surface. This is scoped
to data fields only. A field annotated as callable is still a data field; descriptor-backed methods and protocol members
remain future work and should use a separate member/method inspection path.

## Current Runtime Value

The system can now support much of the old reflection system's practical runtime workload:

- reflect runtime type forms into mypy-like IR;
- recover generic base arguments across MRO layers;
- inspect dataclass and namedtuple data fields with generic substitution;
- emit runtime annotations for common generated-signature and marshal-recursion cases;
- extract literal values for validation;
- query optionals, literal unions, primitive unions, and collection base args;
- produce explicit structural cache keys for supported type shapes.

## Boundaries

The runtime record surface intentionally does not model methods, descriptors, properties, protocol members, or callable
attribute binding. Those should be handled by a later member-inspection layer that can explicitly distinguish:

- instance data fields containing callable values;
- functions on classes that bind through `__get__`;
- staticmethods and classmethods;
- properties and other descriptors;
- protocol-declared members and signatures.

The current APIs continue the fail-closed approach. If a type cannot be reflected, substituted, keyed, or converted back
to a runtime annotation accurately, it should raise or return `None` from the permissive helper.

## Test State

Runtime surface tests now cover the intended entrypoint modules together:

- annotations;
- dataclasses;
- namedtuples;
- queries;
- records;
- type keys;
- runtime ops.

The full package test suite currently passes with 463 tests.
