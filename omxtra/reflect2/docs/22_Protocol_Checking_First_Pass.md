# Protocol Checking First Pass

This checkpoint covers the runtime protocol checking work added after member and protocol inspection.

## Member Signature Improvements

Member inspection now reflects annotations into the internal type IR and also applies generic substitutions in the
inspected class context.

Examples now covered include:

- `Box[int].get(self) -> T` producing a public call return type of `int`;
- `Box[int].put(self, value: T) -> None` producing a public call parameter type of `int`;
- inherited generic methods from `Box[T]` on subclasses such as `StrBox(Box[str])`.

The stored raw signature remains unbound. Public call helpers still provide descriptor-aware views by dropping `self` or
`cls` where appropriate.

## Protocol Members

Protocol inspection now collects:

- methods and properties through the member inspection machinery;
- annotation-only data members;
- inherited protocol members;
- generic protocol substitutions;
- protocol member keys.

Protocol member keys reuse the member key machinery:

- callable protocol members key by public call signature;
- data and property members key by value type;
- unkeyable members fail closed.

## First Protocol Check

`runtime.protocols` now includes a strict exact-key protocol predicate:

- `is_protocol_implemented_by(concrete, protocol, reflector=None)`.

The concrete side is assembled from:

- record fields for dataclasses and namedtuples;
- runtime members for methods, properties, and keyable class data members.

The protocol side is assembled from protocol member keys.

This first pass is exact matching only. A method returning `int` and a protocol requiring `object` do not yet match by
covariance. A parameter accepting `object` and a protocol requiring `int` does not yet match by contravariance. Mutable
field semantics are also not modeled yet.

## Diagnostics

There is also a diagnostic/permissive layer:

- `ProtocolImplementationIssue`;
- `check_protocol_implementation`;
- `is_protocol_implemented_by_or_false`.

Issues currently report:

- missing members;
- mismatched member keys;
- unkeyable members.

The strict predicate may still raise for unkeyable members. The diagnostic path reports those cases instead.

## Boundaries

This remains intentionally conservative. It does not yet implement:

- variance-aware protocol matching;
- overload matching;
- property setter/deleter semantics;
- mutable data-field variance rules;
- recursive protocols;
- `@runtime_checkable` behavior;
- full mypy-style structural subtype checking.

The next careful expansion should be small. Good candidates are:

- property return covariance;
- method return covariance;
- method parameter contravariance;
- explicit mutable data-field invariance.

Each of those should be added separately so the runtime semantics stay inspectable and fail-closed.

## Test State

The full package test suite currently passes with 509 tests.
